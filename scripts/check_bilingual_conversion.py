#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression checks for source-aligned conversion and bilingual ruby output."""

from __future__ import print_function

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from resources.bilingual import (  # noqa: E402
    BILINGUAL_STYLE_BLOCK,
    format_bilingual_html,
    strip_bilingual_annotations,
)
from resources.opencc_python.opencc import (  # noqa: E402
    CONFIG_FILE,
    DICT_FILE,
    OpenCC,
)


def resource_getter(kind, name):
    folder = 'config' if kind == CONFIG_FILE else 'dictionary'
    path = os.path.join(
        REPO_ROOT, 'resources', 'opencc_python', folder, name)
    with open(path, 'rb') as handle:
        return handle.read()


def assert_equal(actual, expected, label):
    if actual != expected:
        raise AssertionError(
            '{}\nexpected: {!r}\nactual:   {!r}'.format(
                label, expected, actual))


def main():
    converter = OpenCC(resource_getter, 's2twp')

    converted, spans = converter.convert_with_details('丑时')
    assert_equal(converted, '丑時', 'phrase conversion')
    ruby = format_bilingual_html('丑时', converted, spans)
    assert_equal(
        ruby,
        '丑<ruby class="ctc-bi"><rb class="ctc-bi-main">時</rb>'
        '<rt class="ctc-bi-rt">时</rt></ruby>',
        'upper Traditional / lower source Simplified')

    unchanged, unchanged_spans = converter.convert_with_details('皇后公里只是')
    assert_equal(unchanged, '皇后公里只是', 'identity phrase protection')
    assert_equal(
        format_bilingual_html(
            '皇后公里只是', unchanged, unchanged_spans),
        '皇后公里只是',
        'unchanged text must not receive ruby')

    escaped, escaped_spans = converter.convert_with_details('发&')
    escaped_ruby = format_bilingual_html('发&', escaped, escaped_spans)
    if '&amp;' not in escaped_ruby or '<rt class="ctc-bi-rt">发</rt>' not in escaped_ruby:
        raise AssertionError('bilingual HTML escaping failed: ' + escaped_ruby)

    document = BILINGUAL_STYLE_BLOCK + '<p>' + ruby + '</p>'
    assert_equal(
        strip_bilingual_annotations(document),
        '<p>丑时</p>',
        're-conversion must restore original Simplified text')

    converter.clear_replacement_counts()
    assert_equal(converter.convert('丑時'), '醜時', 'mixed-input diagnostic case')
    diagnostics = converter.get_conversion_diagnostics()
    kinds = {key[0] for key in diagnostics['counts']}
    if 'traditional_input_in_simplified_mode' not in kinds:
        raise AssertionError('traditional-only input was not diagnosed')
    if 'ambiguous_character_fallback' not in kinds:
        raise AssertionError('ambiguous character fallback was not diagnosed')

    converter.clear_replacement_counts()
    assert_equal(converter.convert('范公子'), '范公子', 'plugin override')
    if converter.get_conversion_diagnostics()['counts']:
        raise AssertionError('protected plugin phrase emitted a diagnostic')

    print('Bilingual conversion assertions passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
