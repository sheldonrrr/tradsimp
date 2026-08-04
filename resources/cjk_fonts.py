# -*- coding: utf-8 -*-
"""CJK font strategy: detect book fonts and unify body text to Serif/Sans stacks."""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import platform
import re
import zipfile

from calibre.ebooks.oeb.polish.container import OEB_DOCS, OEB_STYLES

from calibre_plugins.chinese_text_conversion.i18n import _

# Keep in sync with main.OUTPUT_LOCALE (avoid importing main here).
_OUTPUT_LOCALE_INDEX = 3

CJK_FONT_POLICY_KEEP = 'keep'
CJK_FONT_POLICY_SERIF = 'serif'
CJK_FONT_POLICY_SANS = 'sans'
CJK_FONT_POLICY_VALUES = (
    CJK_FONT_POLICY_KEEP,
    CJK_FONT_POLICY_SERIF,
    CJK_FONT_POLICY_SANS,
)

CJK_FONT_STYLE_MARKER = 'ctc-cjk-font-style'
CJK_FONT_RULE_SELECTOR = u'body.calibre-chinese_text, body.calibre-chinese_text *'

_FONT_FAMILY_DECL_RE = re.compile(
    r'font-family\s*:\s*([^;}{]+)', re.IGNORECASE)
_AT_FONT_FACE_RE = re.compile(
    r'@font-face\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
    re.IGNORECASE | re.DOTALL)
_SRC_URL_RE = re.compile(
    r'src\s*:[^;]*url\s*\(\s*[\'"]?(?!https?:|data:)([^\'")\s]+)',
    re.IGNORECASE)
_STYLE_BLOCK_RE = re.compile(
    r'<style\b[^>]*>(.*?)</style>', re.IGNORECASE | re.DOTALL)

# Names commonly used for Simplified-only or Mainland Song/Hei embeds.
_SIMPLIFIED_EMBEDDED_HINTS = (
    '宋体', '宋體', 'simsun', 'nsimsun', '新宋体', '新宋體',
    '仿宋', 'fangsong', '楷体', '楷體', 'kaiti',
    '黑体', '黑體', 'simhei', '微软雅黑', '微軟雅黑', 'microsoft yahei',
    '华文宋体', '華文宋體', '华文黑体', '華文黑體', '华文楷体', '華文楷體',
    '方正', '汉仪', '漢儀', '华康', '華康',
)

_GENERIC_FAMILIES = frozenset({
    'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy',
    'system-ui', 'ui-serif', 'ui-sans-serif', 'ui-monospace',
    'emoji', 'math', 'fangsong', 'inherit', 'initial', 'unset',
})

_WIN_SERIF = ('SimSun', 'NSimSun', 'STSong', 'SimSun-ExtB')
_MAC_SERIF = ('Songti SC', 'Songti TC', 'STSong', 'LiSong Pro')
_LINUX_SERIF = (
    'Noto Serif CJK SC', 'Noto Serif CJK TC', 'Noto Serif CJK HK',
    'Source Han Serif SC', 'Source Han Serif TC', 'AR PL UMing CN',
)

_WIN_SANS = ('Microsoft YaHei', 'SimHei', 'Microsoft JhengHei', 'DengXian')
_MAC_SANS = ('PingFang SC', 'PingFang TC', 'Heiti SC', 'Heiti TC', 'STHeiti')
_LINUX_SANS = (
    'Noto Sans CJK SC', 'Noto Sans CJK TC', 'Noto Sans CJK HK',
    'Source Han Sans SC', 'Source Han Sans TC', 'WenQuanYi Micro Hei',
)

_CJK_FONT_STYLE_BLOCK_RE = re.compile(
    r'(?is)<style\b[^>]*\bid\s*=\s*[\'"]'
    + re.escape(CJK_FONT_STYLE_MARKER)
    + r'[\'"][^>]*>.*?</style>\s*')


def normalize_cjk_font_policy(value):
    text = (value or CJK_FONT_POLICY_KEEP).strip().lower()
    if text in CJK_FONT_POLICY_VALUES:
        return text
    return CJK_FONT_POLICY_KEEP


def _host_os_key():
    system = platform.system().lower()
    if system.startswith('darwin'):
        return 'mac'
    if system.startswith('win'):
        return 'win'
    return 'linux'


def _ordered_unique(names):
    seen = set()
    out = []
    for name in names:
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(name)
    return out


def _locale_boosted(names, output_locale):
    """Prefer TC/HK variants when converting to Traditional regions."""
    if output_locale == 1:  # Hong Kong
        prefer = ('HK', 'TC', 'HK')
    elif output_locale == 2:  # Taiwan
        prefer = ('TC', 'HK')
    else:
        prefer = ('SC',)
    preferred = []
    rest = []
    for name in names:
        upper = name.upper()
        if any(token in upper for token in prefer):
            preferred.append(name)
        else:
            rest.append(name)
    return preferred + rest


def build_cjk_font_stack(policy, output_locale=0):
    """
    Return a CSS font-family value with host-OS fonts first, then other
    platforms, ending in serif or sans-serif.
    """
    policy = normalize_cjk_font_policy(policy)
    if policy == CJK_FONT_POLICY_KEEP:
        return ''
    host = _host_os_key()
    if policy == CJK_FONT_POLICY_SERIF:
        by_os = {'win': _WIN_SERIF, 'mac': _MAC_SERIF, 'linux': _LINUX_SERIF}
        generic = 'serif'
    else:
        by_os = {'win': _WIN_SANS, 'mac': _MAC_SANS, 'linux': _LINUX_SANS}
        generic = 'sans-serif'
    order = [host] + [k for k in ('win', 'mac', 'linux') if k != host]
    names = []
    for key in order:
        names.extend(_locale_boosted(by_os[key], output_locale))
    names = _ordered_unique(names)
    quoted = []
    for name in names:
        needs_quotes = (' ' in name) or any(ord(ch) > 127 for ch in name)
        if needs_quotes:
            quoted.append('"{}"'.format(name.replace('"', '\\"')))
        else:
            quoted.append(name)
    quoted.append(generic)
    return ', '.join(quoted)


def cjk_font_css_text(policy, output_locale=0):
    stack = build_cjk_font_stack(policy, output_locale=output_locale)
    if not stack:
        return ''
    return 'font-family:{} !important'.format(stack)


def cjk_font_style_block(policy, output_locale=0):
    css_text = cjk_font_css_text(policy, output_locale=output_locale)
    if not css_text:
        return ''
    return (
        '<style type="text/css" id="' + CJK_FONT_STYLE_MARKER + '">'
        + CJK_FONT_RULE_SELECTOR + '{' + css_text + '}'
        + '</style>'
    )


def strip_cjk_font_style_blocks(html):
    if not html or CJK_FONT_STYLE_MARKER not in html:
        return html
    return _CJK_FONT_STYLE_BLOCK_RE.sub('', html)


def _split_font_families(value):
    families = []
    for part in re.split(r'\s*,\s*', value or ''):
        name = part.strip().strip('"\'').strip()
        if not name:
            continue
        if name.lower() in _GENERIC_FAMILIES:
            continue
        families.append(name)
    return families


def _looks_simplified_embedded_name(name):
    lowered = name.lower()
    for hint in _SIMPLIFIED_EMBEDDED_HINTS:
        if hint.lower() in lowered or hint in name:
            return True
    return False


def _collect_from_css_text(css_text, families, embedded_families):
    if not css_text:
        return
    for face_match in _AT_FONT_FACE_RE.finditer(css_text):
        body = face_match.group(1)
        has_local_url = bool(_SRC_URL_RE.search(body))
        for decl in _FONT_FAMILY_DECL_RE.finditer(body):
            for name in _split_font_families(decl.group(1)):
                families.add(name)
                if has_local_url:
                    embedded_families.add(name)
    # Non-@font-face font-family usages
    without_faces = _AT_FONT_FACE_RE.sub('', css_text)
    for decl in _FONT_FAMILY_DECL_RE.finditer(without_faces):
        for name in _split_font_families(decl.group(1)):
            families.add(name)


def _iter_epub_text_members(zf):
    for info in zf.infolist():
        name = info.filename
        lower = name.lower()
        if lower.endswith(('.css', '.html', '.htm', '.xhtml', '.xml')):
            yield name


def scan_book_fonts_from_path(book_path):
    """
    Scan an EPUB/AZW3 (ZIP) for font-family names and embedded @font-face fonts.
    Returns dict: families (list), embedded_families (list), has_embedded (bool).
    """
    families = set()
    embedded_families = set()
    if not book_path or not os.path.isfile(book_path):
        return {
            'families': [],
            'embedded_families': [],
            'has_embedded': False,
        }
    try:
        with zipfile.ZipFile(book_path, 'r') as zf:
            members = list(_iter_epub_text_members(zf))
            for name in members:
                try:
                    raw = zf.read(name)
                except Exception:
                    continue
                try:
                    text = raw.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        text = raw.decode('utf-8', 'replace')
                    except Exception:
                        continue
                lower = name.lower()
                if lower.endswith('.css'):
                    _collect_from_css_text(text, families, embedded_families)
                else:
                    for style_match in _STYLE_BLOCK_RE.finditer(text):
                        _collect_from_css_text(
                            style_match.group(1), families, embedded_families)
    except Exception:
        return {
            'families': [],
            'embedded_families': [],
            'has_embedded': False,
        }
    return {
        'families': sorted(families, key=lambda s: s.lower()),
        'embedded_families': sorted(embedded_families, key=lambda s: s.lower()),
        'has_embedded': bool(embedded_families),
    }


def scan_book_fonts_from_container(container):
    """Scan an open Calibre polish container for font families."""
    families = set()
    embedded_families = set()
    try:
        for name, mt in container.mime_map.items():
            if mt in OEB_STYLES:
                try:
                    raw = container.raw_data(name)
                except Exception:
                    continue
                _collect_from_css_text(raw, families, embedded_families)
            elif mt in OEB_DOCS:
                try:
                    raw = container.raw_data(name)
                except Exception:
                    continue
                for style_match in _STYLE_BLOCK_RE.finditer(raw):
                    _collect_from_css_text(
                        style_match.group(1), families, embedded_families)
    except Exception:
        pass
    return {
        'families': sorted(families, key=lambda s: s.lower()),
        'embedded_families': sorted(embedded_families, key=lambda s: s.lower()),
        'has_embedded': bool(embedded_families),
    }


def format_cjk_font_policy_help(scan_info, policy=CJK_FONT_POLICY_KEEP):
    """
    Build help text for the CJK font policy control.
    scan_info: result of scan_book_fonts_from_path / from_container (or None).
    """
    policy = normalize_cjk_font_policy(policy)
    families = list((scan_info or {}).get('families') or [])
    embedded = list((scan_info or {}).get('embedded_families') or [])
    has_embedded = bool((scan_info or {}).get('has_embedded'))

    if families:
        shown = ', '.join(families[:8])
        if len(families) > 8:
            shown += ', …'
        current_line = _('Current fonts: {0}').format(shown)
    else:
        current_line = _(
            'No specific fonts detected; the reader’s default fonts will be used.')

    if policy == CJK_FONT_POLICY_SERIF:
        return '\n'.join([
            current_line,
            _('CJK font policy serif help'),
        ])
    if policy == CJK_FONT_POLICY_SANS:
        return '\n'.join([
            current_line,
            _('CJK font policy sans help'),
        ])

    # keep
    lines = [current_line]
    if has_embedded:
        simp_names = [n for n in embedded if _looks_simplified_embedded_name(n)]
        if simp_names:
            example = simp_names[0]
            lines.append(
                _('CJK embedded simplified font warning').format(example))
        else:
            lines.append(_('CJK embedded font general warning'))
    return '\n'.join(lines)


def apply_cjk_font_policy(container, criteria, changed_files, policy_index):
    """
    Write unified font-family rules into stylesheets when policy is serif/sans.
    Returns True if any stylesheet changed.
    """
    if criteria is None or len(criteria) <= policy_index:
        return False
    policy = normalize_cjk_font_policy(criteria[policy_index])
    if policy == CJK_FONT_POLICY_KEEP:
        return False

    from css_parser import css

    output_locale = (
        criteria[_OUTPUT_LOCALE_INDEX]
        if len(criteria) > _OUTPUT_LOCALE_INDEX else 0)
    css_text = cjk_font_css_text(policy, output_locale=output_locale)
    if not css_text:
        return False

    file_changed = False
    style_sheets = [
        name for name, mt in container.mime_map.items() if mt in OEB_STYLES]
    for name in style_sheets:
        sheet = container.parsed(name)
        rule = None
        for existing in sheet:
            if existing.type != existing.STYLE_RULE:
                continue
            selector_text = ','.join(
                sel.selectorText for sel in existing.selectorList)
            if _normalize_selector(selector_text) == _normalize_selector(
                    CJK_FONT_RULE_SELECTOR):
                rule = existing
                break
        if rule is None:
            style = css.CSSStyleDeclaration()
            style.cssText = css_text
            sheet.add(css.CSSStyleRule(
                selectorText=CJK_FONT_RULE_SELECTOR, style=style))
            sheet_changed = True
        else:
            if _normalize_css(rule.style.cssText) == _normalize_css(css_text):
                sheet_changed = False
            else:
                rule.style.cssText = css_text
                sheet_changed = True
        if not sheet_changed:
            continue
        file_changed = True
        if name not in changed_files:
            changed_files.append(name)
        container.dirty(name)
    return file_changed


def _normalize_css(css_text):
    return ''.join(str(css_text or '').split())


def _normalize_selector(selector_text):
    return ''.join(str(selector_text or '').split())
