#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression checks for source-aligned conversion and bilingual ruby output."""

from __future__ import print_function

import os
import sys
from html.parser import HTMLParser
from zipfile import ZipFile

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
    SEGMENTATION_JIEBA,
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


class _TextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_data(self, data):
        if data.strip():
            self.items.append(data.strip())


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

    # Coverage-first mode uses only existing OpenCC reverse/forward configs.
    forced = OpenCC(resource_getter, 's2twp')
    forced.set_segmentation_mode(SEGMENTATION_JIEBA)
    forced.set_force_pivot_conversion(True)
    mixed = '皇后 \t皇後 \t皇后；公里 \t公裡 \t公里'
    mixed_converted, mixed_spans = forced.convert_with_details(mixed)
    assert_equal(
        mixed_converted,
        '皇后 \t皇后 \t皇后；公里 \t公里 \t公里',
        'forced pivot mixed-script normalization')
    mixed_ruby = format_bilingual_html(
        mixed, mixed_converted, mixed_spans)
    if ('<rb class="ctc-bi-main">后</rb>'
            '<rt class="ctc-bi-rt">後</rt>' not in mixed_ruby):
        raise AssertionError(
            'forced pivot did not preserve 皇後 source: ' + mixed_ruby)
    if ('<rb class="ctc-bi-main">里</rb>'
            '<rt class="ctc-bi-rt">裡</rt>' not in mixed_ruby):
        raise AssertionError(
            'forced pivot did not preserve 公裡 source: ' + mixed_ruby)
    assert_equal(
        strip_bilingual_annotations('<p>' + mixed_ruby + '</p>'),
        '<p>' + mixed + '</p>',
        'forced pivot re-conversion must restore real source')

    # The mode is intentionally coverage-first: valid regional wording can move.
    regional, regional_spans = forced.convert_with_details('搜尋欄位')
    assert_equal(regional, '搜尋字段', 'documented pivot regional side effect')
    regional_ruby = format_bilingual_html(
        '搜尋欄位', regional, regional_spans)
    if '<rt class="ctc-bi-rt">欄位</rt>' not in regional_ruby:
        raise AssertionError(
            'pivot side effect source not visible in ruby: ' + regional_ruby)

    # Length-changing target phrases must use a safe whole-context fallback.
    expanded, expanded_spans = forced.convert_with_details('内存')
    assert_equal(expanded, '記憶體', 'forced pivot length-changing phrase')
    assert_equal(len(expanded_spans), 1, 'length-changing fallback span')
    assert_equal(
        format_bilingual_html('内存', expanded, expanded_spans),
        '<ruby class="ctc-bi"><rb class="ctc-bi-main">記憶體</rb>'
        '<rt class="ctc-bi-rt">内存</rt></ruby>',
        'length-changing fallback ruby')

    forced.set_force_pivot_conversion(False)
    assert_equal(
        forced.convert('皇後 公裡'),
        '皇後 公裡',
        'disabled pivot preserves direct OpenCC behavior')

    # Exercise the repository's mixed-script EPUB fixture end to end in memory.
    fixture = os.path.join(
        REPO_ROOT, 'testdata', 'Test (2026) - 简繁.epub')
    collector = _TextCollector()
    with ZipFile(fixture) as archive:
        for name in archive.namelist():
            if name.lower().endswith(('.xhtml', '.html', '.htm')):
                collector.feed(
                    archive.read(name).decode('utf-8', errors='replace'))
    fixture_converter = OpenCC(resource_getter, 's2twp')
    fixture_converter.set_segmentation_mode(SEGMENTATION_JIEBA)
    fixture_converter.set_force_pivot_conversion(True)
    fixture_cases = {
        '只是 \t隻是 \t只是/衹是': '只是 \t只是 \t只是/衹是',
        '丑时 \t醜時 \t丑時': '丑時 \t丑時 \t丑時',
        '皇后 \t皇後 \t皇后': '皇后 \t皇后 \t皇后',
        '公里 \t公裡 \t公里': '公里 \t公里 \t公里',
        # Upstream OpenCC does not know that 范 is a surname here.
        '范公子 \t範公子 \t范公子': '範公子 \t範公子 \t範公子',
        # 南韓 is valid regional wording; no private name override is used.
        '韩国瑜 \t南韓瑜\t韓國瑜': '韓國瑜 \t南韓瑜\t韓國瑜',
    }
    for source, expected in fixture_cases.items():
        if source not in collector.items:
            raise AssertionError('fixture row not found: ' + source)
        assert_equal(
            fixture_converter.convert(source), expected,
            'fixture forced pivot: ' + source)

    print('Bilingual conversion assertions passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
