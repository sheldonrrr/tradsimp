# -*- coding: utf-8 -*-

"""Derive filter tokens for the Script / 书写系统 column (no Calibre imports)."""

__license__ = 'GPL 3'

_LOCALE_BY_REGION = {
    'CN': 'zh_CN',
    'TW': 'zh_TW',
    'HK': 'zh_HK',
    'MO': 'zh_MO',
}


def conversion_language_code(conversion_type, input_locale, output_locale):
    """BCP-47 used for HTML/OPF language, or '' when no language change.

    Mirrors ``main.get_language_code`` (which returns ``'None'`` for '').
    """
    try:
        conversion_mode = int(conversion_type or 0)
        input_type = int(input_locale or 0)
        output_type = int(output_locale or 0)
    except (TypeError, ValueError):
        return ''

    if conversion_mode == 1:
        if output_type == 0:
            return 'zh-Hans-CN'
    elif conversion_mode == 2:
        if output_type == 0:
            return 'zh-Hant-CN'
        if output_type == 1:
            return 'zh-Hant-HK'
        return 'zh-Hant-TW'
    elif conversion_mode == 3:
        if input_type == 0:
            if output_type == 1:
                return 'zh-Hant-HK'
            if output_type == 2:
                return 'zh-Hant-TW'
            return ''
        if input_type == 1:
            if output_type == 0:
                return 'zh-Hant-CN'
            if output_type == 2:
                return 'zh-Hant-TW'
            return ''
        if input_type == 2:
            if output_type == 0:
                return 'zh-Hant-CN'
            if output_type == 1:
                return 'zh-Hant-HK'
            return ''
    return ''


def _script_and_region(conversion_type, input_locale, output_locale):
    try:
        output_type = int(output_locale or 0)
    except (TypeError, ValueError):
        output_type = 0
    if output_type == 3:
        return '', ''

    full = conversion_language_code(
        conversion_type, input_locale, output_locale)
    if not full:
        return '', ''

    script = ''
    region = ''
    for part in full.replace('_', '-').split('-')[1:]:
        low = part.lower()
        if low in ('hans', 'hant'):
            script = low
        elif low in ('cn', 'tw', 'hk', 'mo'):
            region = low.upper()
    return script, region


def bcp47_script_tag(conversion_type, input_locale, output_locale):
    """BCP-47 script subtag: zh-Hans or zh-Hant."""
    script, _region = _script_and_region(
        conversion_type, input_locale, output_locale)
    if script == 'hans':
        return 'zh-Hans'
    if script == 'hant':
        return 'zh-Hant'
    return ''


def locale_tag(conversion_type, input_locale, output_locale):
    """POSIX-style locale: zh_CN / zh_TW / zh_HK."""
    _script, region = _script_and_region(
        conversion_type, input_locale, output_locale)
    return _LOCALE_BY_REGION.get(region, '')


def short_script_tag(
        conversion_type, input_locale, output_locale, use_target_phrases=True):
    """BCP-47 script tag for Calibre languages / OPF (zh-Hans or zh-Hant)."""
    return bcp47_script_tag(conversion_type, input_locale, output_locale)


def english_filter_tokens(
        conversion_type, input_locale, output_locale, use_target_phrases=True):
    """English-side keys: BCP-47 script plus locale when the region is known."""
    tokens = []
    script = bcp47_script_tag(conversion_type, input_locale, output_locale)
    if script:
        tokens.append(script)
    locale = locale_tag(conversion_type, input_locale, output_locale)
    if locale and locale not in tokens:
        tokens.append(locale)
    return tokens


def metadata_language_codes(english_tag):
    """Calibre ``languages`` list for the converted book, or None to leave as-is."""
    tag = (english_tag or '').strip()
    if not tag:
        return None
    return [tag]
