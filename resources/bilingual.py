# -*- coding: utf-8 -*-

import difflib
import re
from html import escape as html_escape


BILINGUAL_STYLE_MARKER = 'ctc-bi-annotation-style'
BILINGUAL_STYLE_CSS = (
    '.ctc-bi{ruby-position:under;ruby-align:end}'
    '.ctc-bi-main{line-height:inherit}'
    '.ctc-bi-rt{font-size:.75em;line-height:1;color:inherit;opacity:.55;'
    'white-space:nowrap;padding-bottom:0.55em}'
)
BILINGUAL_STYLE_BLOCK = (
    '<style type="text/css" id="' + BILINGUAL_STYLE_MARKER + '">'
    + BILINGUAL_STYLE_CSS +
    '</style>'
)
BILINGUAL_BI_STYLE_CSS_TEXT = 'ruby-position:under;ruby-align:end'
BILINGUAL_MAIN_STYLE_CSS_TEXT = 'line-height:inherit'
BILINGUAL_RT_STYLE_CSS_TEXT = (
    'font-size:.75em;line-height:1;color:inherit;opacity:.55;'
    'white-space:nowrap;padding-bottom:0.55em'
)

_BILINGUAL_UNWRAP_RE = re.compile(
    r'<span\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*(?<=["\'\s])ctc-bi(?=["\'\s]))[^>]*>'
    r'(?:<span\b(?=[^>]*\bctc-bi-main\b)[^>]*>)?([^<]*)(?:</span>)?'
    r'<span\b(?=[^>]*\bclass\s*=\s*["\'][^"\']*(?<=["\'\s])ctc-bi-rt(?=["\'\s]))[^>]*>'
    r'(.*?)'
    r'</span>\s*</span>',
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


def strip_bilingual_annotations(html):
    """Restore original <rt> text and remove plugin bilingual styles."""
    if not html or ('ctc-bi' not in html and BILINGUAL_STYLE_MARKER not in html):
        return html
    html = _BILINGUAL_STYLE_BLOCK_RE.sub('', html)
    previous = None
    while previous != html:
        previous = html
        html = _BILINGUAL_RUBY_UNWRAP_RE.sub(r'\1', html)
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


def format_bilingual_html(original, converted, spans=None):
    """Render converted text above changed source fragments using ruby markup."""
    if original == converted:
        return original

    converter_pairs = _validated_conversion_segments(original, converted, spans)
    if converter_pairs is None:
        converter_pairs = [(original, converted)]

    parts = []
    for source_pair, target_pair in converter_pairs:
        # Keep OpenCC phrase boundaries for correctness, then leave equal
        # sub-runs unannotated so only changed characters receive an <rt>.
        for source, target in align_conversion_segments(source_pair, target_pair):
            if not source and not target:
                continue
            if source == target:
                parts.append(html_escape(source, quote=False))
            elif not source:
                parts.append(html_escape(target, quote=False))
            elif not target:
                parts.append(html_escape(source, quote=False))
            else:
                parts.append(
                    '<ruby class="ctc-bi"><rb class="ctc-bi-main">{}</rb>'
                    '<rt class="ctc-bi-rt">{}</rt></ruby>'.format(
                        html_escape(target, quote=False),
                        html_escape(source, quote=False)))
    return ''.join(parts)
