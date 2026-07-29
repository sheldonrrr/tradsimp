**Languages:** [English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

# tradsimp

**Chinese Conversion · 简繁转换** · for Calibre

Convert Simplified and Traditional Chinese in your Calibre library on your own machine. The plugin uses the built-in **OpenCC** dictionaries and rules—**no network access, no AI**—so your books never leave your computer.

This repository continues development and maintenance of Hopkins’s [Chinese Text Conversion](https://www.mobileread.com/forums/showthread.php?t=275572) plugin for Calibre.

**Current version: 3.7.1** · Requires Calibre 6.0 or later · Type: **Main library toolbar action**

---

## Download and install

Download the latest `chinese_text_conversion-x.y.z.zip` from this repository’s **Releases** page (build output lives in `dist/`), then in Calibre:

1. Open **Preferences → Plugins → Load plugin from file** and select the zip.
2. Restart Calibre when prompted.
3. Open **Preferences → Toolbars & menus → The main toolbar**, search for **Chinese Conversion** (简繁中文转换). The plugin is registered as **Chinese Conversion · 简繁转换** in Preferences → Plugins.

The **About** panel appears the first time you open the conversion dialog. You can open it again anytime from **About** in the lower-left corner of that window.

If the toolbar button is missing after an upgrade, or you are upgrading from the old import name (`chinese_text`), remove the previous plugin before installing the new zip:

```text
calibre-customize -r "Chinese Conversion · 简繁转换"
```

Then install again via **Load plugin from file**.

**From 3.2.0 onward**, the plugin Python module name changed from `calibre_plugins.chinese_text` to `calibre_plugins.chinese_text_conversion` (matching the zip filename `chinese_text_conversion-*.zip`). Uninstall the old version before upgrading. Saved conversion preferences (`plugins/chinese_text_conversion_ChineseConversion_settings`) are usually preserved, but you must add the toolbar button again.

---

## What it does

- **Traditional ↔ Simplified Chinese**, plus **regional Traditional variants** (Mainland, Hong Kong, and Taiwan usage)
- **Quotation marks** (Western vs. East Asian styles), **horizontal/vertical layout**, and **punctuation** adjustments
- Process **EPUB / AZW3** books in the library: conversion **adds a new book** and **does not modify** the original file
- UI languages: **English**, **简体中文**, **繁体中文（台湾）**, **繁体中文（香港）**
- Conversion uses OpenCC **mmseg** segmentation by default (aligned with upstream OpenCC). An optional experimental **Jieba** segmentation checkbox can improve phrase-level accuracy for some texts (first use may load the dictionary more slowly).

### Why it is safe to use: fully offline

Conversion runs entirely on your computer using the plugin’s bundled OpenCC data and rules. **No online APIs or AI services are called**, and no manuscript is uploaded—ideal if you care about privacy and reliability.

---

## Using the plugin (library)

1. Select one or more books in the Calibre library (EPUB or AZW3).
2. Click **Chinese Conversion** / **简繁中文转换** on the toolbar.
3. Choose conversion direction, regional style, and other options in the dialog (see **About** in the lower-left corner).
4. Start the job and wait for it to finish.
5. Sort by date or search the library for the **new book** whose title includes a time suffix—the original remains unchanged.

Default keyboard shortcut: `Ctrl+Shift+Alt+C` (customizable under Calibre **Preferences → Keyboard shortcuts**).

---

## Building from source

From the repository root:

```bash
python3 scripts/build_plugin_zip.py
# or: python3 setup.py -b
```

This reads the version from `__init__.py` and writes `dist/chinese_text_conversion-{version}.zip` (for example `dist/chinese_text_conversion-3.6.0.zip`). The zip includes `package-version.txt` and excludes dev files (`.cursor`, `__pycache__`, `mobileread-*.md`, README copies, etc.). Install it with:

```bash
calibre-customize -a "dist/chinese_text_conversion-3.6.0.zip"
```

Other useful commands:

```bash
python3 setup.py          # build zip and print install hint
python3 setup.py -d       # build, install zip, launch Calibre GUI
python3 setup.py -s       # install from source directory (no zip), launch GUI
```

---

## Local development (macOS / fish)

The `scripts/caldbg.fish` helper sets up Calibre on macOS and defines shortcuts for install-and-launch workflows:

```fish
source scripts/caldbg.fish
```

| Command | Description |
|---------|-------------|
| `caldbg-tsc` | Install from source, launch GUI |
| `caldbg-tsc-ag` | Kill old Calibre process, install from source, launch GUI |
| `caldbg-tsc-p` | Build zip (`python3 setup.py -b`), install zip, launch GUI |
| `caldbg-tsc-pag` | Same as `caldbg-tsc-p`, but kill old process first |

---

## License

- Plugin code: [GPL v3](LICENSE)
- OpenCC data and opencc-python components: Apache License 2.0 (see `resources/opencc_python/`)
- Optional Jieba segmentation: MIT (vendored slim copy under `resources/jieba/`, based on [fxsjy/jieba](https://github.com/fxsjy/jieba) v0.42.1)
