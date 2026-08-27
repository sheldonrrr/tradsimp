# -*- coding: utf-8 -*-
"""Identify Simplified vs Traditional Chinese in a text sample.

Classification follows hanzidentifier (MIT, https://github.com/tsroten/hanzidentifier):
UNKNOWN, BOTH, TRADITIONAL, SIMPLIFIED, MIXED.

Distinctive characters come from bundled OpenCC STCharacters.txt and
TSCharacters.txt (not zhon/CEDICT). Characters that appear on both the
simplified and traditional sides are treated as shared and ignored.
The remainder is counted: a clear majority of simplified-only or
traditional-only hits yields SIMPLIFIED / TRADITIONAL; otherwise MIXED.
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import re
import zipfile

UNKNOWN = 'unknown'
BOTH = 'both'
TRADITIONAL = 'traditional'
SIMPLIFIED = 'simplified'
MIXED = 'mixed'

HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'

_HTML_BLOCK_RE = re.compile(
    r'<(script|style)\b[^>]*>.*?</\1>', re.IGNORECASE | re.DOTALL)
_HTML_TAG_RE = re.compile(r'<[^>]+>')

_WRITING_MODE_PROP_RE = re.compile(
    r'(?:-webkit-|-epub-)?writing-mode\s*:\s*([a-z0-9-]+)',
    re.IGNORECASE)
_PRIMARY_WRITING_MODE_RE = re.compile(
    r'name\s*=\s*[\'"]primary-writing-mode[\'"][^>]*content\s*=\s*[\'"]([a-z0-9-]+)[\'"]'
    r'|content\s*=\s*[\'"]([a-z0-9-]+)[\'"][^>]*name\s*=\s*[\'"]primary-writing-mode[\'"]',
    re.IGNORECASE)

_VERTICAL_MODES = frozenset((
    'vertical-rl', 'vertical-lr',
    'tb-rl', 'tb-lr', 'bt-rl', 'bt-lr',
    'sideways-rl', 'sideways-lr',
))
_HORIZONTAL_MODES = frozenset((
    'horizontal-tb', 'horizontal-bt',
    'lr-tb', 'rl-tb', 'lr-bt', 'rl-bt',
))

_MAX_SAMPLE_FILES = 8
_MAX_CJK_CHARS = 8000

# Distinctive-char occurrence share needed to call Simplified or Traditional
# when both sides appear (3:1). Below this → MIXED.
_MAJORITY_SHARE = 0.75

_DISTINCT_SETS = None


def _is_cjk(char):
    code = ord(char)
    return (
        0x4E00 <= code <= 0x9FFF
        or 0x3400 <= code <= 0x4DBF
        or 0xF900 <= code <= 0xFAFF
    )


def _read_opencc_char_dict_bytes(file_name):
    raw = None
    try:
        raw = get_resources(  # noqa: F821 — injected by Calibre
            'resources/opencc_python/dictionary/' + file_name)
    except Exception:
        raw = None
    if raw:
        return raw
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'opencc_python', 'dictionary', file_name)
    try:
        with open(path, 'rb') as fh:
            return fh.read()
    except Exception:
        return None


def _iter_opencc_char_pairs(raw):
    if not raw:
        return
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8', 'replace')
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) < 2 or not parts[0]:
            continue
        targets = [item for item in parts[1].split() if item]
        if not targets:
            continue
        yield parts[0], targets


def _distinct_sets():
    """Simplified-only / traditional-only chars from OpenCC ST + TS tables.

    Shared glyphs (appear on both sides, including identity variants such as
    里 in 里→裏 里) are excluded. Only the remainder is used for identify().
    """
    global _DISTINCT_SETS
    if _DISTINCT_SETS is not None:
        return _DISTINCT_SETS
    simplified = set()
    traditional = set()
    for source, targets in _iter_opencc_char_pairs(
            _read_opencc_char_dict_bytes('STCharacters.txt')):
        simplified.add(source)
        traditional.update(targets)
    for source, targets in _iter_opencc_char_pairs(
            _read_opencc_char_dict_bytes('TSCharacters.txt')):
        traditional.add(source)
        simplified.update(targets)
    simp_only = frozenset(simplified - traditional)
    trad_only = frozenset(traditional - simplified)
    _DISTINCT_SETS = (simp_only, trad_only)
    return _DISTINCT_SETS


def identify(text):
    """Return UNKNOWN, BOTH, TRADITIONAL, SIMPLIFIED, or MIXED."""
    if not text:
        return UNKNOWN
    simp_only, trad_only = _distinct_sets()
    simp_hits = 0
    trad_hits = 0
    saw_cjk = False
    for char in text:
        if char in simp_only:
            simp_hits += 1
            saw_cjk = True
        elif char in trad_only:
            trad_hits += 1
            saw_cjk = True
        elif _is_cjk(char):
            saw_cjk = True
    total = simp_hits + trad_hits
    if total == 0:
        return BOTH if saw_cjk else UNKNOWN
    if simp_hits == 0:
        return TRADITIONAL
    if trad_hits == 0:
        return SIMPLIFIED
    if simp_hits / float(total) >= _MAJORITY_SHARE:
        return SIMPLIFIED
    if trad_hits / float(total) >= _MAJORITY_SHARE:
        return TRADITIONAL
    return MIXED


def strip_html_to_text(markup):
    if not markup:
        return ''
    text = _HTML_BLOCK_RE.sub(' ', markup)
    text = _HTML_TAG_RE.sub(' ', text)
    return text


def _classify_writing_mode_value(value):
    if not value:
        return None
    lowered = value.lower().strip()
    if lowered in _VERTICAL_MODES:
        return VERTICAL
    if lowered in _HORIZONTAL_MODES:
        return HORIZONTAL
    return None


def _scan_writing_mode_text(text):
    """Return (saw_vertical, saw_horizontal) from CSS/HTML/OPF markup."""
    saw_vertical = False
    saw_horizontal = False
    if not text:
        return saw_vertical, saw_horizontal
    values = []
    for match in _WRITING_MODE_PROP_RE.finditer(text):
        values.append(match.group(1))
    for match in _PRIMARY_WRITING_MODE_RE.finditer(text):
        values.append(match.group(1) or match.group(2))
    for value in values:
        kind = _classify_writing_mode_value(value)
        if kind == VERTICAL:
            saw_vertical = True
        elif kind == HORIZONTAL:
            saw_horizontal = True
        if saw_vertical and saw_horizontal:
            break
    return saw_vertical, saw_horizontal


def _resolve_writing_mode(saw_vertical, saw_horizontal):
    if saw_vertical and not saw_horizontal:
        return VERTICAL
    if saw_horizontal and not saw_vertical:
        return HORIZONTAL
    return None


def _book_member_names(zf):
    try:
        from calibre_plugins.chinese_text_conversion.resources.cjk_fonts import (
            _iter_epub_text_members)
    except ImportError:
        _iter_epub_text_members = None
    if _iter_epub_text_members is not None:
        names = list(_iter_epub_text_members(zf))
    else:
        names = [info.filename for info in zf.infolist()]
    seen = set(names)
    for info in zf.infolist():
        if info.filename.lower().endswith('.opf') and info.filename not in seen:
            names.append(info.filename)
            seen.add(info.filename)
    return names


def _scan_book_archive(book_path):
    """Read EPUB/AZW3 once. Return (html_sample, saw_vertical, saw_horizontal)."""
    if not book_path or not os.path.isfile(book_path):
        return '', False, False
    chunks = []
    cjk_count = 0
    files_used = 0
    saw_vertical = False
    saw_horizontal = False
    try:
        with zipfile.ZipFile(book_path, 'r') as zf:
            for name in _book_member_names(zf):
                lower = name.lower()
                is_markup = lower.endswith((
                    '.css', '.html', '.htm', '.xhtml', '.xml', '.opf'))
                is_html = lower.endswith(('.html', '.htm', '.xhtml'))
                if not is_markup:
                    continue
                try:
                    raw = zf.read(name)
                except Exception:
                    continue
                try:
                    markup = raw.decode('utf-8')
                except UnicodeDecodeError:
                    markup = raw.decode('utf-8', 'replace')
                if not (saw_vertical and saw_horizontal):
                    file_v, file_h = _scan_writing_mode_text(markup)
                    saw_vertical = saw_vertical or file_v
                    saw_horizontal = saw_horizontal or file_h
                if not is_html:
                    continue
                if files_used >= _MAX_SAMPLE_FILES or cjk_count >= _MAX_CJK_CHARS:
                    if saw_vertical and saw_horizontal:
                        break
                    continue
                piece = strip_html_to_text(markup)
                if not piece.strip():
                    continue
                chunks.append(piece)
                files_used += 1
                cjk_count += sum(1 for char in piece if _is_cjk(char))
    except Exception:
        return '', False, False
    return ' '.join(chunks), saw_vertical, saw_horizontal


def inspect_book(book_path):
    """Sample an EPUB/AZW3 once. Return (script_kind, writing_mode_kind).

    writing_mode_kind is HORIZONTAL, VERTICAL, or None when unclear.
    """
    text, saw_vertical, saw_horizontal = _scan_book_archive(book_path)
    return identify(text), _resolve_writing_mode(saw_vertical, saw_horizontal)


def sample_book_text(book_path):
    """Pull a short HTML text sample from an EPUB/AZW3 zip. Empty if unavailable."""
    text, _saw_vertical, _saw_horizontal = _scan_book_archive(book_path)
    return text


def identify_book(book_path):
    """Identify script from an EPUB/AZW3 sample. UNKNOWN when sampling fails."""
    script_kind, _writing_mode = inspect_book(book_path)
    return script_kind
