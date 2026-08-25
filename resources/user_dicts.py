# -*- coding: utf-8 -*-
"""Copy-on-write local OpenCC dictionaries in the Calibre config directory."""

from __future__ import print_function

import os
import re

USER_PHRASES_FILE = 'UserPhrases.txt'
PLUGIN_DICT_SUBDIR = ('plugins', 'chinese_text_conversion', 'dictionaries')

# Files the dictionary manager lists. UserPhrases.txt is a local overlay only.
MANAGED_DICT_FILES = (
    USER_PHRASES_FILE,
    'STPhrases.txt',
    'STPhrases_GeneratedFromRegionalPhrases.txt',
    'STCharacters.txt',
    'TSPhrases.txt',
    'TSCharacters.txt',
    'TSCharactersExt.txt',
    'TWPhrases.txt',
    'TWPhrasesRev.txt',
    'TWVariants.txt',
    'TWVariantsPhrases.txt',
    'TWVariantsRev.txt',
    'TWVariantsRevPhrases.txt',
    'HKPhrases.txt',
    'HKPhrasesRev.txt',
    'HKVariants.txt',
    'HKVariantsPhrases.txt',
    'HKVariantsRev.txt',
    'HKVariantsRevPhrases.txt',
    'JPShinjitaiCharacters.txt',
    'JPShinjitaiPhrases.txt',
    'JPShinjitaiCharactersRev.txt',
    'CJK_Compatibility_Ideographs.txt',
)

USER_PHRASES_TEMPLATE = (
    '# Open Chinese Convert (OpenCC) Dictionary\n'
    '# File: UserPhrases.txt\n'
    '# Format: key\tvalue(s) (values separated by spaces)\n'
    '# Local overlay: highest priority in conversion and segmentation.\n'
    '# This file is not bundled with OpenCC; Restore bundled deletes it.\n'
    '# Prefer this file for small additions instead of copying STPhrases.txt.\n'
    '#\n'
    '# Example:\n'
    '# 服务器\t伺服器\n'
)

_PIN_RE = re.compile(r'commit ([0-9a-f]+) \(([^)]+)\)')
_FALLBACK_COMMIT = '025f371'
_FALLBACK_TAG = 'ver.1.4.2'


def _config_dir():
    try:
        from calibre.utils.config import config_dir
        return config_dir
    except Exception:
        return os.path.join(os.path.expanduser('~'), '.config', 'calibre')


def _plugin_bundled_dict_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'opencc_python', 'dictionary')


def safe_dict_name(file_name):
    name = os.path.basename(file_name or '')
    if (not name or name != file_name or not name.endswith('.txt')
            or '/' in file_name or '\\' in file_name):
        raise ValueError('invalid dictionary file name')
    return name


def user_dict_dir():
    return os.path.join(_config_dir(), *PLUGIN_DICT_SUBDIR)


def ensure_user_dict_dir():
    path = user_dict_dir()
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def user_dict_path(file_name):
    return os.path.join(user_dict_dir(), safe_dict_name(file_name))


def is_overridden(file_name):
    try:
        path = user_dict_path(file_name)
    except ValueError:
        return False
    return os.path.isfile(path)


def read_user_dict_bytes(file_name):
    """Return local override bytes, or None if that file is not overridden."""
    try:
        path = user_dict_path(file_name)
    except ValueError:
        return None
    if not os.path.isfile(path):
        return None
    with open(path, 'rb') as handle:
        return handle.read()


def _read_bundled_via_get_resources(file_name):
    try:
        data = get_resources(  # noqa: F821 — injected by Calibre
            'resources/opencc_python/dictionary/' + file_name)
    except Exception:
        data = None
    return data or None


def read_bundled_dict_bytes(file_name):
    name = safe_dict_name(file_name)
    data = _read_bundled_via_get_resources(name)
    if data:
        return data
    fs_path = os.path.join(_plugin_bundled_dict_dir(), name)
    if os.path.isfile(fs_path):
        with open(fs_path, 'rb') as handle:
            return handle.read()
    return None


def read_effective_dict_bytes(file_name):
    user_bytes = read_user_dict_bytes(file_name)
    if user_bytes is not None:
        return user_bytes
    if file_name == USER_PHRASES_FILE:
        return USER_PHRASES_TEMPLATE.encode('utf-8')
    return read_bundled_dict_bytes(file_name)


def read_effective_dict_text(file_name):
    data = read_effective_dict_bytes(file_name)
    if data is None:
        return ''
    return data.decode('utf-8', errors='replace')


def save_override(file_name, text):
    name = safe_dict_name(file_name)
    directory = ensure_user_dict_dir()
    path = os.path.join(directory, name)
    payload = text if isinstance(text, bytes) else text.encode('utf-8')
    if not payload.endswith(b'\n'):
        payload += b'\n'
    with open(path, 'wb') as handle:
        handle.write(payload)
    return path


def restore_bundled(file_name):
    """Delete the local override so the bundled file is used again."""
    path = user_dict_path(file_name)
    if os.path.isfile(path):
        os.remove(path)
        return True
    return False


def overridden_dict_names():
    names = []
    directory = user_dict_dir()
    if not os.path.isdir(directory):
        return names
    for name in MANAGED_DICT_FILES:
        if os.path.isfile(os.path.join(directory, name)):
            names.append(name)
    return names


def bundled_opencc_pin():
    """Return (commit, tag) from bundled dictionary/readme.txt."""
    data = read_bundled_dict_bytes('readme.txt')
    if not data:
        return _FALLBACK_COMMIT, _FALLBACK_TAG
    match = _PIN_RE.search(data.decode('utf-8', errors='replace'))
    if not match:
        return _FALLBACK_COMMIT, _FALLBACK_TAG
    return match.group(1), match.group(2)


def bundled_opencc_tag():
    return bundled_opencc_pin()[1]
