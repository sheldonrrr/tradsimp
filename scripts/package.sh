#!/usr/bin/env bash
# Package Chinese Conversion plugin zip into dist/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

exec python3 scripts/build_plugin_zip.py "$@"
