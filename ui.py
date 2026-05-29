# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

import shutil
import traceback

try:
    from qt.core import QApplication, QCursor, Qt
except ImportError:
    from PyQt5.Qt import QApplication, QCursor, Qt

from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import error_dialog, info_dialog
from calibre.ebooks.oeb.polish.container import get_container
from calibre_plugins.chinese_text_conversion import PLUGIN_NAME
from calibre_plugins.chinese_text_conversion.icons import apply_action_icon
from calibre_plugins.chinese_text_conversion.i18n import _, ngettext, apply_ui_language_from_prefs
from calibre_plugins.chinese_text_conversion.library_flow import (
    make_conversion_suffix, import_converted_book_as_new,
    text_preview_from_changes, convert_book_to_temp_copy,
    languages_from_metadata, books_with_non_chinese_language,
    confirm_chinese_books_or_cancel,
)
from calibre_plugins.chinese_text_conversion.main import (
    PUNC_OMITS, _h2v_master_dict, getPrefs, prepare_prefs, build_criteria,
    get_configuration, get_language_code, get_resource_file,
    HTML_TextProcessor, OpenCC,
)


SUPPORTED_LIBRARY_FORMATS = ('EPUB', 'AZW3')


class ChineseTextAction(InterfaceAction):
    '''
    Main library action: convert selected book(s) from the calibre library.
    Add to "The main toolbar" via Preferences → Toolbars & menus.
    '''

    name = 'Chinese Text Conversion'
    # Icon path in action_spec is for Calibre built-in icons only; set plugin icon in genesis().
    action_spec = (
        _('Chinese Conversion'),
        None,
        _('Convert traditional/simplified Chinese in selected books'),
        ('Ctrl+Shift+Alt+C',),
    )
    action_shortcut_name = _('Chinese Text Conversion')
    action_type = 'current'

    def genesis(self):
        apply_action_icon(self.qaction, PLUGIN_NAME)
        apply_action_icon(self.menuless_qaction, PLUGIN_NAME)
        self.qaction.triggered.connect(self.convert_selected_books)
        self.menuless_qaction.triggered.connect(self.convert_selected_books)

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

        from calibre_plugins.chinese_text_conversion.dialogs import ConversionDialog
        dlg = ConversionDialog(
            self.gui, prefs, _h2v_master_dict, PUNC_OMITS, force_entire_book=True)
        dlg.apply_translations()
        if not dlg.exec_():
            return

        apply_ui_language_from_prefs(prefs)

        flagged = books_with_non_chinese_language(
            (db.title(book_id, index_is_id=True),
             languages_from_metadata(db.get_metadata(book_id, index_is_id=True)))
            for book_id in book_ids)
        if not confirm_chinese_books_or_cancel(self.gui, flagged):
            return

        criteria = build_criteria(prefs)
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

        converter = OpenCC(get_resource_file)
        parser = HTML_TextProcessor(converter)
        lang = get_language_code(criteria)
        if lang != 'None':
            parser.setLanguageAttribute('lang=\"' + lang + '\"')
        else:
            parser.setLanguageAttribute(None)
        converter.set_conversion(conversion)

        work = []
        skipped = []
        for book_id in book_ids:
            path, fmt = self._book_format_path(db, book_id)
            if not path:
                skipped.append(db.title(book_id, index_is_id=True))
                continue
            work.append((book_id, path, fmt))

        if not work:
            return error_dialog(
                self.gui, _('Cannot Process'),
                _('None of the selected books have an EPUB or AZW3 format.'),
                show=True)

        from calibre_plugins.chinese_text_conversion.dialogs import LibraryConversionStatusDialog
        status_dlg = LibraryConversionStatusDialog(self.gui)
        status_dlg.apply_translations()
        status_dlg.log_processing(
            _('New books will be added to the library; original files are not modified.'))
        if skipped:
            status_dlg.log_processing(
                _('Skipped (no EPUB/AZW3):') + ' ' + ', '.join(skipped))
        status_dlg.show()
        QApplication.processEvents()

        created = []
        unchanged = []
        failed = []
        new_book_ids = []

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            total = len(work)
            for index, (book_id, path, fmt) in enumerate(work, start=1):
                title = db.title(book_id, index_is_id=True)
                suffix = make_conversion_suffix()
                status_dlg.log_processing(
                    _('Processing ({}/{}): {}').format(index, total, title))
                QApplication.processEvents()
                tmpdir = None
                try:
                    tmpdir, temp_path, changed_files = convert_book_to_temp_copy(
                        path, fmt, criteria, converter, parser)
                    if not changed_files:
                        unchanged.append(title)
                        status_dlg.log_processing(
                            _('No changes for “{}”; no new book created.').format(title))
                        continue

                    container = get_container(temp_path)
                    excerpt = text_preview_from_changes(container, changed_files)
                    new_id, new_title = import_converted_book_as_new(
                        db, book_id, temp_path, fmt, suffix)
                    new_book_ids.append(new_id)
                    created.append(new_title)
                    status_dlg.log_result(_('—— {} ——').format(_('Result preview')))
                    status_dlg.log_result(
                        _('Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}\nSuffix: {}').format(
                            title, new_title, new_id, fmt, suffix))
                    status_dlg.log_result(excerpt)
                except Exception:
                    failed.append((title, traceback.format_exc()))
                    status_dlg.log_processing(
                        _('Failed: {}').format(title))
                finally:
                    if tmpdir:
                        shutil.rmtree(tmpdir, ignore_errors=True)
        finally:
            QApplication.restoreOverrideCursor()
            self._refresh_library_new_books(new_book_ids)
            status_dlg.set_complete()
            summary = []
            if created:
                summary.append(ngettext(
                    'Created 1 new book in the library:',
                    'Created {} new books in the library:',
                    len(created)).format(len(created)))
                summary.extend('• ' + t for t in created)
            if unchanged:
                summary.append(_('No changes (originals kept):') + ' ' + ', '.join(unchanged))
            if failed:
                summary.append(_('Failed:') + ' ' + ', '.join(t for t, _ in failed))
            if summary:
                status_dlg.log_result('\n'.join(summary))
            if new_book_ids:
                status_dlg.log_result('')
                if len(new_book_ids) == 1:
                    status_dlg.log_result(_(
                        'Conversion succeeded. The new book is already in your library. Open the library and check the most recently added book (sort by Date).'))
                else:
                    status_dlg.log_result(_(
                        'Conversion succeeded. {} new books are already in your library. Open the library and check the most recently added entries (sort by Date).'
                    ).format(len(new_book_ids)))
            status_dlg.exec_()

        if failed and not created:
            det = '\n\n'.join('=== {} ===\n{}'.format(t, e) for t, e in failed)
            error_dialog(
                self.gui, _('Failed'),
                _('Failed to convert one or more books, click "Show details" for more info'),
                det_msg=det, show=True)

    def _refresh_library_new_books(self, new_book_ids):
        '''Refresh the library view before the status dialog closes.'''
        if not new_book_ids:
            return
        model = self.gui.library_view.model()
        # import_book() already calls db.data.books_added(); model.books_added(n)
        # only inserts empty placeholder rows at the top (Calibre BooksModel API).
        model.refresh_ids(new_book_ids)
        try:
            if getattr(self.gui, 'db_images', None) is not None:
                self.gui.db_images.reset()
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
