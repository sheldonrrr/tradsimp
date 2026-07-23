# /pack — Build the local release zip

Run the project packaging script and confirm the artifact path.

## Steps

1. From the repo root, run:

```bash
bash scripts/package.sh
```

(Equivalent: `python3 scripts/build_plugin_zip.py` or `python3 setup.py -b`.)

2. Confirm output exists:

```text
dist/chinese_text_conversion-X.Y.Z.zip
```

(`X.Y.Z` comes from `PLUGIN_VERSION_TUPLE` / `PLUGIN_VERSION` in `__init__.py`.)

3. Optionally list the zip briefly to verify runtime files are present and dev-only trees are absent:
   - Should include: `__init__.py`, `main.py`, `dialogs.py`, `i18n.py`, `ui.py`, `resources/`, `images/`, `package-version.txt`, `plugin-import-name-*.txt`
   - Must **not** include: `docs/`, `scripts/`, `bin/`, `.git/`, `.cursor/`, `README*.md`, `mobileread-*.md`, `__pycache__/`

4. Reply with the full path to the zip and the version string.

## Packaging expectations

Packaging is an **allowlist** (root `PLUGIN_FILES` + `images/` + `resources/` only), plus explicit OS/dev excludes in `setup.py`:

- **macOS (primary pack host):** `.DS_Store`, `._*` AppleDouble, `__MACOSX/`, `.Spotlight-V100`, `.Trashes`, `.fseventsd`, `.TemporaryItems`
- **Windows:** `Thumbs.db`, `Desktop.ini`, `$RECYCLE.BIN/`
- **Editor / Python:** `*~`, `*.swp`, `*.swo`, `__pycache__/`, `*.py[cod]`
- **Dev-only:** `.cursor/`, `scripts/`, `bin/`, `dist/`, `testdata/`, README / `mobileread*.md`, `setup.py`

If a new junk path appears on the pack machine, add it to `setup.py` before packaging, then re-run.

## Do not

- Commit the zip
- Upload/release unless the user also asks
- Change the plugin version (use `/upgrade-version` for that)
