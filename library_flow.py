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


def classify_book_languages(language_codes):
    '''
    Return 'chinese', 'non_chinese', or 'unknown' for a list of language codes.
    Unknown/empty metadata is treated as unknown (no warning).
    '''
    codes = [_normalize_language_code(code) for code in (language_codes or [])]
    codes = [code for code in codes if code]
    if not codes:
        return 'unknown'

    has_chinese = False
    has_non_chinese = False
    for code in codes:
        result = is_chinese_language_code(code)
        if result is True:
            has_chinese = True
        elif result is False:
            has_non_chinese = True

    if has_chinese:
        return 'chinese'
    if has_non_chinese:
        return 'non_chinese'
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
    Returns list of (title, language_display) for non-Chinese books.
    '''
    flagged = []
    for title, language_codes in book_items:
        if classify_book_languages(language_codes) != 'non_chinese':
            continue
        display_langs = ', '.join(str(lang) for lang in language_codes if lang and str(lang).strip())
        if not display_langs:
            display_langs = _('Unknown')
        flagged.append((title, display_langs))
    return flagged


def confirm_chinese_books_or_cancel(gui, flagged_books):
    '''
    Warn when metadata language is not Chinese. Returns True to continue.
    '''
    if not flagged_books:
        return True

    from calibre.gui2 import question_dialog

    msg = _('Please confirm the current book language is Chinese.')
    if len(flagged_books) == 1:
        title, langs = flagged_books[0]
        det_msg = _('Book: {}\nLanguage: {}').format(title, langs)
    else:
        lines = [
            _('The following {} book(s) are not marked as Chinese:').format(
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


def make_conversion_suffix():
    '''Plugin name + local time (HH-MM-SS), safe for titles and filenames.'''
    stamp = datetime.now().strftime('%H-%M-%S')
    return '{}-{}'.format(PLUGIN_SAFE_NAME, stamp)


def import_converted_book_as_new(db, source_book_id, converted_path, fmt, suffix_tag):
    '''
    Add a new library entry with converted file; does not modify the source book.
    Returns (new_book_id, new_title).
    '''
    mi = db.get_metadata(source_book_id, index_is_id=True)
    new_mi = mi.deepcopy_metadata()
    base_title = (mi.title or '').strip() or _('Unknown')
    new_mi.title = '{} {}'.format(base_title, suffix_tag).strip()
    note = _('Created as a new library book by Chinese Text Conversion (source book id: {}).').format(
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


def text_preview_from_changes(container, changed_files, max_chars=1200):
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
        text = re.sub(r'<[^>]+>', '', raw)
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            if len(text) > max_chars:
                text = text[:max_chars] + '…'
            return _('File: ') + name + '\n\n' + text
    if changed_files:
        return _('Changed files: ') + ', '.join(sorted(changed_files)[:20])
    return _('No text excerpt available.')


def convert_book_to_temp_copy(src_path, fmt, criteria, converter, parser):
    '''
    Copy format to a temp file, convert in place, return (tmpdir, temp_path, changed_files).
    Caller must shutil.rmtree(tmpdir) when done.
    '''
    tmpdir = tempfile.mkdtemp(prefix='chinese_text_conversion_')
    ext = fmt.lower()
    temp_path = os.path.join(tmpdir, 'converted.{}'.format(ext))
    shutil.copy2(src_path, temp_path)
    from calibre.ebooks.oeb.polish.container import get_container
    from calibre_plugins.chinese_text_conversion.main import cli_process_files

    container = get_container(temp_path)
    changed_files = cli_process_files(criteria, container, converter, parser)
    if changed_files:
        container.commit()
    return tmpdir, temp_path, changed_files or []
