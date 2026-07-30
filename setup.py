#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import glob
import inspect
import os
import re
import sys
import zipfile
from subprocess import Popen, PIPE, STDOUT

SCRIPT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
DIST_DIR = os.path.join(SCRIPT_DIR, 'dist')

PLUGIN_DIRS = ['images', 'resources']

def find_plugin_import_name_file():
    '''Return the plugin-import-name-*.txt basename (must be exactly one).'''
    matches = sorted(glob.glob(os.path.join(SCRIPT_DIR, 'plugin-import-name-*.txt')))
    if len(matches) != 1:
        raise SystemExit(
            'Expected exactly one plugin-import-name-*.txt, found: {}'.format(
                [os.path.basename(m) for m in matches]))
    return os.path.basename(matches[0])


PLUGIN_IMPORT_NAME_FILE = find_plugin_import_name_file()

PLUGIN_FILES = [
    '__init__.py',
    'ui.py',
    'library_flow.py',
    'icons.py',
    'ui_style.py',
    'dialogs.py',
    'i18n.py',
    'main.py',
    'zhconvert_api.py',
    'vision_ocr.py',
    'ocr_compat.py',
    PLUGIN_IMPORT_NAME_FILE,
    'LICENSE',
]

# Never pack these (OS junk / caches / dev trees). Plugin targets win+mac+linux;
# primary pack host is macOS, so Apple metadata must stay out of the zip.
SKIP_DIR_NAMES = frozenset({
    '__pycache__', '__MACOSX', '.git', '.cursor', '.idea', '.vscode',
    '.windsurf', '.claude', '.codex', '.agent', '.history', '.obsidian',
    'dist', 'scripts', 'bin', 'testdata', 'tmp_test_assets',
    '.pytest_cache', '.mypy_cache', 'venv', '.venv', 'env', 'node_modules',
    'agent-transcripts', 'terminals',
    # macOS Finder / Spotlight / Trash volume metadata
    '.Spotlight-V100', '.Trashes', '.fseventsd', '.TemporaryItems',
    '.DocumentRevisions-V100', '.AppleDouble',
    # Windows recycle bin folder name
    '$RECYCLE.BIN',
})
SKIP_FILE_NAMES = frozenset({
    # macOS
    '.DS_Store', '.AppleDouble', '.LSOverride',
    # Windows
    'Thumbs.db', 'ehthumbs.db', 'Desktop.ini',
    # VCS / packaging
    '.gitignore', '.gitattributes', 'setup.py',
})
SKIP_FILE_SUFFIXES = (
    '.pyc', '.pyo', '.pyd', '.po', '.pot', '.po~',
    '.swp', '.swo',  # vim
)
# Root-only dev docs (not used when walking resources/; listed for clarity).
SKIP_ROOT_DOC_BASENAMES = frozenset({
    'README.md', 'README.zh-CN.md', 'README.zh-TW.md',
})
SKIP_BASENAME_PREFIXES = (
    'mobileread',
    '._',      # AppleDouble resource forks (common on macOS SMB/USB copies)
)
SKIP_BASENAME_SUFFIXES = (
    '~',       # editor backups (file~, README.md~)
)
PACKAGE_VERSION_FILE = 'package-version.txt'


def _read_init_py():
    with open(os.path.join(SCRIPT_DIR, '__init__.py'), 'r', encoding='utf-8') as fd:
        return fd.read()


def find_version():
    match = re.search(
        r'PLUGIN_VERSION_TUPLE = \((\d+),\s*(\d+),\s*(\d+)\)', _read_init_py())
    if match:
        return '{}.{}.{}'.format(match.group(1), match.group(2), match.group(3))
    return '0.0.0'


def find_zip_slug():
    '''Zip basename prefix; matches PLUGIN_SAFE_NAME in __init__.py.'''
    match = re.search(r'PLUGIN_SAFE_NAME\s*=\s*["\']([^"\']+)["\']', _read_init_py())
    if match:
        return match.group(1).strip()
    return 'chinese_text_conversion'


def plugin_zip_basename(version=None):
    slug = find_zip_slug()
    ver = version if version is not None else find_version()
    return '{}-{}.zip'.format(slug, ver)


def plugin_zip_path(version=None):
    return os.path.join(DIST_DIR, plugin_zip_basename(version))


def package_version_payload(version=None):
    ver = version if version is not None else find_version()
    slug = find_zip_slug()
    lines = (
        'name={}\n'.format(slug),
        'version={}\n'.format(ver),
        'zip={}\n'.format(plugin_zip_basename(ver)),
    )
    return ''.join(lines)


def should_skip_archive_name(name):
    '''Filter OS junk, caches, and dev-only paths from the plugin zip.'''
    if not name:
        return False
    base = os.path.basename(name)
    if base in SKIP_FILE_NAMES or base in SKIP_ROOT_DOC_BASENAMES:
        return True
    lower_base = base.lower()
    for prefix in SKIP_BASENAME_PREFIXES:
        if lower_base.startswith(prefix):
            return True
    if base.endswith(SKIP_FILE_SUFFIXES):
        return True
    for suffix in SKIP_BASENAME_SUFFIXES:
        if base.endswith(suffix):
            return True
    parts = name.replace('\\', '/').split('/')
    for part in parts:
        if not part or part in ('.', '..'):
            continue
        if part in SKIP_DIR_NAMES:
            return True
        if part.startswith('._'):
            return True
        if part in ('.DS_Store', 'Thumbs.db', 'Desktop.ini'):
            return True
        if part == '.cursor' or part.startswith('.cursor'):
            return True
    return False


def calibre_wrapper(*cmd):
    process = Popen(list(cmd), stdout=PIPE, stderr=STDOUT)
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        if isinstance(nextline, bytes):
            nextline = nextline.decode('utf-8', 'replace')
        sys.stdout.write(nextline)
        sys.stdout.flush()
    process.wait()
    return process.returncode


def zip_up_dir(myzip, base_dir, local_name):
    current_dir = base_dir
    if local_name:
        current_dir = os.path.join(current_dir, local_name)
    try:
        entries = os.listdir(current_dir)
    except OSError:
        return
    for entry in sorted(entries):
        if entry in SKIP_DIR_NAMES:
            continue
        local_path = os.path.join(local_name, entry) if local_name else entry
        if should_skip_archive_name(local_path):
            continue
        real_path = os.path.join(current_dir, entry)
        if os.path.isfile(real_path):
            myzip.write(real_path, local_path.replace('\\', '/'), zipfile.ZIP_DEFLATED)
        elif os.path.isdir(real_path):
            zip_up_dir(myzip, base_dir, local_path)


def _zip_version_key(path):
    match = re.search(
        r'{}-([\d.]+)\.zip$'.format(re.escape(find_zip_slug())), os.path.basename(path))
    if not match:
        return (0, 0, 0)
    try:
        return tuple(int(x) for x in match.group(1).split('.'))
    except ValueError:
        return (0, 0, 0)


def prune_dist_versions(keep=2):
    '''Keep only the newest `keep` plugin zips in dist/ (latest + second-latest).'''
    os.makedirs(DIST_DIR, exist_ok=True)
    zips = glob.glob(os.path.join(DIST_DIR, find_zip_slug() + '-*.zip'))
    for legacy in (glob.glob(os.path.join(DIST_DIR, 'tradsimp-*.zip')) +
                   glob.glob(os.path.join(DIST_DIR, 'chinese_text_v*_plugin.zip'))):
        try:
            os.remove(legacy)
            print('Removed legacy dist zip: {}'.format(os.path.basename(legacy)))
        except OSError:
            pass
    if len(zips) <= keep:
        return
    zips.sort(key=_zip_version_key, reverse=True)
    for old in zips[keep:]:
        try:
            os.remove(old)
            print('Removed old build: {}'.format(os.path.basename(old)))
        except OSError as exc:
            print('Warning: could not remove {}: {}'.format(old, exc))


def remove_legacy_root_zips():
    for each in (glob.glob(os.path.join(SCRIPT_DIR, 'chinese_text_v*_plugin.zip')) +
                 glob.glob(os.path.join(SCRIPT_DIR, 'tradsimp-*.zip'))):
        try:
            os.remove(each)
            print('Removed legacy zip from repo root: {}'.format(os.path.basename(each)))
        except OSError:
            pass


def build_zip(keep=2):
    version = find_version()
    zip_slug = find_zip_slug()
    zip_path = plugin_zip_path(version)
    zip_basename = plugin_zip_basename(version)
    os.makedirs(DIST_DIR, exist_ok=True)
    remove_legacy_root_zips()
    print('Version {} -> dist/{}'.format(version, zip_basename))
    print('Creating {} ...'.format(os.path.join('dist', zip_basename)))
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as outzip:
        outzip.writestr(
            PACKAGE_VERSION_FILE,
            package_version_payload(version).encode('utf-8'))
        for entry in sorted(os.listdir(SCRIPT_DIR)):
            filepath = os.path.join(SCRIPT_DIR, entry)
            if os.path.isfile(filepath) and entry in PLUGIN_FILES:
                if should_skip_archive_name(entry):
                    continue
                outzip.write(filepath, entry, zipfile.ZIP_DEFLATED)
            elif os.path.isdir(filepath) and entry in PLUGIN_DIRS:
                zip_up_dir(outzip, SCRIPT_DIR, entry)
    prune_dist_versions(keep=keep)
    print('Plugin zip: {}'.format(zip_path))
    print('Embedded: {} ({})'.format(PACKAGE_VERSION_FILE, version))
    remaining = sorted(glob.glob(os.path.join(DIST_DIR, zip_slug + '-*.zip')),
                       key=_zip_version_key, reverse=True)
    if remaining:
        print('dist/ retains {} file(s): {}'.format(
            len(remaining), ', '.join(os.path.basename(z) for z in remaining)))
    return zip_path


def install_and_launch(debug_from_source=False):
    if debug_from_source:
        print('Installing from source directory ...')
        calibre_wrapper('calibre-customize', '-b', SCRIPT_DIR)
    else:
        zip_path = build_zip()
        print('Installing zip ...')
        calibre_wrapper('calibre-customize', '-a', zip_path)
    print('Launching calibre ...')
    return calibre_wrapper('calibre-debug', '--gui')


if __name__ == '__main__':
    from optparse import OptionParser

    opt = OptionParser(usage='python %prog [options]')
    opt.add_option(
        '-d', '--debug', action='store_true', dest='debugmode',
        help='Build zip, install plugin, and launch calibre GUI')
    opt.add_option(
        '-s', '--source', action='store_true', dest='sourcemode',
        help='Install from source dir (no zip) and launch calibre GUI')
    opt.add_option(
        '-b', '--build-only', action='store_true', dest='buildonly',
        help='Only build the plugin zip file into dist/')
    (options, args) = opt.parse_args()

    if options.buildonly:
        build_zip()
        sys.exit(0)

    if options.debugmode:
        calibre_wrapper('calibre-debug', '-s')
        sys.exit(install_and_launch(debug_from_source=False))

    if options.sourcemode:
        calibre_wrapper('calibre-debug', '-s')
        sys.exit(install_and_launch(debug_from_source=True))

    build_zip()
    print('Done. Install with: calibre-customize -a "{}"'.format(plugin_zip_path()))
