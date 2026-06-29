#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync OpenCC dictionary txt files and configs from an upstream checkout."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

OPENCC_COMMIT = '1a7c529'
OPENCC_TAG = 'ver.1.3.2'

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_DIR = os.path.join(PLUGIN_ROOT, 'resources', 'opencc_python', 'dictionary')
CONFIG_DIR = os.path.join(PLUGIN_ROOT, 'resources', 'opencc_python', 'config')

UPSTREAM_TXT_FILES = [
    'CJK_Compatibility_Ideographs.txt',
    'HKPhrases.txt',
    'HKPhrasesRev.txt',
    'HKVariants.txt',
    'HKVariantsPhrases.txt',
    'HKVariantsRevPhrases.txt',
    'JPShinjitaiCharacters.txt',
    'JPShinjitaiPhrases.txt',
    'STCharacters.txt',
    'STPhrases.txt',
    'TSCharacters.txt',
    'TSPhrases.txt',
    'TWPhrases.txt',
    'TWPhrasesRev.txt',
    'TWVariants.txt',
    'TWVariantsPhrases.txt',
    'TWVariantsRevPhrases.txt',
]

REVERSE_SOURCES = [
    'HKVariants',
    'TWVariants',
    'JPShinjitaiCharacters',
]

OBSOLETE_DICT_FILES = [
    'JPVariants.txt',
    'JPVariantsRev.txt',
    'TWPhrasesIT.txt',
    'TWPhrasesName.txt',
    'TWPhrasesOther.txt',
]

CONFIG_FILES = [
    'hk2s.json', 'hk2sp.json', 'hk2t.json', 'jp2t.json', 's2hk.json', 's2hkp.json',
    's2t.json', 's2tw.json', 's2twp.json', 't2hk.json', 't2jp.json', 't2s.json',
    't2tw.json', 'tw2s.json', 'tw2sp.json', 'tw2t.json',
]


def upstream_dict_dir(src: str) -> str:
    return os.path.join(src, 'data', 'dictionary')


def upstream_config_dir(src: str) -> str:
    return os.path.join(src, 'data', 'config')


def upstream_scripts_dir(src: str) -> str:
    return os.path.join(src, 'data', 'scripts')


def copy_upstream_txt(src: str) -> None:
    src_dir = upstream_dict_dir(src)
    for name in UPSTREAM_TXT_FILES:
        shutil.copy2(os.path.join(src_dir, name), os.path.join(DICT_DIR, name))


def generate_ts_characters_ext(src: str) -> None:
    script = os.path.join(upstream_scripts_dir(src), 'extract_tofu_risk.py')
    subprocess.check_call([
        sys.executable, script,
        os.path.join(DICT_DIR, 'TSCharacters.txt'),
        os.path.join(DICT_DIR, 'TSCharactersExt.txt'),
    ])


def generate_reverse_dicts(src: str) -> None:
    script = os.path.join(upstream_scripts_dir(src), 'reverse.py')
    for base in REVERSE_SOURCES:
        subprocess.check_call([
            sys.executable, script,
            os.path.join(DICT_DIR, base + '.txt'),
            os.path.join(DICT_DIR, base + 'Rev.txt'),
        ])


def ocd2_config_to_txt(obj):
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if key == 'may_output_tofu' and value:
                return None
            converted = ocd2_config_to_txt(value)
            if converted is None:
                continue
            out[key] = converted
        if obj.get('type') == 'ocd2':
            out['type'] = 'txt'
            out['file'] = obj['file'].replace('.ocd2', '.txt')
        return out
    if isinstance(obj, list):
        items = []
        for item in obj:
            converted = ocd2_config_to_txt(item)
            if converted is not None:
                items.append(converted)
        return items
    return obj


def sync_configs(src: str) -> None:
    for name in CONFIG_FILES:
        with open(os.path.join(upstream_config_dir(src), name), encoding='utf-8') as fh:
            data = json.load(fh)
        data = ocd2_config_to_txt(data)
        with open(os.path.join(CONFIG_DIR, name), 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write('\n')


def generate_st_phrases_from_regional(src: str) -> None:
    opencc_dir = os.path.join(PLUGIN_ROOT, 'resources', 'opencc_python')
    sys.path.insert(0, opencc_dir)
    from opencc import OpenCC

    def get_resource(file_type, file_name):
        if file_type == 'config':
            path = os.path.join(CONFIG_DIR, file_name)
        elif file_type == 'dictionary':
            path = os.path.join(DICT_DIR, file_name)
        else:
            raise ValueError(file_type)
        with open(path, 'rb') as fh:
            return fh.read()

    converter = OpenCC(get_resource, 't2s')
    collisions = {}
    conflicts = {}
    for phrase_file in ('HKPhrases.txt', 'TWPhrases.txt'):
        path = os.path.join(DICT_DIR, phrase_file)
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key = line.split('\t', 1)[0]
                converted = converter.convert(key)
                if len(converted) < 3:
                    continue
                if converted in collisions and collisions[converted] != key:
                    conflicts.setdefault(converted, set()).update({collisions[converted], key})
                else:
                    collisions[converted] = key

    if conflicts:
        raise SystemExit(
            'Conflicting regional phrase simplified projections: '
            + ', '.join(sorted(conflicts))
        )

    output = os.path.join(DICT_DIR, 'STPhrases_GeneratedFromRegionalPhrases.txt')
    with open(output, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# Open Chinese Convert (OpenCC) Dictionary\n')
        fh.write('# File: STPhrases_GeneratedFromRegionalPhrases.txt\n')
        fh.write('# Format: key\tvalue(s) (values separated by spaces)\n')
        fh.write('# License: Apache-2.0 (see LICENSE)\n')
        fh.write('# Source: generated from HKPhrases.txt, TWPhrases.txt keys via t2s.json\n')
        fh.write('# Used in configs: s2hkp.json, s2twp.json, s2hk.json, s2tw.json, s2t.json\n')
        fh.write('#\n')
        fh.write('# This generated ST phrase dictionary preserves Simplified-input spans\n')
        fh.write('# before applying regional phrase vocabulary.\n')
        fh.write('\n')
        for simplified in sorted(collisions):
            fh.write(f'{simplified}\t{collisions[simplified]}\n')


def remove_obsolete_files() -> None:
    for name in OBSOLETE_DICT_FILES:
        path = os.path.join(DICT_DIR, name)
        if os.path.exists(path):
            os.remove(path)


def update_readme() -> None:
    readme = os.path.join(DICT_DIR, 'readme.txt')
    with open(readme, encoding='utf-8') as fh:
        text = fh.read()
    text = re.sub(
        r'commit [0-9a-f]+',
        f'commit {OPENCC_COMMIT} ({OPENCC_TAG})',
        text,
        count=1,
    )
    with open(readme, 'w', encoding='utf-8') as fh:
        fh.write(text)


def main() -> int:
    parser = argparse.ArgumentParser(description='Sync OpenCC resources into the plugin.')
    parser.add_argument(
        'upstream',
        nargs='?',
        default='/tmp/opencc-upstream',
        help='Path to an OpenCC git checkout (default: /tmp/opencc-upstream)',
    )
    args = parser.parse_args()
    if not os.path.isdir(args.upstream):
        print('Upstream path not found:', args.upstream, file=sys.stderr)
        return 1

    print('Copying upstream txt dictionaries...')
    copy_upstream_txt(args.upstream)
    print('Generating TSCharactersExt.txt...')
    generate_ts_characters_ext(args.upstream)
    print('Generating reverse dictionaries...')
    generate_reverse_dicts(args.upstream)
    print('Syncing config JSON files...')
    sync_configs(args.upstream)
    print('Generating STPhrases_GeneratedFromRegionalPhrases.txt...')
    generate_st_phrases_from_regional(args.upstream)
    print('Removing obsolete dictionary files...')
    remove_obsolete_files()
    print('Updating readme.txt...')
    update_readme()
    print(f'Done. Synced OpenCC {OPENCC_TAG} ({OPENCC_COMMIT}).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
