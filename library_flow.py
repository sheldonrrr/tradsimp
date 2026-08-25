# -*- coding: utf-8 -*-

__license__ = 'GPL 3'

import os
import re
import shutil
import tempfile
import time
from datetime import datetime

from calibre_plugins.chinese_text_conversion.__init__ import (
    PLUGIN_RELEASE_THREAD_URL, PLUGIN_SAFE_NAME)
from calibre_plugins.chinese_text_conversion.i18n import (
    _, translate, UI_LANG_ZH_CN, UI_LANG_ZH_HK, UI_LANG_ZH_TW)


def confirm_and_open_release_notes(parent):
    '''Ask before opening the MobileRead release page in a browser.'''
    from calibre.gui2 import open_url, question_dialog
    try:
        from qt.core import QUrl
    except ImportError:
        from PyQt5.QtCore import QUrl
    proceed = question_dialog(
        parent,
        _("What's new"),
        _('Open release notes confirm'),
        default_yes=False,
        yes_text=_('Open in browser'),
        no_text=_('Cancel'),
    )
    if proceed:
        open_url(QUrl(PLUGIN_RELEASE_THREAD_URL))


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
LIBRARY_DIAGNOSTIC_SAMPLE_LIMIT = 12
LIBRARY_JIEBA_SAMPLE_LIMIT = 8
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
    prefix = []
    if getattr(converter, 'get_force_pivot_conversion', lambda: False)():
        prefix.append(_('Forced pivot conversion: {0}').format(_('enabled')))
    if not counts:
        prefix.append(_('No OpenCC replacements recorded for this book.'))
        return '\n'.join(prefix)
    total = sum(counts.values())
    unique = len(counts)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
    lines = prefix + [
        _('OpenCC replacements: {} hits, {} unique pairs').format(
            '{:,}'.format(total), '{:,}'.format(unique)),
    ]
    for (old, new), n in ranked[:max_samples]:
        lines.append('  {} → {} (×{:,})'.format(old, new, n))
    remaining = unique - min(unique, max_samples)
    if remaining > 0:
        lines.append(_('… and {} more unique pairs not shown').format(
            '{:,}'.format(remaining)))
    return '\n'.join(lines)


def format_conversion_diagnostics_log(
        converter, max_samples=LIBRARY_DIAGNOSTIC_SAMPLE_LIMIT):
    diagnostics = converter.get_conversion_diagnostics()
    counts = diagnostics.get('counts') or {}
    samples = diagnostics.get('samples') or []
    if not counts:
        return ''

    total = sum(counts.values())
    mixed = sum(
        count for (kind, _source, _target), count in counts.items()
        if kind == 'traditional_input_in_simplified_mode')
    ambiguous = sum(
        count for (kind, _source, _target), count in counts.items()
        if kind == 'ambiguous_character_fallback')
    lines = [
        _('Conversion diagnostics: {} suspicious hits').format(
            '{:,}'.format(total)),
        _('  Traditional-only input in Simplified mode: {}').format(
            '{:,}'.format(mixed)),
        _('  Ambiguous character fallbacks: {}').format(
            '{:,}'.format(ambiguous)),
    ]
    displayable = [
        sample for sample in samples
        if (sample.get('kind') == 'traditional_input_in_simplified_mode'
            or (sample.get('source') or '') != (sample.get('target') or ''))
    ]
    for sample in displayable[:max_samples]:
        kind = sample.get('kind')
        source = sample.get('source') or ''
        target = sample.get('target') or ''
        context = sample.get('context') or ''
        if kind == 'traditional_input_in_simplified_mode':
            lines.append(
                _('  Mixed input: {} (context: {})').format(source, context))
        else:
            lines.append(
                _('  Ambiguous fallback: {} → {}').format(source, target))
    remaining = len(displayable) - min(len(displayable), max_samples)
    if remaining > 0:
        lines.append(_('… and {} more samples not shown').format(
            '{:,}'.format(remaining)))
    return '\n'.join(lines)


def _text_has_cjk(text):
    for ch in text or '':
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


_JIEBA_LOG_TAG_RE = re.compile(r'</?[A-Za-z][^>]*>')
_JIEBA_LOG_ENTITY_RE = re.compile(r'&(?:#\d+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);')
_JIEBA_LOG_MARKUP_TOKENS = frozenset((
    '<', '>', '/', '&', ';', '#',
    'nbsp', 'ensp', 'emsp', 'thinsp', 'zwnj', 'zwj', 'shy',
    'mdash', 'ndash', 'minus', 'hellip', 'middot',
    'quot', 'amp', 'lt', 'gt', 'apos',
    'ldquo', 'rdquo', 'lsquo', 'rsquo', 'laquo', 'raquo',
    'p', 'br', 'div', 'span', 'em', 'strong', 'b', 'i', 'u',
))


def _plain_jieba_log_text(text):
    import html
    cleaned = _JIEBA_LOG_TAG_RE.sub('', text or '')
    cleaned = _JIEBA_LOG_ENTITY_RE.sub(' ', cleaned)
    cleaned = html.unescape(cleaned).replace('\xa0', ' ')
    return ' '.join(cleaned.split())


def _is_jieba_log_markup_token(token):
    piece = (token or '').strip()
    if not piece or piece in _JIEBA_LOG_MARKUP_TOKENS:
        return True
    if piece.startswith('<') or piece.endswith('>'):
        return True
    if _JIEBA_LOG_ENTITY_RE.fullmatch(piece):
        return True
    return piece.lower().strip('&;') in _JIEBA_LOG_MARKUP_TOKENS


def format_jieba_samples_log(converter, max_samples=LIBRARY_JIEBA_SAMPLE_LIMIT):
    """Human-readable Jieba cut samples: original → tokens → converted tokens."""
    samples = list(converter.get_jieba_samples() or [])
    cjk_samples = [
        sample for sample in samples if _text_has_cjk(sample.get('text') or '')]
    samples = cjk_samples or samples
    if not samples:
        return _('No Jieba segmentation samples recorded for this book.')
    lines = []
    for sample in samples[:max_samples]:
        text = _plain_jieba_log_text(sample.get('text') or '')
        segs = sample.get('segments') or []
        conv = sample.get('converted_segments') or []
        kept = [
            (seg, converted)
            for seg, converted in zip(segs, conv)
            if not _is_jieba_log_markup_token(seg)
        ]
        if not text or not kept or not _text_has_cjk(text):
            continue
        cut = ' / '.join(seg for seg, _converted in kept)
        out = ' / '.join(converted for _seg, converted in kept)
        lines.append('  {} → {} → {}'.format(text, cut, out))
    if not lines:
        return _('No Jieba segmentation samples recorded for this book.')
    return '\n'.join(lines)


def make_conversion_suffix():
    '''
    Plugin name + local time (HH-MM-SS) for conversion logs only (not applied to titles).
    Returns (suffix_tag, generated_at) so logs can show the same instant.
    '''
    generated_at = datetime.now()
    stamp = generated_at.strftime('%H-%M-%S')
    suffix_tag = '{}-{}'.format(PLUGIN_SAFE_NAME, stamp)
    return suffix_tag, generated_at


# Title-suffix timestamp formats (prefs / criteria).
SUFFIX_TIMESTAMP_OFF = 'off'
SUFFIX_TIMESTAMP_ISO = 'iso'              # YYYY-MM-DD_HH-MM-SS
SUFFIX_TIMESTAMP_COMPACT = 'compact'      # YYYYMMDD_HHMMSS
SUFFIX_TIMESTAMP_NO_SECONDS = 'no_seconds'  # YYYY-MM-DD_HH-MM
SUFFIX_TIMESTAMP_DEFAULT = SUFFIX_TIMESTAMP_ISO
SUFFIX_TIMESTAMP_FORMATS = (
    SUFFIX_TIMESTAMP_OFF,
    SUFFIX_TIMESTAMP_ISO,
    SUFFIX_TIMESTAMP_COMPACT,
    SUFFIX_TIMESTAMP_NO_SECONDS,
)

# Longer patterns first so ISO wins over No-seconds; include legacy MM-DD_HH-MM.
_BOOK_TIME_CODE_BODY = (
    r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
    r'|\d{8}_\d{6}'
    r'|\d{4}-\d{2}-\d{2}_\d{2}-\d{2}'
    r'|\d{2}-\d{2}_\d{2}-\d{2}'
)
_BOOK_TIME_CODE_RE = re.compile(
    r'(?:' + _BOOK_TIME_CODE_BODY + r')(?:_(?:[2-9]|\d{2,}))?')
_BOOK_TIME_CODE_AT_TITLE_END_RE = re.compile(
    r'_(' + _BOOK_TIME_CODE_RE.pattern + r')(?=\s*$)')


def normalize_suffix_timestamp_format(value, append_conversion_suffix=None):
    '''Normalize prefs/criteria to one of SUFFIX_TIMESTAMP_FORMATS.'''
    text = (value or '').strip().lower() if value is not None else ''
    if text in SUFFIX_TIMESTAMP_FORMATS:
        return text
    # Legacy boolean preference: True → ISO (recommended), False → off.
    if append_conversion_suffix is not None:
        return (
            SUFFIX_TIMESTAMP_ISO if append_conversion_suffix
            else SUFFIX_TIMESTAMP_OFF)
    return SUFFIX_TIMESTAMP_DEFAULT


def suffix_timestamp_enabled(timestamp_format):
    return normalize_suffix_timestamp_format(timestamp_format) != SUFFIX_TIMESTAMP_OFF


def format_book_timestamp(generated_at, timestamp_format):
    '''Return the bare timestamp string for the chosen format, or '' if off.'''
    fmt = normalize_suffix_timestamp_format(timestamp_format)
    generated_at = generated_at or datetime.now()
    if fmt == SUFFIX_TIMESTAMP_ISO:
        return generated_at.strftime('%Y-%m-%d_%H-%M-%S')
    if fmt == SUFFIX_TIMESTAMP_COMPACT:
        return generated_at.strftime('%Y%m%d_%H%M%S')
    if fmt == SUFFIX_TIMESTAMP_NO_SECONDS:
        return generated_at.strftime('%Y-%m-%d_%H-%M')
    return ''


def collect_generated_book_time_codes(db):
    """Return time codes already used at the end of titles in the library."""
    codes = set()
    for book_id in db.all_ids():
        try:
            title = db.title(book_id, index_is_id=True) or ''
        except Exception:
            continue
        match = _BOOK_TIME_CODE_AT_TITLE_END_RE.search(title)
        if match:
            codes.add(match.group(1))
    return codes


def make_book_time_code(
        generated_at=None, used_codes=None,
        timestamp_format=SUFFIX_TIMESTAMP_DEFAULT):
    """Return a local-time code in the chosen format; add a sequence if used."""
    fmt = normalize_suffix_timestamp_format(timestamp_format)
    if fmt == SUFFIX_TIMESTAMP_OFF:
        return ''
    generated_at = generated_at or datetime.now()
    base_code = format_book_timestamp(generated_at, fmt)
    if not base_code:
        return ''
    if used_codes is None:
        used_codes = set()

    code = base_code
    sequence = 2
    while code in used_codes:
        code = '{}_{}'.format(base_code, sequence)
        sequence += 1
    used_codes.add(code)
    return code


# Kind → fixed token written into library titles (stable for strip/regex).
_SUFFIX_TARGET_TOKENS = {
    'traditional_hong_kong': '繁體中文_香港',
    'traditional_taiwan': '繁體中文_台灣',
    'japanese_kanji': '日文汉字',
    'simplified': '简体中文',
    'traditional': '繁体中文',
    'chinese_conversion': '中文转换',
}
_SUFFIX_TARGET_MSGIDS = {
    'traditional_hong_kong': 'Suffix target traditional hong kong',
    'traditional_taiwan': 'Suffix target traditional taiwan',
    'japanese_kanji': 'Suffix target japanese kanji',
    'simplified': 'Suffix target simplified',
    'traditional': 'Suffix target traditional',
    'chinese_conversion': 'Suffix target chinese conversion',
}


def title_suffix_target_kind(conversion_type, output_locale):
    """Classify the target-language marker for generated book title suffixes."""
    if output_locale == 1:
        return 'traditional_hong_kong'
    if output_locale == 2:
        return 'traditional_taiwan'
    if output_locale == 3:
        return 'japanese_kanji'
    if conversion_type == 1:
        return 'simplified'
    if conversion_type in (2, 3):
        return 'traditional'
    return 'chinese_conversion'


def title_suffix_target_token(conversion_type, output_locale):
    """Stable (non-localized) target token embedded in generated titles."""
    return _SUFFIX_TARGET_TOKENS[title_suffix_target_kind(
        conversion_type, output_locale)]


def title_suffix_target_label(conversion_type, output_locale):
    """Localized target marker for UI suffix examples."""
    return _(_SUFFIX_TARGET_MSGIDS[title_suffix_target_kind(
        conversion_type, output_locale)])


def make_converted_title_suffix(
        conversion_type, output_locale, bilingual=False, enabled=None,
        time_code=None, generated_at=None, used_time_codes=None,
        timestamp_format=SUFFIX_TIMESTAMP_DEFAULT):
    """Build the visible suffix appended to each generated library-book title."""
    fmt = normalize_suffix_timestamp_format(timestamp_format)
    if enabled is None:
        enabled = suffix_timestamp_enabled(fmt)
    if not enabled or fmt == SUFFIX_TIMESTAMP_OFF:
        return ''

    target = title_suffix_target_token(conversion_type, output_locale)

    code = time_code or make_book_time_code(
        generated_at, used_time_codes, timestamp_format=fmt)
    if not code or not _BOOK_TIME_CODE_RE.fullmatch(code):
        raise ValueError(
            'book time code must match a supported timestamp format '
            'with an optional sequence')
    parts = [target]
    if bilingual and conversion_type != 0:
        parts.append('双语标注')
    parts.append(code)
    return '_' + '_'.join(parts)


def format_book_tag_log_lines(suffix_tag, generated_at):
    '''Human-readable conversion-time lines for the status log (not applied to titles).'''
    time_stamp = generated_at.strftime('%Y-%m-%d %H:%M:%S')
    return '\n'.join([
        _('Log conversion id: {}').format(suffix_tag),
        _('Log generated at (local time): {}').format(time_stamp),
    ])


def format_elapsed_duration(seconds):
    '''Format seconds as M:SS or H:MM:SS.'''
    total = max(0, int(round(float(seconds or 0))))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return '{}:{:02d}:{:02d}'.format(hours, minutes, secs)
    return '{}:{:02d}'.format(minutes, secs)


def format_progress_status_fields(local_done, local_total, book_started_at, converter):
    '''
    Structured progress lines for the status dialog (one field per row).
    Empty strings keep the corresponding fixed row blank without removing it.
    '''
    total = max(int(local_total or 0), 1)
    done = max(0, min(int(local_done or 0), total))
    fields = {
        'percent': _('Progress percent').format(int(round(100.0 * done / total))),
        'elapsed': '',
        'eta': '',
        'chars': '',
    }

    elapsed = 0.0
    if book_started_at is not None:
        elapsed = max(0.0, time.time() - float(book_started_at))
    fields['elapsed'] = _('Progress elapsed').format(format_elapsed_duration(elapsed))
    if done > 0 and done < total and elapsed > 0:
        eta = elapsed * (total - done) / float(done)
        fields['eta'] = _('Progress eta').format(format_elapsed_duration(eta))

    if converter is not None:
        processed = int(converter.get_chars_processed() or 0)
        converted = int(converter.get_chars_converted() or 0)
        fields['chars'] = _('Progress chars').format(
            '{:,}'.format(processed), '{:,}'.format(converted))
    return fields


def format_progress_enrichment(local_done, local_total, book_started_at, converter):
    '''
    Extra progress fragments: percent, elapsed, ETA, character counts.
    Joined with " · " for log lines.
    '''
    fields = format_progress_status_fields(
        local_done, local_total, book_started_at, converter)
    parts = [
        fields.get('percent') or '',
        fields.get('elapsed') or '',
        fields.get('eta') or '',
        fields.get('chars') or '',
    ]
    return ' · '.join(part for part in parts if part)


def format_opencc_dict_version_label():
    '''Read-only OpenCC pin plus local override summary.'''
    from calibre_plugins.chinese_text_conversion.resources.user_dicts import (
        bundled_opencc_pin, overridden_dict_names)
    _commit, tag = bundled_opencc_pin()
    names = overridden_dict_names()
    if not names:
        return _('OpenCC dictionary version: {}').format(tag)
    return _('OpenCC dictionary version with local: {0} + {1} files ({2})').format(
        tag, len(names), ', '.join(names))


def format_local_opencc_dicts_log():
    '''One log line listing local dictionary overrides, or empty.'''
    from calibre_plugins.chinese_text_conversion.resources.user_dicts import (
        overridden_dict_names)
    names = overridden_dict_names()
    if not names:
        return ''
    return _('Local OpenCC dictionaries: {}').format(', '.join(names))


def format_conversion_stats_log(
        chars_processed=0, chars_converted=0, replacement_hits=0,
        elapsed_seconds=0):
    '''Human-readable per-book conversion stats for the status log.'''
    lines = [
        _('Conversion stats total characters: {}').format(
            '{:,}'.format(int(chars_processed or 0))),
        _('Conversion stats converted characters: {}').format(
            '{:,}'.format(int(chars_converted or 0))),
        _('Conversion stats replacement hits: {}').format(
            '{:,}'.format(int(replacement_hits or 0))),
        _('Conversion stats process time: {}').format(
            format_elapsed_duration(elapsed_seconds)),
    ]
    extra = format_local_opencc_dicts_log()
    if extra:
        lines.append(extra)
    return '\n'.join(lines)


def comments_template_language(conversion_type, output_locale=0):
    '''Catalog language for Comments templates written into the new book.

    Traditional targets use Traditional (Taiwan / Hong Kong) templates;
    Simplified targets use Simplified templates. Other cases follow the UI.
    '''
    try:
        conversion_type = int(conversion_type or 0)
        output_locale = int(output_locale or 0)
    except (TypeError, ValueError):
        return None
    kind = title_suffix_target_kind(conversion_type, output_locale)
    if kind == 'traditional_hong_kong':
        return UI_LANG_ZH_HK
    if kind in ('traditional_taiwan', 'traditional'):
        return UI_LANG_ZH_TW
    if kind == 'simplified':
        return UI_LANG_ZH_CN
    return None


def format_conversion_direction_label(
        conversion_type, input_locale=0, output_locale=0, lang=None):
    '''Short human-readable conversion direction for Comments / logs.'''
    if lang is None:
        lang = comments_template_language(conversion_type, output_locale)
    if conversion_type == 0:
        return translate('No Change', lang)
    locale_names = {
        0: translate('Mainland', lang),
        1: translate('Hong Kong', lang),
        2: translate('Taiwan', lang),
        3: translate('Japanese Kanji', lang),
    }
    src = locale_names.get(input_locale, str(input_locale))
    dst = locale_names.get(output_locale, str(output_locale))
    if conversion_type == 1:
        return translate('Comments direction trad to simp: {} → {}', lang).format(
            src, dst)
    if conversion_type == 2:
        return translate('Comments direction simp to trad: {} → {}', lang).format(
            src, dst)
    if conversion_type == 3:
        return translate('Comments direction trad to trad: {} → {}', lang).format(
            src, dst)
    return '{} → {}'.format(src, dst)


def format_conversion_info_comment_lines(stats, lang=None):
    '''Compact conversion-info lines for Comments / 简介.'''
    stats = stats or {}
    conversion_type = stats.get('conversion_type', 0)
    input_locale = stats.get('input_locale', 0)
    output_locale = stats.get('output_locale', 0)
    if lang is None:
        lang = comments_template_language(conversion_type, output_locale)
    lines = [
        translate('Comments conversion info header', lang),
        translate('Conversion stats total characters: {}', lang).format(
            '{:,}'.format(int(stats.get('chars_processed', 0) or 0))),
        translate('Conversion stats converted characters: {}', lang).format(
            '{:,}'.format(int(stats.get('chars_converted', 0) or 0))),
        translate('Conversion stats replacement hits: {}', lang).format(
            '{:,}'.format(int(stats.get('replacement_hits', 0) or 0))),
        translate('Conversion stats process time: {}', lang).format(
            format_elapsed_duration(stats.get('elapsed_seconds', 0))),
    ]
    suffix_tag = stats.get('suffix_tag')
    generated_at = stats.get('generated_at')
    if suffix_tag:
        lines.append(translate('Log conversion id: {}', lang).format(suffix_tag))
    if generated_at is not None:
        try:
            stamp = generated_at.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            stamp = str(generated_at)
        lines.append(translate('Log generated at (local time): {}', lang).format(
            stamp))
    direction = stats.get('direction_label')
    if not direction and conversion_type:
        direction = format_conversion_direction_label(
            conversion_type, input_locale, output_locale, lang=lang)
    if direction:
        lines.append(translate('Comments conversion direction: {}', lang).format(
            direction))
    return lines


def preview_conversion_info_comment_text(
        conversion_type=0, input_locale=0, output_locale=0):
    '''Settings preview of the Comments conversion-info block about to be written.'''
    # Sample runtime fields so the template matches a real write; language
    # follows the conversion target (Traditional templates for Traditional output).
    lang = comments_template_language(conversion_type, output_locale)
    stats = {
        'chars_processed': 12345,
        'chars_converted': 2345,
        'replacement_hits': 3000,
        'elapsed_seconds': 12,
        'suffix_tag': '{}-14-23-00'.format(PLUGIN_SAFE_NAME),
        'generated_at': datetime(2026, 8, 6, 14, 23, 0),
        'conversion_type': conversion_type,
        'input_locale': input_locale,
        'output_locale': output_locale,
        'direction_label': format_conversion_direction_label(
            conversion_type, input_locale, output_locale, lang=lang),
    }
    return '\n'.join(format_conversion_info_comment_lines(stats, lang=lang))


def build_library_conversion_comments_note(stats=None, store_info=False, lang=None):
    '''Promo block (+ optional conversion stats) written into Comments / 简介.'''
    stats = stats or {}
    if lang is None:
        lang = comments_template_language(
            stats.get('conversion_type', 0),
            stats.get('output_locale', 0))
    lines = [
        translate(
            'Converted by Chinese Conversion · 简繁转换(for calibre) plugin',
            lang),
        PLUGIN_RELEASE_THREAD_URL,
        translate('Plugin comments tagline', lang),
    ]
    if store_info and stats:
        lines.append('')
        lines.extend(format_conversion_info_comment_lines(stats, lang=lang))
    return '\n'.join(lines)


_PLUGIN_TITLE_SUFFIX_RE = re.compile(
    r'(?:\s+|^)' + re.escape(PLUGIN_SAFE_NAME) + r'-\d{2}-\d{2}-\d{2}(?=\s*$)')
_GENERATED_TITLE_SUFFIX_RE = re.compile(
    r'_(?:简体中文|繁[体體]中文(?:_(?:香港|台湾|台灣|臺灣))?|日文汉字|中文转换)'
    r'(?:_双语标注)?_(?:[A-Za-z0-9]{4}|'
    + _BOOK_TIME_CODE_RE.pattern + r')(?=\s*$)')

_PLUGIN_COMMENT_MARKERS = (
    PLUGIN_RELEASE_THREAD_URL,
    'for calibre',
    'source book id:',
    '来源书籍编号',
    '來源書籍編號',
    '新建入库',
    '新建入庫',
    'Created as a new library book by Chinese Conversion',
    'Converted by the “Chinese Conversion',
    'Converted by Chinese Conversion',
    '完全离线，不调用大语言模型',
    '完全離線，不呼叫大型語言模型',
    'Fully offline — no large language models',
    '插件支持横竖排转换',
    '外掛支援橫豎排轉換',
    'Supports horizontal/vertical layout conversion',
    'Comments conversion info',
    'Conversion info',
    '转换信息',
    '轉換資訊',
    'Conversion stats total characters',
    '总字符数',
    '總字元數',
    'Conversion stats converted characters',
    '已转换字符',
    '已轉換字元',
    'Conversion stats process time',
    '处理耗时',
    '處理耗時',
    'Comments conversion direction',
    '转换方向',
    '轉換方向',
)


def sanitize_converted_book_title(title):
    '''Remove legacy and current generated suffixes from title/title_sort.'''
    text = (title or '').strip()
    while True:
        cleaned = _PLUGIN_TITLE_SUFFIX_RE.sub('', text).strip()
        cleaned = _GENERATED_TITLE_SUFFIX_RE.sub('', cleaned).strip()
        if cleaned == text:
            return cleaned
        text = cleaned


def _plain_comment_text(block):
    text = re.sub(r'(?is)<br\s*/?>', '\n', block or '')
    text = re.sub(r'(?is)<[^>]+>', '', text)
    return text.replace('&nbsp;', ' ').strip()


def _is_plugin_comment_block(block):
    plain = _plain_comment_text(block)
    if not plain or re.fullmatch(r'-{3,}', plain):
        return True
    for marker in _PLUGIN_COMMENT_MARKERS:
        if marker in plain or marker in (block or ''):
            return True
    if 'Chinese Conversion' in plain and (
            '插件' in plain or '外掛' in plain or 'plugin' in plain.lower()):
        return True
    return False


def _strip_plugin_paragraphs(segment):
    paras = re.split(r'\n\s*\n', (segment or '').strip())
    while paras and _is_plugin_comment_block(paras[0]):
        paras.pop(0)
    while paras and _is_plugin_comment_block(paras[-1]):
        paras.pop()
    return '\n\n'.join(p.strip() for p in paras if p.strip()).strip()


def sanitize_converted_book_comments(comments):
    '''
    Remove prior plugin promo / “created by plugin” blocks from Comments so
    re-converting a previously converted book does not stack history.
    '''
    text = (comments or '').strip()
    if not text:
        return ''
    text = re.sub(r'(?is)<hr\s*/?>', '\n----\n', text)
    segments = re.split(r'\n\s*-{3,}\s*\n', text)
    kept = []
    for seg in segments:
        cleaned = _strip_plugin_paragraphs(seg)
        if cleaned and not _is_plugin_comment_block(cleaned):
            kept.append(cleaned)
    return '\n\n'.join(kept).strip()


def append_library_conversion_comments(existing_comments, note):
    '''
    Append the conversion promo note to Comments.
    If other text already exists, separate with a ---- line below it.
    '''
    existing = sanitize_converted_book_comments(existing_comments)
    if existing:
        return existing + '\n----\n' + note
    return note


def format_numbered_log_marker(marker, step, total):
    '''
    Insert a (n/N) flow index into a ----section---- marker.
    Example: ----Book info begin---- → ---- (1/5) Book info begin ----
    '''
    raw = (marker or '').strip()
    if raw.startswith('----') and raw.endswith('----') and len(raw) > 8:
        inner = raw[4:-4].strip()
    else:
        inner = raw
    return _('----Log numbered marker----').format(
        int(step), int(total), inner)


def format_log_phase_header(step, total, title):
    '''Top-level phase divider, e.g. —— (1/3) Preparation ——.'''
    return _('Log phase header').format(int(step), int(total), title)


def log_phase_header(status_dlg, step, total, title, blank_after=True):
    '''Write a top-level phase header (and optional trailing blank line).'''
    status_dlg.log_result(format_log_phase_header(step, total, title))
    if blank_after:
        status_dlg.log_result('')


def log_section(status_dlg, title, body_lines, blank_after=True):
    '''Write a titled plain-text log block (one header, no matching end line).'''
    title = (title or '').strip()
    if title:
        status_dlg.log_result(title)
    for line in body_lines:
        if line is not None and line != '':
            status_dlg.log_result(line)
    if blank_after:
        status_dlg.log_result('')


def _convert_text(converter, value):
    '''OpenCC-convert a non-empty string; leave None/empty unchanged.'''
    if value is None:
        return value
    text = value if isinstance(value, str) else str(value)
    if not text:
        return value
    return converter.convert(text)


def convert_calibre_metadata(mi, converter):
    '''
    OpenCC-convert Calibre library fields so the new book row matches converted content.
    Mutates mi in place. Covers title, authors, tags, publisher, comments/简介
    (and sort fields). Does not touch identifiers, series index, dates, rating, or cover.
    '''
    if mi.title:
        mi.title = _convert_text(converter, mi.title)
    if getattr(mi, 'title_sort', None):
        mi.title_sort = _convert_text(converter, mi.title_sort)
    if mi.authors:
        mi.authors = [_convert_text(converter, a) for a in mi.authors]
    if getattr(mi, 'author_sort', None):
        mi.author_sort = _convert_text(converter, mi.author_sort)
    if mi.tags:
        mi.tags = [_convert_text(converter, t) for t in mi.tags]
    if mi.publisher:
        mi.publisher = _convert_text(converter, mi.publisher)
    if getattr(mi, 'comments', None):
        mi.comments = _convert_text(converter, mi.comments)


def _conversion_utcnow():
    '''UTC "now" for Calibre Date / last_modified (timezone-aware when available).'''
    try:
        from calibre.utils.date import utcnow
        return utcnow()
    except Exception:
        try:
            from datetime import timezone
            return datetime.now(timezone.utc)
        except Exception:
            return datetime.utcnow()


def import_converted_book_as_new(
        db, source_book_id, converted_path, fmt, suffix_tag=None,
        converter=None, title_suffix='', conversion_stats=None,
        store_conversion_info=False, use_conversion_date=True):
    '''
    Add a new library entry with converted file; does not modify the source book.
    When converter is provided, OpenCC-converts title/authors/tags/publisher/comments
    (简介) and sort fields. title_suffix identifies the generated target form.
    After conversion,
    Comments get a short plugin promo note (with ---- separator when prior comments
    exist). When store_conversion_info is True, a compact conversion stats summary
    is appended under the promo. When use_conversion_date is True (default), the
    new book's Date / last_modified follow conversion time so sorting by Date
    finds the new entry; pubdate is left unchanged. suffix_tag is unused (kept
    for call-site compat).
    Returns (new_book_id, new_title).
    '''
    mi = db.get_metadata(source_book_id, index_is_id=True)
    new_mi = mi.deepcopy_metadata()
    # Drop legacy title suffixes / stacked promo notes copied from a prior conversion.
    new_mi.title = sanitize_converted_book_title(new_mi.title)
    if getattr(new_mi, 'title_sort', None):
        new_mi.title_sort = sanitize_converted_book_title(new_mi.title_sort)
    new_mi.comments = sanitize_converted_book_comments(new_mi.comments)
    if converter is not None:
        convert_calibre_metadata(new_mi, converter)
    new_mi.title = (new_mi.title or '').strip() or _('Unknown')
    if title_suffix:
        new_mi.title += title_suffix
        if getattr(new_mi, 'title_sort', None):
            new_mi.title_sort = new_mi.title_sort.rstrip() + title_suffix
    new_mi.comments = append_library_conversion_comments(
        new_mi.comments,
        build_library_conversion_comments_note(
            stats=conversion_stats, store_info=store_conversion_info))
    if use_conversion_date:
        # deepcopy_metadata copies the source Date; reset so new books sort as
        # recently added (the usual “find my conversion” workflow).
        now = _conversion_utcnow()
        new_mi.timestamp = now
        if hasattr(new_mi, 'last_modified'):
            new_mi.last_modified = now
        try:
            os.utime(converted_path, None)
        except Exception:
            pass

    # Keep notify=False; GUI row insertion is handled in ui._refresh_library_new_books
    # via model.books_added() (Calibre plugin pattern). Avoid set_cover(notify=True)
    # here so a partial metadata notify cannot desync the view before books_added.
    new_id = db.import_book(new_mi, [converted_path], notify=False, apply_import_tags=True)
    try:
        cover = db.cover(source_book_id, index_is_id=True)
        if cover:
            db.set_cover(new_id, cover, notify=False)
    except Exception:
        pass
    return new_id, new_mi.title


_PREVIEW_NAV_TOC_BASENAMES = frozenset((
    'nav.xhtml', 'nav.html', 'nav.htm',
    'toc.xhtml', 'toc.html', 'toc.htm',
))


def _is_preview_nav_or_toc(name):
    base = os.path.basename(name or '').lower()
    if base in _PREVIEW_NAV_TOC_BASENAMES:
        return True
    stem = os.path.splitext(base)[0]
    return stem in ('nav', 'toc') or stem.startswith('toc')


def _html_to_preview_text(source):
    '''Strip tags but keep paragraph breaks so the log stays readable.'''
    source = re.sub(
        r'<(style|script)\b[^>]*>.*?</\1>',
        ' ',
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    source = re.sub(r'<br\s*/?>', '\n', source, flags=re.IGNORECASE)
    source = re.sub(
        r'</(?:p|div|h[1-6]|li|tr|blockquote|section|article|header|nav)\s*>',
        '\n',
        source,
        flags=re.IGNORECASE,
    )
    text = re.sub(r'<[^>]+>', '', source)
    text = text.replace('\xa0', ' ').replace('&nbsp;', ' ')
    text = re.sub(r'[^\S\n]+', ' ', text)
    text = re.sub(r' *\n *', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def text_preview_from_changes(container, changed_files, max_chars=LIBRARY_PREVIEW_MAX_CHARS):
    '''Plain-text excerpt from the first changed content HTML file.'''
    html_names = sorted(
        n for n in changed_files
        if n.lower().endswith(('.html', '.htm', '.xhtml'))
    )
    preferred = [n for n in html_names if not _is_preview_nav_or_toc(n)]
    for name in (preferred or html_names):
        try:
            raw = container.raw_data(name)
            if isinstance(raw, bytes):
                raw = raw.decode('utf-8', errors='replace')
        except Exception:
            continue
        source = raw
        body_match = re.search(
            r'<body\b[^>]*>(.*?)</body>', source,
            flags=re.IGNORECASE | re.DOTALL)
        if body_match:
            source = body_match.group(1)
        text = _html_to_preview_text(source)
        if text:
            truncated = len(text) > max_chars
            if truncated:
                text = text[:max_chars].rstrip() + '…'
                header = _('Preview file header').format(name, max_chars)
            else:
                header = _('Preview file header full').format(name)
            return header + '\n\n' + text
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
