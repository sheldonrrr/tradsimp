# -*- coding: utf-8 -*-
"""Lazy loader for vendored MediaWiki zhconv (gumblex/zhconv)."""

from __future__ import print_function

import json
import os
import sys

ZHCONV_VERSION = '1.4.3'
ZHCONV_PACKAGE = 'calibre_plugins.chinese_text_conversion.resources.zhconv'

_zhconv_module = None
_zhconv_failed = False


def _resources_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _bundled_zhconv_dir():
    return os.path.join(_resources_dir(), 'zhconv')


def _read_dict_bytes():
    """Read zhcdict.json from the plugin zip or filesystem (zip-safe)."""
    try:
        data = get_resources('resources/zhconv/zhcdict.json')  # noqa: F821
    except Exception:
        data = None
    if data:
        return data

    try:
        import pkgutil
        data = pkgutil.get_data(ZHCONV_PACKAGE, 'zhcdict.json')
    except Exception:
        data = None
    if data:
        return data

    fs_path = os.path.join(_bundled_zhconv_dir(), 'zhcdict.json')
    if os.path.isfile(fs_path):
        with open(fs_path, 'rb') as handle:
            return handle.read()
    return None


def _ensure_import_path():
    bundled = _bundled_zhconv_dir()
    parent = _resources_dir()
    # Prefer package import via calibre_plugins...resources.zhconv when installed.
    # For scripts / unit tests, allow resources/ on sys.path.
    if parent not in sys.path:
        sys.path.insert(0, parent)
    return bundled


def _inject_dictionary(module):
    """Load MediaWiki tables without relying on pkg_resources in a plugin zip."""
    if getattr(module, 'zhcdicts', None) is not None:
        return True
    raw = _read_dict_bytes()
    if not raw:
        return False
    zhcdicts = json.loads(raw.decode('utf-8'))
    zhcdicts['SIMPONLY'] = frozenset(zhcdicts['SIMPONLY'])
    zhcdicts['TRADONLY'] = frozenset(zhcdicts['TRADONLY'])
    module.zhcdicts = zhcdicts
    return True


def get_zhconv():
    """
    Return the vendored zhconv.zhconv module, or None if unavailable.
    Loads conversion tables via get_resources when running inside Calibre.
    """
    global _zhconv_module, _zhconv_failed
    if _zhconv_module is not None:
        return _zhconv_module
    if _zhconv_failed:
        return None

    try:
        _ensure_import_path()
        try:
            from calibre_plugins.chinese_text_conversion.resources.zhconv import (
                zhconv as module)
        except Exception:
            from zhconv import zhconv as module  # resources/ on sys.path
        if not _inject_dictionary(module):
            raise RuntimeError('zhcdict.json missing from plugin resources')
        _zhconv_module = module
        return _zhconv_module
    except Exception:
        _zhconv_failed = True
        return None


def convert_text(text, locale):
    """Convert text to a MediaWiki locale tag, or return text unchanged on failure."""
    if text is None or locale is None:
        return text
    module = get_zhconv()
    if module is None:
        return text
    try:
        return module.convert(text, locale)
    except Exception:
        return text


def is_available():
    return get_zhconv() is not None
