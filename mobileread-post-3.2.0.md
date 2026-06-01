[b][GUI Plugin] Chinese Text Conversion - Version 3.2.0 (community maintenance)[/b]

Continues Hopkins's original thread:
[url=https://www.mobileread.com/forums/showthread.php?t=275572]Traditional<->Simplified Chinese Convertor[/url]

Original author: Hopkins (3.1.2, Oct 2025). This release: 3.2.0 (Jun 2026), maintained in the tradsimp community fork. OpenCC-based, fully offline.

[b]Main changes in 3.2.0[/b]

- [b]GUI plugin on the main toolbar[/b]: was an Edit-book-only plugin (Editor -> Plugins menu). Now a library toolbar action: add [b]Chinese Conversion[/b] / 中文转换 under Preferences -> Toolbars & menus -> The main toolbar. Select EPUB/AZW3 in the library and convert without opening Edit book.
- [b]UI localization[/b]: dialog in English, Simplified Chinese, and Traditional Chinese (Taiwan / Hong Kong).
- [b]Non-destructive conversion[/b]: adds a new library entry; the original file is not replaced.

[b]Install[/b]

1. Remove old plugin: [code]calibre-customize -r "Chinese Text Conversion"[/code]
2. Preferences -> Plugins -> Load plugin from file -> chinese_text_conversion-3.2.0.zip
3. Restart calibre; add the toolbar button (see above)

Requires calibre 6.0+. Attached: chinese_text_conversion-3.2.0.zip
