#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Build the Calibre plugin zip from the repository root.

Reads PLUGIN_VERSION_TUPLE from __init__.py and writes:
  dist/chinese_text_conversion-{version}.zip
  package-version.txt (inside the zip)

Excludes macOS metadata, __pycache__, .cursor, release/, mobileread-*.md,
README*.md, setup.py, scripts/, bin/, and other dev-only paths (see setup.py).

Usage (from repo root):
  python3 scripts/build_plugin_zip.py
  python3 scripts/build_plugin_zip.py --keep 3
'''

from __future__ import print_function

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from setup import (  # noqa: E402
    build_zip,
    find_version,
    plugin_zip_basename,
    plugin_zip_path,
)


def main():
    parser = argparse.ArgumentParser(description='Build Calibre plugin zip')
    parser.add_argument(
        '--keep', type=int, default=2, metavar='N',
        help='Keep newest N zip files in dist/ (default: 2)')
    args = parser.parse_args()
    os.chdir(REPO_ROOT)
    version = find_version()
    path = build_zip(keep=args.keep)
    print('')
    print('Build complete.')
    print('  version : {}'.format(version))
    print('  archive : {}'.format(path))
    print('  install : calibre-customize -a "{}"'.format(path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
