# -*- coding: utf-8 -*-

import difflib
import re
from html import escape as html_escape


BILINGUAL_MODE_FULL = 'full'
BILINGUAL_MODE_CHANGED = 'changed'
BILINGUAL_MODE_VALUES = (BILINGUAL_MODE_FULL, BILINGUAL_MODE_CHANGED)

BILINGUAL_STYLE_MARKER = 'ctc-bi-annotation-style'
BILINGUAL_STYLE_CSS = (
    '.ctc-bi{ruby-position:under;ruby-align:center}'
    '.ctc-bi-main{line-height:inherit}'
    '.ctc-bi-rt{font-size:.75em;line-height:1;color:inherit;opacity:.55;'
    'padding-bottom:0.55em}'
    '.ctc-bi-pair{display:inline-block;vertical-align:baseline;text-align:center;'
    'max-width:100%;word-break:keep-all}'
    '.ctc-bi-pair>.ctc-bi-main{display:block;line-height:inherit}'
    '.ctc-bi-pair>.ctc-bi-rt{display:block;font-size:.75em;line-height:1;'
    'color:inherit;opacity:.55;padding-bottom:0.15em;word-break:keep-all}'
)
BILINGUAL_STYLE_BLOCK = (
    '<style type="text/css" id="' + BILINGUAL_STYLE_MARKER + '">'
    + BILINGUAL_STYLE_CSS +
    '</style>'
)
BILINGUAL_BI_STYLE_CSS_TEXT = 'ruby-position:under;ruby-align:center'
BILINGUAL_MAIN_STYLE_CSS_TEXT = 'line-height:inherit'
BILINGUAL_RT_STYLE_CSS_TEXT = (
    'font-size:.75em;line-height:1;color:inherit;opacity:.55;'
    'padding-bottom:0.55em'
)
BILINGUAL_PAIR_STYLE_CSS_TEXT = (
    'display:inline-block;vertical-align:baseline;text-align:center;'
    'max-width:100%;word-break:keep-all'
)
BILINGUAL_PAIR_MAIN_STYLE_CSS_TEXT = 'display:block;line-height:inherit'
BILINGUAL_PAIR_RT_STYLE_CSS_TEXT = (
    'display:block;font-size:.75em;line-height:1;color:inherit;opacity:.55;'
    'padding-bottom:0.15em;word-break:keep-all'
)

_BILINGUAL_UNWRAP_RE = re.compile(
    r'<span\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*(?<=["\'\s])ctc-bi(?=["\'\s]))[^>]*>'
    r'(?:<span\b(?=[^>]*\bctc-bi-main\b)[^>]*>)?([^<]*)(?:</span>)?'
    r'<span\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*(?<=["\'\s])ctc-bi-rt(?=["\'\s]))[^>]*>'
    r'(.*?)'
    r'</span>\s*</span>',
    re.IGNORECASE | re.DOTALL,
)
_BILINGUAL_PAIR_UNWRAP_RE = re.compile(
    r'<span\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*(?<=["\'\s])ctc-bi-pair(?=["\'\s]))[^>]*>'
    r'<span\b(?=[^>]*\bctc-bi-main\b)[^>]*>.*?</span>\s*'
    r'<span\b(?=[^>]*\bctc-bi-rt\b)[^>]*>(.*?)</span>\s*'
    r'</span>',
    re.IGNORECASE | re.DOTALL,
)
_BILINGUAL_RUBY_UNWRAP_RE = re.compile(
    r'<ruby\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*(?<=[\"\'\s])ctc-bi(?=[\"\'\s]))[^>]*>'
    r'<rb\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*\bctc-bi-main\b)[^>]*>.*?</rb>'
    r'<rt\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*\bctc-bi-rt\b)[^>]*>(.*?)</rt>'
    r'\s*</ruby>',
    re.IGNORECASE | re.DOTALL,
)
_BILINGUAL_STYLE_BLOCK_RE = re.compile(
    r'<style\b[^>]*\bid\s*=\s*["\']'
    + re.escape(BILINGUAL_STYLE_MARKER)
    + r'["\'][^>]*>.*?</style>\s*',
    re.IGNORECASE | re.DOTALL,
)


def normalize_bilingual_mode(value):
    text = (value or BILINGUAL_MODE_FULL).strip().lower()
    if text in BILINGUAL_MODE_VALUES:
        return text
    return BILINGUAL_MODE_FULL


def strip_bilingual_annotations(html):
    """Restore original annotated text and remove plugin bilingual styles."""
    if not html or ('ctc-bi' not in html and BILINGUAL_STYLE_MARKER not in html):
        return html
    html = _BILINGUAL_STYLE_BLOCK_RE.sub('', html)
    previous = None
    while previous != html:
        previous = html
        html = _BILINGUAL_RUBY_UNWRAP_RE.sub(r'\1', html)
        html = _BILINGUAL_PAIR_UNWRAP_RE.sub(r'\1', html)
        html = _BILINGUAL_UNWRAP_RE.sub(r'\2', html)
    return html


def align_conversion_segments(original, converted):
    """Align original and converted strings into (source, target) segments."""
    if original == converted:
        return [(original, converted)]

    matcher = difflib.SequenceMatcher(None, original, converted, autojunk=False)
    segments = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ('equal', 'replace'):
            segments.append((original[i1:i2], converted[j1:j2]))
        elif tag == 'delete':
            segments.append((original[i1:i2], ''))
        elif tag == 'insert':
            inserted = converted[j1:j2]
            if segments:
                previous_source, previous_target = segments[-1]
                segments[-1] = (
                    previous_source, previous_target + inserted)
            else:
                segments.append(('', inserted))
    return segments


def _validated_conversion_segments(original, converted, spans):
    """Return source/target pairs from converter spans, or None if incomplete."""
    if not spans:
        return None
    expected_start = 0
    pairs = []
    for span in spans:
        start = span.get('source_start')
        end = span.get('source_end')
        source = span.get('source', '')
        target = span.get('target', '')
        if (start != expected_start or end is None or end < start
                or original[start:end] != source):
            return None
        pairs.append((source, target))
        expected_start = end
    if expected_start != len(original):
        return None
    if ''.join(target for _source, target in pairs) != converted:
        return None
    return pairs


def _ruby_annotation(target, source):
    return (
        '<ruby class="ctc-bi"><rb class="ctc-bi-main">{}</rb>'
        '<rt class="ctc-bi-rt">{}</rt></ruby>'.format(
            html_escape(target, quote=False),
            html_escape(source, quote=False)))


def _pair_annotation(target, source):
    """Length-mismatched phrase: stacked pair that wraps as one unit."""
    return (
        '<span class="ctc-bi ctc-bi-pair">'
        '<span class="ctc-bi-main">{}</span>'
        '<span class="ctc-bi-rt">{}</span>'
        '</span>'.format(
            html_escape(target, quote=False),
            html_escape(source, quote=False)))


def _annotated_segment(source, target):
    if len(source) == len(target):
        return _ruby_annotation(target, source)
    return _pair_annotation(target, source)


def format_bilingual_html(original, converted, spans=None, mode=BILINGUAL_MODE_FULL):
    """
    Render converted text with original forms below.

    mode=full: annotate every segment (including unchanged) so the second line
    is continuous original text.
    mode=changed: annotate only segments where source != target (gapped second line).
    Equal-length changes use ruby; unequal lengths use an inline-block pair.
    """
    mode = normalize_bilingual_mode(mode)
    if original == converted:
        return original

    converter_pairs = _validated_conversion_segments(original, converted, spans)
    if converter_pairs is None:
        converter_pairs = [(original, converted)]

    parts = []
    for source_pair, target_pair in converter_pairs:
        # Keep OpenCC phrase boundaries; never force fake 1:1 splits on
        # length-changing phrases (handled as one pair/ruby unit).
        for source, target in align_conversion_segments(source_pair, target_pair):
            if not source and not target:
                continue
            if source == target:
                if mode == BILINGUAL_MODE_FULL and source:
                    parts.append(_ruby_annotation(target, source))
                else:
                    parts.append(html_escape(source, quote=False))
            elif not source:
                parts.append(html_escape(target, quote=False))
            elif not target:
                parts.append(html_escape(source, quote=False))
            else:
                parts.append(_annotated_segment(source, target))
    return ''.join(parts)
