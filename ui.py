# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

import os
import shutil
import traceback

try:
    from qt.core import QApplication, QMenu, QObject, QThread, pyqtSignal
except ImportError:
    from PyQt5.Qt import QApplication, QMenu
    from PyQt5.QtCore import QObject, QThread, pyqtSignal

from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog, info_dialog, question_dialog
from calibre.ebooks.oeb.polish.container import get_container
from calibre_plugins.chinese_text_conversion import PLUGIN_NAME
from calibre_plugins.chinese_text_conversion.icons import apply_action_icon
from calibre_plugins.chinese_text_conversion.i18n import _, ngettext, apply_ui_language_from_prefs
from calibre_plugins.chinese_text_conversion.library_flow import (
    make_conversion_suffix, make_converted_title_suffix,
    collect_generated_book_time_codes,
    format_book_tag_log_lines,
    import_converted_book_as_new, log_section,
    text_preview_from_changes, ocr_preview_from_samples, convert_book_to_temp_copy,
    format_replacement_stats_log, format_conversion_diagnostics_log,
    format_jieba_samples_log, ocr_summary_line,
    languages_from_metadata, books_with_unsupported_language_items,
    count_image_resources_from_path,
    OCR_LARGE_IMAGE_COUNT_THRESHOLD, unsupported_language_skip_set_or_cancel,
)
from calibre_plugins.chinese_text_conversion.main import (
    PUNC_OMITS, _h2v_master_dict, getPrefs, prepare_prefs, build_criteria,
    get_configuration, get_language_code, get_resource_file, ENABLE_VISION_OCR,
    INCLUDE_METADATA, INPUT_LOCALE, USE_JIEBA_SEGMENTATION,
    CONVERSION_TYPE, OUTPUT_LOCALE, BILINGUAL_ANNOTATION,
    APPEND_CONVERSION_SUFFIX,
    HTML_TextProcessor, OpenCC, apply_converter_segmentation,
    apply_converter_force_pivot, criteria_with_ocr_enabled,
    estimate_library_book_progress_units,
)
from calibre_plugins.chinese_text_conversion.ocr_compat import (
    get_missing_ocr_language_notice, format_ocr_language_notice_message,
)


SUPPORTED_LIBRARY_FORMATS = ('EPUB', 'AZW3')


class LibraryConversionWorker(QObject):
    progress = pyqtSignal(int, int, str)
    book_done = pyqtSignal(object)
    book_failed = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, work, criteria, conversion):
        super().__init__()
        self.work = list(work)
        self.criteria = criteria
        self.conversion = conversion

    def run(self):
        total = len(self.work)
        converter = OpenCC(get_resource_file)
        converter.set_conversion(self.conversion)
        apply_converter_segmentation(converter, self.criteria, verbose=True)
        apply_converter_force_pivot(converter, self.criteria, verbose=True)
        parser = HTML_TextProcessor(converter)
        lang = get_language_code(self.criteria)
        if lang != 'None':
            parser.setLanguageAttribute('lang=\"' + lang + '\"')
        else:
            parser.setLanguageAttribute(None)

        ocr_enabled = bool(self.criteria[ENABLE_VISION_OCR])
        book_estimates = [
            estimate_library_book_progress_units(
                item.get('image_count', 0), ocr_enabled)
            for item in self.work
        ]
        done_before = 0

        for index, item in enumerate(self.work):
            book_id = item['book_id']
            title = item['title']
            fmt = item['fmt']
            path = item['path']
            suffix, generated_at = make_conversion_suffix()
            processing_message = _('Current book progress label').format(
                index + 1, total, title)
            remaining_est = sum(book_estimates[index + 1:])
            book_units = [book_estimates[index]]

            def on_progress(local_done, local_total, detail):
                book_units[0] = max(int(local_total or 0), 1)
                global_current = done_before + max(0, int(local_done or 0))
                global_total = done_before + book_units[0] + remaining_est
                message = processing_message
                if detail:
                    message = '{} — {}'.format(processing_message, detail)
                self.progress.emit(global_current, max(global_total, 1), message)

            self.progress.emit(
                done_before, done_before + book_units[0] + remaining_est,
                processing_message)
            tmpdir = None
            try:
                tmpdir, temp_path, changed_files, ocr_samples, ocr_stats = (
                    convert_book_to_temp_copy(
                        path, fmt, self.criteria, converter, parser,
                        progress_callback=on_progress))
                done_before += book_units[0]
                self.progress.emit(
                    done_before, done_before + remaining_est, processing_message)
                replacement_log = format_replacement_stats_log(converter)
                diagnostic_log = format_conversion_diagnostics_log(converter)
                jieba_log = None
                if (
                    self.criteria is not None
                    and len(self.criteria) > USE_JIEBA_SEGMENTATION
                    and bool(self.criteria[USE_JIEBA_SEGMENTATION])
                ):
                    jieba_log = format_jieba_samples_log(converter)
                self.book_done.emit({
                    'book_id': book_id,
                    'title': title,
                    'fmt': fmt,
                    'tmpdir': tmpdir,
                    'temp_path': temp_path,
                    'changed_files': changed_files,
                    'ocr_samples': ocr_samples,
                    'ocr_stats': ocr_stats,
                    'replacement_log': replacement_log,
                    'diagnostic_log': diagnostic_log,
                    'jieba_log': jieba_log,
                    'suffix': suffix,
                    'generated_at': generated_at,
                })
            except Exception:
                if tmpdir:
                    shutil.rmtree(tmpdir, ignore_errors=True)
                # Keep overall bar moving past a failed book using its estimate.
                done_before += book_units[0]
                self.book_failed.emit({
                    'title': title,
                    'traceback': traceback.format_exc(),
                })

        self.finished.emit()


class ChineseTextAction(InterfaceAction):
    '''
    Main library action: convert selected book(s) from the calibre library.
    Add to "The main toolbar" via Preferences → Toolbars & menus.
    '''

    name = PLUGIN_NAME
    # Icon path in action_spec is for Calibre built-in icons only; set plugin icon in genesis().
    action_spec = (
        _('Chinese Conversion'),
        None,
        _('Convert traditional/simplified Chinese in selected books'),
        ('Ctrl+Shift+Alt+C',),
    )
    action_shortcut_name = _('Chinese Conversion')
    action_type = 'current'

    _library_conversion_thread = None
    _library_conversion_worker = None
    _library_conversion_status_dialog = None
    _zhconvert_dialog = None

    def genesis(self):
        prefs = getPrefs()
        prepare_prefs(prefs)
        apply_ui_language_from_prefs(prefs)
        apply_action_icon(self.qaction, PLUGIN_NAME)
        apply_action_icon(self.menuless_qaction, PLUGIN_NAME)
        self.qaction.triggered.connect(self.convert_selected_books)
        self.menuless_qaction.triggered.connect(self.convert_selected_books)
        self._action_menu = QMenu(self.gui)
        self._convert_menu_action = self._action_menu.addAction('')
        self._convert_menu_action.triggered.connect(self.convert_selected_books)
        self._zhconvert_menu_action = self._action_menu.addAction('')
        self._zhconvert_menu_action.triggered.connect(self.open_zhconvert_dialog)
        self.qaction.setMenu(self._action_menu)
        self._update_action_translations()

    def _update_action_translations(self):
        if getattr(self, '_convert_menu_action', None) is not None:
            self._convert_menu_action.setText(_('Convert selected books'))
        if getattr(self, '_zhconvert_menu_action', None) is not None:
            self._zhconvert_menu_action.setText(
                _('ZhConvert online short-text conversion'))

    def open_zhconvert_dialog(self):
        prefs = getPrefs()
        prepare_prefs(prefs)
        apply_ui_language_from_prefs(prefs)
        self._update_action_translations()
        from calibre_plugins.chinese_text_conversion.dialogs import ZhConvertDialog
        dlg = ZhConvertDialog(self.gui, prefs)
        self._zhconvert_dialog = dlg
        try:
            dlg.exec_()
        finally:
            self._zhconvert_dialog = None

    def location_selected(self, loc):
        enabled = loc == 'library'
        self.qaction.setEnabled(enabled)
        self.menuless_qaction.setEnabled(enabled)

    def convert_selected_books(self):
        db = self.gui.current_db
        if db is None:
            return error_dialog(
                self.gui, _('No library open'),
                _('Open a calibre library first.'), show=True)

        book_ids = self._selected_book_ids()
        if not book_ids:
            return error_dialog(
                self.gui, _('No books selected'),
                _('Select one or more books in the library, then run Chinese Conversion.'),
                show=True)

        prefs = getPrefs()
        prepare_prefs(prefs)
        apply_ui_language_from_prefs(prefs)
        self._update_action_translations()

        from calibre_plugins.chinese_text_conversion.dialogs import ConversionDialog
        scan_path = None
        for book_id in book_ids:
            path, _fmt = self._book_format_path(db, book_id)
            if path:
                scan_path = path
                break
        dlg = ConversionDialog(
            self.gui, prefs, _h2v_master_dict, PUNC_OMITS,
            force_entire_book=True, book_font_scan_path=scan_path)
        dlg.apply_translations()
        if not dlg.exec_():
            return

        apply_ui_language_from_prefs(prefs)

        flagged = books_with_unsupported_language_items(
            (book_id, db.title(book_id, index_is_id=True),
             languages_from_metadata(db.get_metadata(book_id, index_is_id=True)))
            for book_id in book_ids)
        skip_book_ids = unsupported_language_skip_set_or_cancel(self.gui, flagged)
        if skip_book_ids is None:
            return

        criteria = build_criteria(prefs)
        if criteria[ENABLE_VISION_OCR]:
            notice = get_missing_ocr_language_notice(criteria[INPUT_LOCALE])
            if notice:
                proceed = question_dialog(
                    self.gui,
                    _('Vision OCR language notice'),
                    _('Vision OCR language notice summary'),
                    det_msg=format_ocr_language_notice_message(notice),
                    default_yes=False,
                    yes_text=_('Continue'),
                    no_text=_('Cancel'),
                )
                if not proceed:
                    return
        if criteria[1] == 0 and criteria[5] == 0 and criteria[6] == 0:
            return info_dialog(
                self.gui, _('No Changes'),
                _('No conversion options were selected.'), show=True)

        conversion = get_configuration(criteria)
        if conversion == 'unsupported_conversion':
            return info_dialog(
                self.gui, _('No Changes'),
                _('The output configuration selected is not supported.\n Please use a different Input/Output Language Styles combination'),
                show=True)

        work = []
        skipped = []
        skipped_language = []
        for book_id in book_ids:
            title = db.title(book_id, index_is_id=True)
            if book_id in skip_book_ids:
                skipped_language.append(title)
                continue
            path, fmt = self._book_format_path(db, book_id)
            if not path:
                skipped.append(title)
                continue
            work.append({
                'book_id': book_id,
                'title': title,
                'path': path,
                'fmt': fmt,
                'image_count': 0,
            })

        if not work:
            if skipped_language:
                return info_dialog(
                    self.gui, _('Cannot Process'),
                    _('All selected books were skipped by language check.'),
                    show=True)
            return error_dialog(
                self.gui, _('Cannot Process'),
                _('None of the selected books have an EPUB or AZW3 format.'),
                show=True)

        if self._library_conversion_thread is not None:
            return info_dialog(
                self.gui, _('Cannot Process'),
                _('Library conversion is already running.'), show=True)

        total_images = 0
        if criteria[ENABLE_VISION_OCR]:
            for item in work:
                try:
                    item['image_count'] = count_image_resources_from_path(item['path'])
                except Exception:
                    item['image_count'] = 0
                total_images += int(item['image_count'] or 0)
            if total_images >= OCR_LARGE_IMAGE_COUNT_THRESHOLD:
                proceed = question_dialog(
                    self.gui,
                    _('Vision OCR large job notice'),
                    _('Vision OCR large job summary').format(total_images),
                    det_msg=_('Vision OCR large job details'),
                    default_yes=False,
                    yes_text=_('Run OCR'),
                    no_text=_('Skip OCR'),
                )
                if not proceed:
                    criteria = criteria_with_ocr_enabled(criteria, False)
                    total_images = 0

        from calibre_plugins.chinese_text_conversion.dialogs import LibraryConversionStatusDialog
        status_dlg = LibraryConversionStatusDialog(
            self.gui, ocr_enabled=bool(criteria[ENABLE_VISION_OCR]))
        status_dlg.apply_translations()
        status_dlg.log_processing(
            _('New books will be added to the library; original files are not modified.'))
        if skipped:
            status_dlg.log_processing(
                _('Skipped (no EPUB/AZW3):') + ' ' + ', '.join(skipped))
        if skipped_language:
            status_dlg.log_processing(
                _('Skipped (language not Chinese/Japanese):') + ' ' + ', '.join(skipped_language))
        status_dlg.show()
        QApplication.processEvents()

        state = {
            'db': db,
            'criteria': criteria,
            'conversion': conversion,
            'used_book_time_codes': (
                collect_generated_book_time_codes(db)
                if criteria[APPEND_CONVERSION_SUFFIX] else set()
            ),
            'ocr_total_images': total_images if criteria[ENABLE_VISION_OCR] else 0,
            'created': [],
            'unchanged': [],
            'failed': [],
            'new_book_ids': [],
            'images_recognized': 0,
            'text_results': 0,
            'sample_results': [],
            'recognized_images': [],
            'recognized_no_change': 0,
            'reason': '',
            'jieba_sample_lines': [],
        }
        self._start_library_conversion_worker(work, criteria, conversion, status_dlg, state)

    def _start_library_conversion_worker(self, work, criteria, conversion, status_dlg, state):
        thread = QThread()
        worker = LibraryConversionWorker(work, criteria, conversion)
        worker.moveToThread(thread)

        self._library_conversion_thread = thread
        self._library_conversion_worker = worker
        self._library_conversion_status_dialog = status_dlg

        thread.started.connect(worker.run)
        worker.progress.connect(status_dlg.set_progress)
        last_progress_book = ['']

        def log_current_book_once(_index, _total, message):
            # Log once per book; stage detail stays on the status label only.
            book_key = (message or '').split(' — ', 1)[0]
            if book_key == last_progress_book[0]:
                return
            last_progress_book[0] = book_key
            status_dlg.log_processing(book_key)

        worker.progress.connect(log_current_book_once)
        worker.book_done.connect(
            lambda result: self._handle_library_book_done(result, status_dlg, state))
        worker.book_failed.connect(
            lambda failure: self._handle_library_book_failed(failure, status_dlg, state))
        worker.finished.connect(thread.quit)
        worker.finished.connect(
            lambda: self._finish_library_conversion(status_dlg, state))
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._clear_library_worker_refs)

        progress_total = sum(
            estimate_library_book_progress_units(
                item.get('image_count', 0), bool(criteria[ENABLE_VISION_OCR]))
            for item in work) or len(work)
        status_dlg.set_progress(0, progress_total, _('Preparing background conversion…'))
        thread.start()

    def _handle_library_book_done(self, result, status_dlg, state):
        db = state['db']
        criteria = state['criteria']
        title = result['title']
        fmt = result['fmt']
        tmpdir = result.get('tmpdir')
        try:
            changed_files = result.get('changed_files') or []
            ocr_stats = result.get('ocr_stats') or {}
            self._merge_ocr_summary(state, ocr_stats)

            ocr_no_delta = bool(
                criteria[ENABLE_VISION_OCR]
                and int(ocr_stats.get('recognized_no_change', 0) or 0) > 0
            )
            if not changed_files and not ocr_no_delta:
                state['unchanged'].append(title)
                status_dlg.log_processing(
                    _('No changes for “{}”; no new book created.').format(title))
                return
            if not changed_files and ocr_no_delta:
                status_dlg.log_processing(
                    _('OCR executed with no content delta; creating a new copy for review.'))

            temp_path = result['temp_path']
            container = get_container(temp_path)
            excerpt = text_preview_from_changes(container, changed_files)
            if criteria[ENABLE_VISION_OCR]:
                excerpt = excerpt + '\n\n' + ocr_preview_from_samples(
                    result.get('ocr_samples'),
                    ocr_enabled=True,
                )
            meta_converter = None
            if criteria[INCLUDE_METADATA]:
                meta_converter = state.get('meta_converter')
                if meta_converter is None:
                    conversion = state.get('conversion')
                    if conversion and conversion != 'no_conversion':
                        meta_converter = OpenCC(get_resource_file)
                        meta_converter.set_conversion(conversion)
                        apply_converter_segmentation(meta_converter, criteria)
                        apply_converter_force_pivot(meta_converter, criteria)
                        state['meta_converter'] = meta_converter
            title_suffix = make_converted_title_suffix(
                criteria[CONVERSION_TYPE],
                criteria[OUTPUT_LOCALE],
                bilingual=criteria[BILINGUAL_ANNOTATION],
                enabled=criteria[APPEND_CONVERSION_SUFFIX],
                used_time_codes=state['used_book_time_codes'],
            )
            new_id, new_title = import_converted_book_as_new(
                db, result['book_id'], temp_path, fmt, result['suffix'],
                converter=meta_converter, title_suffix=title_suffix)
            state['new_book_ids'].append(new_id)
            state['created'].append(new_title)
            saved_path = db.format_abspath(new_id, fmt, index_is_id=True)
            book_info = _('Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}').format(
                title, new_title, new_id, fmt)
            book_info = book_info + '\n' + format_book_tag_log_lines(
                result['suffix'], result['generated_at'])
            if saved_path:
                book_info = book_info + '\n' + _('Saved file log line').format(
                    os.path.basename(saved_path), saved_path)
            log_section(
                status_dlg,
                _('----Log book info begin----'),
                _('----Log book info end----'),
                [book_info])
            status_dlg.log_result('')
            log_section(
                status_dlg,
                _('----Log replacements begin----'),
                _('----Log replacements end----'),
                [result.get('replacement_log')])
            status_dlg.log_result('')
            diagnostic_log = result.get('diagnostic_log')
            if diagnostic_log:
                log_section(
                    status_dlg,
                    _('----Log conversion diagnostics begin----'),
                    _('----Log conversion diagnostics end----'),
                    [diagnostic_log])
                status_dlg.log_result('')
            log_section(
                status_dlg,
                _('----Log preview begin----'),
                _('----Log preview end----'),
                [excerpt])
            status_dlg.log_result('')
            # Jieba runs before OpenCC conversion; show samples after conversion
            # results so the log reads: convert first, then how Jieba split it.
            jieba_log = result.get('jieba_log')
            if jieba_log:
                log_section(
                    status_dlg,
                    _('----Log Jieba samples begin----'),
                    _('----Log Jieba samples end----'),
                    [jieba_log])
                status_dlg.log_result('')
                for line in str(jieba_log).splitlines():
                    text = line.strip()
                    if ' → ' not in text:
                        continue
                    sample_line = '  ' + text
                    if (
                        sample_line not in state['jieba_sample_lines']
                        and len(state['jieba_sample_lines']) < 8
                    ):
                        state['jieba_sample_lines'].append(sample_line)
        except Exception:
            state['failed'].append((title, traceback.format_exc()))
            status_dlg.log_processing(_('Failed: {}').format(title))
        finally:
            if tmpdir:
                shutil.rmtree(tmpdir, ignore_errors=True)

    def _handle_library_book_failed(self, failure, status_dlg, state):
        title = failure.get('title', _('Unknown'))
        state['failed'].append((title, failure.get('traceback', '')))
        status_dlg.log_processing(_('Failed: {}').format(title))

    def _merge_ocr_summary(self, state, ocr_stats):
        state['images_recognized'] += int(ocr_stats.get('images_recognized', 0) or 0)
        state['text_results'] += int(ocr_stats.get('text_results', 0) or 0)
        state['recognized_no_change'] += int(ocr_stats.get('recognized_no_change', 0) or 0)
        stats_reason = ocr_stats.get('reason', '') or ''
        if stats_reason == 'ocr_no_delta':
            state['reason'] = 'ocr_no_delta'
        elif stats_reason == 'no_image_resources' and not state['reason']:
            state['reason'] = 'no_image_resources'
        for sample in ocr_stats.get('sample_results', []):
            if len(state['sample_results']) >= 3:
                break
            sample_text = str(sample).strip()
            if sample_text:
                state['sample_results'].append(sample_text)
        for image_name in ocr_stats.get('recognized_images', []):
            if len(state['recognized_images']) >= 3:
                break
            name_text = str(image_name).strip()
            if name_text and name_text not in state['recognized_images']:
                state['recognized_images'].append(name_text)

    def _finish_library_conversion(self, status_dlg, state):
        self._refresh_library_new_books(state['new_book_ids'])
        completed_images = state.get('images_recognized') if state['criteria'][ENABLE_VISION_OCR] else None
        status_dlg.set_complete(completed_images=completed_images)
        summary = []
        created = state['created']
        unchanged = state['unchanged']
        failed = state['failed']
        if created:
            summary.append(ngettext(
                'Created 1 new book in the library:',
                'Created {} new books in the library:',
                len(created)).format(len(created)))
            summary.extend('• ' + title for title in created)
        if unchanged:
            summary.append(_('No changes (originals kept):') + ' ' + ', '.join(unchanged))
        if failed:
            summary.append(_('Failed:') + ' ' + ', '.join(title for title, _tb in failed))
        ocr_line = ocr_summary_line(
            {
                'images_recognized': state['images_recognized'],
                'text_results': state['text_results'],
                'sample_results': state['sample_results'],
                'recognized_images': state['recognized_images'],
                'recognized_no_change': state['recognized_no_change'],
                'reason': state['reason'],
            },
            ocr_enabled=bool(state['criteria'][ENABLE_VISION_OCR]),
        )
        if ocr_line:
            summary.append(ocr_line)
        criteria = state['criteria']
        use_jieba = (
            criteria is not None
            and len(criteria) > USE_JIEBA_SEGMENTATION
            and bool(criteria[USE_JIEBA_SEGMENTATION])
        )
        summary.append(
            _('Segmentation: Jieba') if use_jieba else _('Segmentation: OpenCC mmseg')
        )
        if use_jieba and state.get('jieba_sample_lines'):
            summary.append(_('Jieba segmentation samples:'))
            summary.extend(state['jieba_sample_lines'][:8])
        if summary:
            log_section(
                status_dlg,
                _('----Log summary begin----'),
                _('----Log summary end----'),
                ['\n'.join(summary)])
            status_dlg.log_result('')
        if state['new_book_ids']:
            if len(state['new_book_ids']) == 1:
                status_dlg.log_result(_(
                    'Conversion succeeded. The new book is already in your library. Open the library and check the most recently added book (sort by Date).'))
            else:
                status_dlg.log_result(_(
                    'Conversion succeeded. {} new books are already in your library. Open the library and check the most recently added entries (sort by Date).'
                ).format(len(state['new_book_ids'])))
        if not status_dlg.isVisible():
            status_dlg.show()
            status_dlg.raise_()
            status_dlg.activateWindow()
        if failed and not created:
            det = '\n\n'.join('=== {} ===\n{}'.format(title, tb) for title, tb in failed)
            error_dialog(
                self.gui, _('Failed'),
                _('Failed to convert one or more books, click "Show details" for more info'),
                det_msg=det, show=True)

    def _clear_library_worker_refs(self):
        self._library_conversion_thread = None
        self._library_conversion_worker = None

    def _refresh_library_new_books(self, new_book_ids):
        '''Refresh the library view before the status dialog closes.'''
        if not new_book_ids:
            return
        model = self.gui.library_view.model()
        # db.import_book(notify=False) updates db.data but not the Qt model.
        # Insert GUI rows first, then fill metadata (kiwidude / Kovid pattern).
        model.books_added(len(new_book_ids))
        model.refresh_ids(list(new_book_ids))
        try:
            if getattr(self.gui, 'db_images', None) is not None:
                self.gui.db_images.reset()
        except Exception:
            pass
        try:
            self.gui.tags_view.recount()
        except Exception:
            pass
        QApplication.processEvents()

    def _selected_book_ids(self):
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows:
            return []
        model = self.gui.library_view.model()
        return [model.id(r.row()) for r in rows]

    @staticmethod
    def _book_format_path(db, book_id):
        fmts = (db.formats(book_id, index_is_id=True) or '').split(',')
        for fmt in SUPPORTED_LIBRARY_FORMATS:
            if fmt in fmts:
                # book_id is a library id from library_view.model().id(), not a row index
                return db.format_abspath(book_id, fmt, index_is_id=True), fmt
        return None, None
