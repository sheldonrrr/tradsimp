#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare OpenCC mmseg vs Jieba segmentation on phrase-sensitive samples.

Also asserts short_circuit identity phrases (e.g. 王后) are not overwritten
by STCharacters after nested group conversion.

Run from repo root:
  python3 scripts/check_segmentation_conversion.py
"""

from __future__ import print_function

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, 'resources'))

from resources.opencc_python.opencc import (  # noqa: E402
    CONFIG_FILE,
    DICT_FILE,
    OpenCC,
    SEGMENTATION_JIEBA,
    SEGMENTATION_MMSEG,
)

SAMPLES = [
    '慰藉着',
    '城堡的士兵',
    '软件鼠标',
    '服务器',
    '内存',
    '程序',
    '网络',
    '打印机',
    '默认',
]

# Identity / 歷曆 phrase protection must match official OpenCC short_circuit.
EXPECTED_PHRASES = (
    ('只是', '只是'),
    ('丑时', '丑時'),
    ('王后', '王后'),
    ('皇后', '皇后'),
    ('公里', '公里'),
    ('范公子', '范公子'),
    ('韩国瑜', '韓國瑜'),
    ('历史', '歷史'),
    ('日历', '日曆'),
    ('经历', '經歷'),
    ('中国历史上的王后', '中國歷史上的王后'),
)

MODES = ('s2t', 's2twp', 's2hkp')


def resource_getter(kind, name):
    if kind == CONFIG_FILE:
        path = os.path.join(REPO_ROOT, 'resources', 'opencc_python', 'config', name)
    elif kind == DICT_FILE:
        path = os.path.join(REPO_ROOT, 'resources', 'opencc_python', 'dictionary', name)
    else:
        raise ValueError(kind)
    with open(path, 'rb') as handle:
        return handle.read()


def check_expected_phrases():
    print('Expected phrase regression')
    failed = 0
    for mode in MODES:
        for seg_mode in (SEGMENTATION_MMSEG, SEGMENTATION_JIEBA):
            converter = OpenCC(resource_getter, mode)
            converter.set_segmentation_mode(seg_mode)
            for src, expect in EXPECTED_PHRASES:
                got = converter.convert(src)
                ok = got == expect
                marker = 'OK' if ok else 'FAIL'
                print('  [{} {}] {} -> {} [{}]{}'.format(
                    mode, seg_mode, src, got, marker,
                    '' if ok else ' expected {}'.format(expect)))
                if not ok:
                    failed += 1
    print('')
    return failed


def main():
    print('Segmentation conversion check')
    print('Repo:', REPO_ROOT)
    print('')
    failed = check_expected_phrases()
    for mode in MODES:
        mmseg = OpenCC(resource_getter, mode)
        mmseg.set_segmentation_mode(SEGMENTATION_MMSEG)
        jieba_cc = OpenCC(resource_getter, mode)
        jieba_cc.set_segmentation_mode(SEGMENTATION_JIEBA)
        print('=== {} ==='.format(mode))
        print('{:<12}  {:<24}  {}'.format('input', 'mmseg', 'jieba'))
        for sample in SAMPLES:
            left = mmseg.convert(sample)
            right = jieba_cc.convert(sample)
            marker = '' if left == right else ' *'
            print('{:<12}  {:<24}  {}{}'.format(sample, left, right, marker))
        print('')
    print('* marks rows where mmseg and jieba differ')
    if failed:
        print('FAILED: {} phrase assertion(s)'.format(failed))
        return 1
    print('All phrase assertions passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
