# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

import os
import re
import shutil
import tempfile
from datetime import datetime

from calibre_plugins.chinese_text_conversion.__init__ import PLUGIN_SAFE_NAME
from calibre_plugins.chinese_text_conversion.i18n import _


_NON_CHINESE_ZH_VARIANTS = ('zh-latn', 'zh-cyrl', 'zh-bopo', 'zh-mong')
_CHINESE_LANG_CODES = frozenset(('zh', 'chi', 'zho', 'cmn', 'yue'))
_JAPANESE_LANG_CODES = frozenset(('ja', 'jpn', 'jap'))


def _normalize_language_code(code):
    if code is None:
        return ''
    return str(code).strip().replace('_', '-').lower()


def is_chinese_language_code(code):
    '''
    Return True if the code denotes Chinese, False if explicitly not Chinese,
    or None when empty/undetermined.
    '''
    norm = _normalize_language_code(code)
    if not norm:
        return None
    for prefix in _NON_CHINESE_ZH_VARIANTS:
        if norm == prefix or norm.startswith(prefix + '-'):
            return False
    if norm in _CHINESE_LANG_CODES:
        return True
    if norm == 'zh' or norm.startswith('zh-'):
        return True
    return False


def is_japanese_language_code(code):
    norm = _normalize_language_code(code)
    if not norm:
        return None
    if norm in _JAPANESE_LANG_CODES:
        return True
    if norm == 'ja' or norm.startswith('ja-'):
        return True
    return False


def is_supported_cjk_language_code(code):
    chinese = is_chinese_language_code(code)
    if chinese is True:
        return True
    japanese = is_japanese_language_code(code)
    if japanese is True:
        return True
    if chinese is None and japanese is None:
        return None
    return False


def classify_book_languages(language_codes):
    '''
    Return 'supported', 'unsupported', or 'unknown' for a list of language codes.
    Unknown/empty metadata is treated as unknown (no warning).
    '''
    codes = [_normalize_language_code(code) for code in (language_codes or [])]
    codes = [code for code in codes if code]
    if not codes:
        return 'unknown'

    has_supported = False
    has_unsupported = False
    for code in codes:
        result = is_supported_cjk_language_code(code)
        if result is True:
            has_supported = True
        elif result is False:
            has_unsupported = True

    if has_supported:
        return 'supported'
    if has_unsupported:
        return 'unsupported'
    return 'unknown'


def languages_from_metadata(mi):
    langs = []
    if getattr(mi, 'languages', None):
        langs.extend(mi.languages)
    elif getattr(mi, 'language', None):
        langs.append(mi.language)
    return [lang for lang in langs if lang and str(lang).strip()]


def languages_from_container(container):
    langs = []
    try:
        langs.extend(languages_from_metadata(container.mi))
    except Exception:
        pass
    if langs:
        return langs
    try:
        for item in container.opf_xpath('//opf:metadata/dc:language'):
            if item.text and item.text.strip():
                langs.append(item.text.strip())
    except Exception:
        pass
    return langs


def books_with_non_chinese_language(book_items):
    '''
    book_items: iterable of (title, language_codes)
    Returns list of (title, language_display) for books not marked Chinese/Japanese.
    '''
    flagged = []
    for title, language_codes in book_items:
        if classify_book_languages(language_codes) != 'unsupported':
            continue
        display_langs = ', '.join(str(lang) for lang in language_codes if lang and str(lang).strip())
        if not display_langs:
            display_langs = _('Unknown')
        flagged.append((title, display_langs))
    return flagged


def books_with_unsupported_language_items(book_items):
    '''
    book_items: iterable of (key, title, language_codes).
    Returns list of (key, title, language_display) for books not marked Chinese/Japanese.
    '''
    flagged = []
    for key, title, language_codes in book_items:
        if classify_book_languages(language_codes) != 'unsupported':
            continue
        display_langs = ', '.join(str(lang) for lang in language_codes if lang and str(lang).strip())
        if not display_langs:
            display_langs = _('Unknown')
        flagged.append((key, title, display_langs))
    return flagged


def confirm_chinese_books_or_cancel(gui, flagged_books):
    '''
    Warn when metadata language is not Chinese/Japanese. Returns True to continue.
    '''
    if not flagged_books:
        return True

    from calibre.gui2 import question_dialog

    msg = _('Please confirm the current book language is Chinese or Japanese Kanji.')
    if len(flagged_books) == 1:
        title, langs = flagged_books[0]
        det_msg = _('Book: {}\nLanguage: {}\nYou can still continue if this book contains Chinese or Japanese Kanji text.').format(title, langs)
    else:
        lines = [
            _('The following {} book(s) are not marked as Chinese or Japanese:').format(
                len(flagged_books))]
        for title, langs in flagged_books[:20]:
            lines.append('• {} ({})'.format(title, langs))
        if len(flagged_books) > 20:
            lines.append('…')
        det_msg = '\n'.join(lines)

    return question_dialog(
        gui, _('Language check'), msg, det_msg=det_msg,
        default_yes=False,
        yes_text=_('Continue'), no_text=_('Cancel'))


def unsupported_language_skip_set_or_cancel(gui, flagged_books):
    '''
    For batch conversion, skip unsupported-language books when there are multiple.
    Returns a set of keys to skip, or None to cancel.
    '''
    if not flagged_books:
        return set()

    from calibre.gui2 import question_dialog

    if len(flagged_books) == 1:
        _key, title, langs = flagged_books[0]
        proceed = question_dialog(
            gui,
            _('Language check'),
            _('Please confirm the current book language is Chinese or Japanese Kanji.'),
            det_msg=_('Book: {}\nLanguage: {}\nYou can still continue if this book contains Chinese or Japanese Kanji text.').format(title, langs),
            default_yes=False,
            yes_text=_('Continue'),
            no_text=_('Cancel'))
        return set() if proceed else None

    lines = [
        _('The following {} book(s) are not marked as Chinese or Japanese and will be skipped:').format(
            len(flagged_books))]
    for _key, title, langs in flagged_books[:20]:
        lines.append('• {} ({})'.format(title, langs))
    if len(flagged_books) > 20:
        lines.append('…')
    proceed = question_dialog(
        gui,
        _('Language check'),
        _('Some selected books are not marked as Chinese or Japanese.'),
        det_msg='\n'.join(lines),
        default_yes=True,
        yes_text=_('Skip listed books'),
        no_text=_('Cancel'))
    if not proceed:
        return None
    return set(key for key, _title, _langs in flagged_books)


LIBRARY_PREVIEW_MAX_CHARS = 500
LIBRARY_REPLACEMENT_SAMPLE_LIMIT = 20
OCR_LARGE_IMAGE_COUNT_THRESHOLD = 5


def count_image_resources(container):
    '''Count image resources in an already-open Calibre container.'''
    return sum(
        1 for _name, mime in container.mime_map.items()
        if (mime or '').startswith('image/')
    )


def count_image_resources_from_path(book_path):
    '''Open an EPUB/AZW3 container only long enough to count image resources.'''
    from calibre.ebooks.oeb.polish.container import get_container
    container = get_container(book_path)
    return count_image_resources(container)


def format_replacement_stats_log(converter, max_samples=LIBRARY_REPLACEMENT_SAMPLE_LIMIT):
    counts = converter.get_replacement_counts()
    if not counts:
        return _('No OpenCC replacements recorded for this book.')
    total = sum(counts.values())
    unique = len(counts)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
    lines = [
        _('OpenCC replacements: {} hits, {} unique pairs').format(total, unique),
    ]
    for (old, new), n in ranked[:max_samples]:
        lines.append('  {} → {} (×{})'.format(old, new, n))
    remaining = unique - min(unique, max_samples)
    if remaining > 0:
        lines.append(_('… and {} more unique pairs not shown').format(remaining))
    return '\n'.join(lines)


def make_conversion_suffix():
    '''
    Plugin name + local time (HH-MM-SS), safe for titles and filenames.
    Returns (suffix_tag, generated_at) so logs can show the same instant.
    '''
    generated_at = datetime.now()
    stamp = generated_at.strftime('%H-%M-%S')
    suffix_tag = '{}-{}'.format(PLUGIN_SAFE_NAME, stamp)
    return suffix_tag, generated_at


def format_book_tag_log_lines(suffix_tag, generated_at):
    '''Human-readable lines explaining the new-book title suffix (log only).'''
    time_stamp = generated_at.strftime('%Y-%m-%d %H:%M:%S')
    return '\n'.join([
        _('Log book title suffix: {}').format(suffix_tag),
        _('Log generated at (local time): {}').format(time_stamp),
        _('Log suffix time hint'),
    ])


def log_section(status_dlg, begin_msg, end_msg, body_lines):
    '''Write a bordered log block (begin line, body, end line).'''
    status_dlg.log_result(begin_msg)
    for line in body_lines:
        if line is not None and line != '':
            status_dlg.log_result(line)
    status_dlg.log_result(end_msg)


def import_converted_book_as_new(db, source_book_id, converted_path, fmt, suffix_tag):
    '''
    Add a new library entry with converted file; does not modify the source book.
    Returns (new_book_id, new_title).
    '''
    mi = db.get_metadata(source_book_id, index_is_id=True)
    new_mi = mi.deepcopy_metadata()
    base_title = (mi.title or '').strip() or _('Unknown')
    new_mi.title = '{} {}'.format(base_title, suffix_tag).strip()
    note = _('Created as a new library book by Chinese Conversion · 简繁转换 (source book id: {}).').format(
        source_book_id)
    if new_mi.comments:
        new_mi.comments = new_mi.comments + '\n\n' + note
    else:
        new_mi.comments = note

    new_id = db.import_book(new_mi, [converted_path], notify=False, apply_import_tags=True)
    try:
        cover = db.cover(source_book_id, index_is_id=True)
        if cover:
            db.set_cover(new_id, cover, notify=True)
    except Exception:
        pass
    return new_id, new_mi.title


def text_preview_from_changes(container, changed_files, max_chars=LIBRARY_PREVIEW_MAX_CHARS):
    '''Plain-text excerpt from the first changed HTML-like file.'''
    html_names = sorted(
        n for n in changed_files
        if n.lower().endswith(('.html', '.htm', '.xhtml'))
    )
    for name in html_names:
        try:
            raw = container.raw_data(name)
            if isinstance(raw, bytes):
                raw = raw.decode('utf-8', errors='replace')
        except Exception:
            continue
        source = raw
        body_match = re.search(r'<body\b[^>]*>(.*?)</body>', source, flags=re.IGNORECASE | re.DOTALL)
        if body_match:
            source = body_match.group(1)
        source = re.sub(
            r'<(style|script)\b[^>]*>.*?</\1>',
            ' ',
            source,
            flags=re.IGNORECASE | re.DOTALL,
        )
        text = re.sub(r'<[^>]+>', '', source)
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            truncated = len(text) > max_chars
            if truncated:
                text = text[:max_chars] + '…'
            header = _('Preview length limit: {} characters').format(max_chars)
            if truncated:
                header = header + '\n' + _('Preview truncated hint')
            return header + '\n\n' + _('File: ') + name + '\n\n' + text
    if changed_files:
        return _('Changed files: ') + ', '.join(sorted(changed_files)[:20])
    return _('No text excerpt available.')


def ocr_preview_from_samples(ocr_samples, ocr_enabled):
    if not ocr_enabled:
        return _('OCR disabled preview')

    samples = list(ocr_samples or [])[:3]
    if not samples:
        return _('OCR enabled but no preview')

    lines = [_('OCR preview header')]
    for idx, sample in enumerate(samples, start=1):
        lines.append(_('OCR preview item').format(idx, sample.get('image', '')))
        lines.append(_('OCR preview recognized').format(_short_preview_text(sample.get('recognized', ''))))
        lines.append(_('OCR preview converted').format(_short_preview_text(sample.get('converted', ''))))
    return '\n'.join(lines)


def ocr_summary_line(ocr_stats, ocr_enabled):
    if not ocr_enabled:
        return ''
    stats = dict(ocr_stats or {})
    images_count = int(stats.get('images_recognized', 0) or 0)
    text_count = int(stats.get('text_results', 0) or 0)
    if images_count <= 0 and text_count <= 0:
        if stats.get('reason') == 'no_image_resources':
            return _('OCR enabled but no image resources summary')
        if stats.get('reason') == 'ocr_no_delta':
            return _('OCR enabled but no delta summary')
        return _('OCR enabled but not used summary')
    samples = [str(item).strip() for item in (stats.get('sample_results') or []) if str(item).strip()]
    sample_text = '，'.join(_short_preview_text(item, 80) for item in samples[:3]) if samples else _('No OCR sample text')
    recognized_images = list(stats.get('recognized_images') or [])
    image_names = [os.path.basename(name) for name in recognized_images[:3]]
    image_names_text = '，'.join(image_names) if image_names else _('No OCR sample text')
    return '\n'.join([
        _('OCR summary line').format(images_count, text_count, sample_text),
        _('OCR summary images line').format(images_count, image_names_text),
    ])


def _short_preview_text(text, max_chars=120):
    value = str(text or '').strip()
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + '…'


def convert_book_to_temp_copy(src_path, fmt, criteria, converter, parser, progress_callback=None):
    '''
    Copy format to a temp file, convert in place, and return
    (tmpdir, temp_path, changed_files, ocr_samples, ocr_stats).
    Caller must shutil.rmtree(tmpdir) when done.
    '''
    converter.clear_replacement_counts()
    tmpdir = tempfile.mkdtemp(prefix='chinese_text_conversion_')
    ext = fmt.lower()
    temp_path = os.path.join(tmpdir, 'converted.{}'.format(ext))
    shutil.copy2(src_path, temp_path)
    from calibre.ebooks.oeb.polish.container import get_container
    from calibre_plugins.chinese_text_conversion.main import (
        cli_process_files, consume_last_ocr_preview_samples, consume_last_ocr_summary_stats)

    container = get_container(temp_path)
    changed_files = cli_process_files(
        criteria, container, converter, parser, progress_callback=progress_callback)
    ocr_samples = consume_last_ocr_preview_samples()
    ocr_stats = consume_last_ocr_summary_stats()
    if changed_files:
        container.commit()
    return tmpdir, temp_path, changed_files or [], ocr_samples, ocr_stats
