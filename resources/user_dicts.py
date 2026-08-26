# -*- coding: utf-8 -*-
"""Copy-on-write local OpenCC dictionaries in the Calibre config directory."""

from __future__ import print_function

import os
import re
import json

USER_PHRASES_FILE = 'UserPhrases.txt'
USER_PHRASES_JSON = 'user_phrases.json'
PLUGIN_DICT_SUBDIR = ('plugins', 'chinese_text_conversion', 'dictionaries')

PHRASE_DIRECTION_S2T = 's2t'
PHRASE_DIRECTION_S2TW = 's2tw'
PHRASE_DIRECTION_S2HK = 's2hk'
PHRASE_DIRECTION_T2S = 't2s'
PHRASE_DIRECTION_TW2S = 'tw2s'
PHRASE_DIRECTION_HK2S = 'hk2s'
PHRASE_DIRECTION_T2TW = 't2tw'
PHRASE_DIRECTION_T2HK = 't2hk'

PHRASE_DIRECTIONS = (
    PHRASE_DIRECTION_S2T,
    PHRASE_DIRECTION_S2TW,
    PHRASE_DIRECTION_S2HK,
    PHRASE_DIRECTION_T2S,
    PHRASE_DIRECTION_TW2S,
    PHRASE_DIRECTION_HK2S,
    PHRASE_DIRECTION_T2TW,
    PHRASE_DIRECTION_T2HK,
)

_PHRASE_DIRECTION_MSGIDS = {
    PHRASE_DIRECTION_S2T: 'Phrase direction s2t',
    PHRASE_DIRECTION_S2TW: 'Phrase direction s2tw',
    PHRASE_DIRECTION_S2HK: 'Phrase direction s2hk',
    PHRASE_DIRECTION_T2S: 'Phrase direction t2s',
    PHRASE_DIRECTION_TW2S: 'Phrase direction tw2s',
    PHRASE_DIRECTION_HK2S: 'Phrase direction hk2s',
    PHRASE_DIRECTION_T2TW: 'Phrase direction t2tw',
    PHRASE_DIRECTION_T2HK: 'Phrase direction t2hk',
}

# OpenCC config name -> phrase-direction keys that apply.
CONVERSION_PHRASE_DIRS = {
    's2t': (PHRASE_DIRECTION_S2T,),
    's2tw': (PHRASE_DIRECTION_S2TW,),
    's2twp': (PHRASE_DIRECTION_S2TW,),
    's2hk': (PHRASE_DIRECTION_S2HK,),
    's2hkp': (PHRASE_DIRECTION_S2HK,),
    't2s': (PHRASE_DIRECTION_T2S,),
    'tw2s': (PHRASE_DIRECTION_T2S, PHRASE_DIRECTION_TW2S),
    'tw2sp': (PHRASE_DIRECTION_T2S, PHRASE_DIRECTION_TW2S),
    'hk2s': (PHRASE_DIRECTION_T2S, PHRASE_DIRECTION_HK2S),
    'hk2sp': (PHRASE_DIRECTION_T2S, PHRASE_DIRECTION_HK2S),
    't2tw': (PHRASE_DIRECTION_T2TW,),
    't2hk': (PHRASE_DIRECTION_T2HK,),
    'hk2tw': (PHRASE_DIRECTION_T2TW,),
    'tw2hk': (PHRASE_DIRECTION_T2HK,),
}

DEFAULT_PHRASE_DIRECTION = PHRASE_DIRECTION_S2T

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


def user_phrases_template():
    from calibre_plugins.chinese_text_conversion.i18n import _
    return _('UserPhrases.txt template')


def _user_phrases_has_data(text):
    for line in (text or '').splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and '\t' in stripped:
            return True
    return False


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


def ensure_user_phrases_file(create_if_missing=True):
    """Create or refresh the local UserPhrases.txt starter file."""
    directory = ensure_user_dict_dir()
    path = os.path.join(directory, USER_PHRASES_FILE)
    template = user_phrases_template()
    if not os.path.isfile(path):
        if create_if_missing:
            save_override(USER_PHRASES_FILE, template)
    else:
        with open(path, 'rb') as handle:
            existing = handle.read().decode('utf-8', errors='replace')
        if not _user_phrases_has_data(existing):
            save_override(USER_PHRASES_FILE, template)
    return path


def user_dict_path(file_name):
    return os.path.join(user_dict_dir(), safe_dict_name(file_name))


def is_overridden(file_name):
    if file_name == USER_PHRASES_FILE:
        return has_user_phrases()
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
        return user_phrases_template().encode('utf-8')
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
    if os.path.isdir(directory):
        for name in MANAGED_DICT_FILES:
            if name == USER_PHRASES_FILE:
                continue
            if os.path.isfile(os.path.join(directory, name)):
                names.append(name)
    if has_user_phrases():
        names.insert(0, USER_PHRASES_FILE)
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


def phrase_direction_label(direction):
    from calibre_plugins.chinese_text_conversion.i18n import _
    msgid = _PHRASE_DIRECTION_MSGIDS.get(direction)
    if msgid:
        return _(msgid)
    return direction


def user_phrases_json_path():
    return os.path.join(user_dict_dir(), USER_PHRASES_JSON)


def user_phrases_json_exists():
    return os.path.isfile(user_phrases_json_path())


def _normalize_phrase(item):
    if not isinstance(item, dict):
        return None
    direction = item.get('direction') or DEFAULT_PHRASE_DIRECTION
    if direction not in PHRASE_DIRECTIONS:
        direction = DEFAULT_PHRASE_DIRECTION
    source = (item.get('source') or '').strip()
    target = (item.get('target') or '').strip()
    if not source or not target:
        return None
    return {
        'direction': direction,
        'source': source,
        'target': target,
    }


def _parse_legacy_user_phrase_lines(text):
    phrases = []
    seen = set()
    for line in (text or '').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or '\t' not in stripped:
            continue
        source, target = stripped.split('\t', 1)
        source = source.strip()
        target = target.strip()
        if not source or not target:
            continue
        key = (DEFAULT_PHRASE_DIRECTION, source)
        if key in seen:
            continue
        seen.add(key)
        phrases.append({
            'direction': DEFAULT_PHRASE_DIRECTION,
            'source': source,
            'target': target,
        })
    return phrases


def _write_user_phrases(phrases):
    directory = ensure_user_dict_dir()
    path = os.path.join(directory, USER_PHRASES_JSON)
    payload = {'phrases': list(phrases)}
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    if not data.endswith('\n'):
        data += '\n'
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(data)
    return path


def import_legacy_user_phrases_if_needed():
    """Create JSON from an existing UserPhrases.txt the first time."""
    path = user_phrases_json_path()
    if os.path.isfile(path):
        return
    raw = read_user_dict_bytes(USER_PHRASES_FILE)
    text = raw.decode('utf-8', errors='replace') if raw else ''
    phrases = _parse_legacy_user_phrase_lines(text)
    _write_user_phrases(phrases)


def load_user_phrases():
    import_legacy_user_phrases_if_needed()
    path = user_phrases_json_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except Exception:
        return []
    items = payload.get('phrases') if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return []
    phrases = []
    seen = set()
    for item in items:
        phrase = _normalize_phrase(item)
        if phrase is None:
            continue
        key = (phrase['direction'], phrase['source'])
        if key in seen:
            continue
        seen.add(key)
        phrases.append(phrase)
    return phrases


def save_user_phrases(phrases):
    cleaned = []
    seen = set()
    for item in phrases or []:
        phrase = _normalize_phrase(item)
        if phrase is None:
            continue
        key = (phrase['direction'], phrase['source'])
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(phrase)
    _write_user_phrases(cleaned)
    return cleaned


def has_user_phrases():
    return bool(load_user_phrases())


def find_user_phrase(direction, source):
    source = (source or '').strip()
    for phrase in load_user_phrases():
        if phrase['direction'] == direction and phrase['source'] == source:
            return phrase
    return None


def add_user_phrase(direction, source, target):
    phrase = _normalize_phrase({
        'direction': direction,
        'source': source,
        'target': target,
    })
    if phrase is None:
        return None, 'empty'
    if find_user_phrase(phrase['direction'], phrase['source']):
        return None, 'duplicate'
    phrases = load_user_phrases()
    phrases.append(phrase)
    save_user_phrases(phrases)
    return phrase, 'ok'


def update_user_phrase(old_direction, old_source, direction, source, target):
    phrase = _normalize_phrase({
        'direction': direction,
        'source': source,
        'target': target,
    })
    if phrase is None:
        return None, 'empty'
    old_source = (old_source or '').strip()
    phrases = load_user_phrases()
    index = None
    for i, existing in enumerate(phrases):
        if (existing['direction'] == old_direction
                and existing['source'] == old_source):
            index = i
            break
    if index is None:
        return None, 'missing'
    collision = find_user_phrase(phrase['direction'], phrase['source'])
    if collision is not None and not (
            phrase['direction'] == old_direction
            and phrase['source'] == old_source):
        return None, 'duplicate'
    phrases[index] = phrase
    save_user_phrases(phrases)
    return phrase, 'ok'


def delete_user_phrase(direction, source):
    source = (source or '').strip()
    phrases = load_user_phrases()
    kept = [
        item for item in phrases
        if not (item['direction'] == direction and item['source'] == source)
    ]
    if len(kept) == len(phrases):
        return False
    save_user_phrases(kept)
    return True


def clear_user_phrases():
    _write_user_phrases([])


def user_phrase_sources():
    sources = []
    seen = set()
    for phrase in load_user_phrases():
        source = phrase['source']
        if source in seen:
            continue
        seen.add(source)
        sources.append(source)
    return sources


def read_user_phrases_opencc_bytes(conversion):
    """OpenCC txt bytes for phrases that apply to this conversion, or None."""
    phrases = load_user_phrases()
    if not phrases:
        return None
    if conversion:
        allowed = CONVERSION_PHRASE_DIRS.get(conversion, ())
        if not allowed:
            return None
        phrases = [
            item for item in phrases if item['direction'] in allowed
        ]
    if not phrases:
        return None
    lines = [
        '%s\t%s' % (item['source'], item['target'])
        for item in phrases
    ]
    return ('\n'.join(lines) + '\n').encode('utf-8')


def iter_user_phrase_keys():
    """Multi-character source keys for Jieba injection."""
    for phrase in load_user_phrases():
        source = phrase.get('source') or ''
        if len(source) >= 2:
            yield source
