**Languages:** [English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

# tradsimp

**Chinese Conversion · 简繁转换** · for Calibre

Convert Simplified and Traditional Chinese ebooks locally with built-in **OpenCC** dictionaries and rules. An optional **ZhConvert online short-text tool** is available for manually entered snippets; it never reads or uploads your books.

This repository continues development and maintenance of Hopkins’s [Chinese Text Conversion](https://www.mobileread.com/forums/showthread.php?t=275572) plugin for Calibre.

**Current version: 3.11.2** · Requires Calibre 6.0 or later · Type: **Main library toolbar action**

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
- Conversion uses the default path out of the box. An optional “Convert by whole words” checkbox can improve phrase-level accuracy for some texts (e.g. avoiding wrong cuts like 王后; first use may be a bit slower).
- **Forced conversion (coverage first)** normalizes mixed Simplified/Traditional text through a Simplified pivot before rebuilding the selected Traditional form. It uses only the bundled OpenCC rules and can convert more text at the cost of regional-wording precision. It is not typo proofreading. The option requires bilingual annotation so the original remains visible below; both options default to enabled for new installations.
- Generated library books receive an identifying title suffix by default, such as `_繁体中文_香港_双语标注_07-29_21-34`. The ending records the local month, day, hour, and minute; books generated in the same minute receive `_2`, `_3`, and so on. The suffix can be disabled in Advanced options.
- **Advanced options** use clearer grouping with live **example previews** when you change quotation marks or bilingual modes
- Optional **Lighter output**: remove embedded font files and/or all images (including the cover) for a smaller, faster, near text-only book
- The toolbar menu also provides an optional **ZhConvert online short-text conversion** window with Simplified, Traditional, China, Hong Kong, Taiwan, and Wiki modes.

### Privacy and online use

Ebook conversion runs entirely on your computer using bundled OpenCC data and rules. It calls no online API and uploads no book content. Only text that you manually enter and explicitly send from the optional ZhConvert window leaves your computer.

The online window uses the third-party [ZhConvert API](https://zhconvert.org/). Its public documentation does not specify text-retention practices, so do not submit private or sensitive content. ZhConvert warns that results may contain errors and require review. This program uses the ZhConvert API service; commercial use of ZhConvert requires payment.

---

## Using the plugin (library)

1. Select one or more books in the Calibre library (EPUB or AZW3).
2. Click **Chinese Conversion** / **简繁中文转换** on the toolbar.
3. Choose conversion direction, regional style, and other options in the dialog (see **About** in the lower-left corner).
4. Start the job and wait for it to finish.
5. Sort by date or search the library for the **new book** whose title includes a time suffix—the original remains unchanged.

Default keyboard shortcut: `Ctrl+Shift+Alt+C` (customizable under Calibre **Preferences → Keyboard shortcuts**).

### Optional online short-text conversion

Open the toolbar button’s menu and choose **ZhConvert online short-text conversion**. Paste a short plain-text excerpt, choose a mode, and explicitly send it. The window displays the result, modules used, and server dictionary revision; it does not modify any book.

---

## Building from source

From the repository root:

```bash
python3 scripts/build_plugin_zip.py
# or: python3 setup.py -b
```

This reads the version from `__init__.py` and writes `dist/chinese_text_conversion-{version}.zip` (for example `dist/chinese_text_conversion-3.6.0.zip`). The zip includes `package-version.txt` and excludes dev files (`.cursor`, `__pycache__`, `release/`, README copies, etc.). Install it with:

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
