# -*- coding: utf-8 -*-
"""Lazy loader for vendored jieba used by optional OpenCC segmentation."""

from __future__ import print_function

import logging
import os
import pkgutil
import sys

JIEBA_VERSION = '0.42.1'
JIEBA_PACKAGE = 'calibre_plugins.chinese_text_conversion.resources.jieba'

# Relative paths under the vendored jieba package (and sibling files for extract).
_JIEBA_PACKAGE_FILES = (
    '__init__.py',
    '_compat.py',
    'dict.txt',
    'finalseg/__init__.py',
    'finalseg/prob_start.p',
    'finalseg/prob_trans.p',
    'finalseg/prob_emit.p',
)

_jieba_module = None
_jieba_failed = False


def _resources_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _bundled_jieba_dir():
    return os.path.join(_resources_dir(), 'jieba')


def _cache_root():
    try:
        from calibre.utils.config import config_dir
        base = config_dir
    except Exception:
        base = os.path.join(os.path.expanduser('~'), '.config', 'calibre')
    return os.path.join(base, 'plugins', 'chinese_text_conversion_jieba', JIEBA_VERSION)


def _read_package_bytes(rel_path):
    """
    Read a file from the vendored jieba package (zip-safe via pkgutil).
    Falls back to the filesystem copy under resources/jieba/.
    """
    normalized = rel_path.replace('\\', '/')
    data = pkgutil.get_data(JIEBA_PACKAGE, normalized)
    if data:
        return data

    fs_path = os.path.join(_bundled_jieba_dir(), *normalized.split('/'))
    if os.path.isfile(fs_path):
        with open(fs_path, 'rb') as handle:
            return handle.read()

    # Dev/script import without the calibre_plugins prefix
    data = pkgutil.get_data('resources.jieba', normalized)
    if data:
        return data
    data = pkgutil.get_data('jieba', normalized)
    if data:
        return data

    raise IOError('unable to read bundled jieba file: %s' % rel_path)


def _ensure_cache():
    cache_dir = _cache_root()
    marker = os.path.join(cache_dir, '.ready')
    dict_path = os.path.join(cache_dir, 'jieba', 'dict.txt')
    if os.path.isfile(marker) and os.path.isfile(dict_path):
        return cache_dir

    for rel in _JIEBA_PACKAGE_FILES:
        target = os.path.join(cache_dir, 'jieba', *rel.split('/'))
        parent = os.path.dirname(target)
        if not os.path.isdir(parent):
            os.makedirs(parent)
        with open(target, 'wb') as handle:
            handle.write(_read_package_bytes(rel))

    with open(marker, 'w') as handle:
        handle.write(JIEBA_VERSION)
    return cache_dir


def _import_jieba_from(parent_dir):
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    for name in list(sys.modules):
        if name == 'jieba' or name.startswith('jieba.'):
            del sys.modules[name]
    import jieba
    return jieba


def get_jieba():
    """
    Return an initialized jieba module, or raise on failure.
    Safe to call repeatedly; initializes once.
    """
    global _jieba_module, _jieba_failed
    if _jieba_module is not None:
        return _jieba_module
    if _jieba_failed:
        raise RuntimeError('jieba previously failed to initialize')

    try:
        bundled = _bundled_jieba_dir()
        # Prefer a real filesystem tree (dev checkout).
        if os.path.isfile(os.path.join(bundled, 'dict.txt')):
            jieba = _import_jieba_from(_resources_dir())
        else:
            # Calibre zip plugin: extract to cache then import as top-level jieba.
            cache_dir = _ensure_cache()
            jieba = _import_jieba_from(cache_dir)

        try:
            jieba.setLogLevel(logging.WARNING)
        except Exception:
            pass

        dict_path = os.path.join(os.path.dirname(jieba.__file__), 'dict.txt')
        if os.path.isfile(dict_path):
            jieba.set_dictionary(dict_path)
        jieba.initialize()
        _jieba_module = jieba
        return jieba
    except Exception:
        _jieba_failed = True
        raise
