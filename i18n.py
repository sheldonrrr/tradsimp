# -*- coding: utf-8 -*-

__license__ = 'GPL v3'

# UI language: 0=English, 1=Simplified Chinese, 2=Traditional (Taiwan), 3=Traditional (Hong Kong)
# All user-visible strings must use _('msgid') or ngettext() from this module.
UI_LANG_EN = 0
UI_LANG_ZH_CN = 1
UI_LANG_ZH_TW = 2
UI_LANG_ZH_HK = 3

UI_LANG_CODES = ('en', 'zh_CN', 'zh_TW', 'zh_HK')
TRADITIONAL_UI_LANGS = frozenset((UI_LANG_ZH_TW, UI_LANG_ZH_HK))

# Taiwan → Hong Kong UI wording (applied to zh_TW strings for UI_LANG_ZH_HK).
_HK_WORD_REPLACEMENTS = (
    ('網路', '網絡'),
    ('軟體', '軟件'),
    ('臺灣', '台灣'),
    ('打印', '列印'),
    ('印出', '列印'),
    ('視頻', '影片'),
    ('這裡', '這裏'),
    ('那里', '那裏'),
    ('哪裡', '哪裏'),
)

_current_ui_lang = UI_LANG_EN


def _T(en, zh_cn, zh_tw, zh_hk=None):
    if zh_hk is None:
        zh_hk = zh_tw
    return {
        UI_LANG_EN: en,
        UI_LANG_ZH_CN: zh_cn,
        UI_LANG_ZH_TW: zh_tw,
        UI_LANG_ZH_HK: zh_hk,
    }


def _traditional_chinese_for_hong_kong(text):
    for old, new in _HK_WORD_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def _finalize_message_catalog():
    for entry in _MESSAGES.values():
        entry[UI_LANG_ZH_HK] = _traditional_chinese_for_hong_kong(
            entry[UI_LANG_ZH_TW])


# English msgid -> per-language string
_MESSAGES = {
    'Chinese Conversion': _T('Chinese Conversion', '中文转换', '中文轉換'),
    'Chinese Punctuation': _T('Chinese Punctuation', '中文标点', '中文標點'),
    'Interface Language:': _T('Interface Language:', '界面语言：', '介面語言：'),
    'English': _T('English', 'English', 'English'),
    'Simplified Chinese': _T('Simplified Chinese', '简体中文', '簡體中文'),
    'Traditional Chinese': _T('Traditional Chinese', '繁体中文', '繁體中文'),
    'Traditional Chinese (Taiwan)': _T(
        'Traditional Chinese (Taiwan)',
        '繁体中文（台湾）',
        '繁體中文（臺灣）',
        '繁體中文（台灣）'),
    'Traditional Chinese (Hong Kong)': _T(
        'Traditional Chinese (Hong Kong)',
        '繁体中文（香港）',
        '繁體中文（香港）',
        '繁體中文（香港）'),
    'Update quotes: “ ”,‘ ’ -> 「 」,『 』': _T(
        'Update quotes: “ ”,‘ ’ -> 「 」,『 』',
        '更新引号：“ ”、‘ ’ → 「 」、『 』',
        '更新引號：“ ”、‘ ’ → 「 」、『 』'),
    'Update quotes: 「 」,『 』 -> “ ”,‘ ’': _T(
        'Update quotes: 「 」,『 』 -> “ ”,‘ ’',
        '更新引号：「 」、『 』 → “ ”、‘ ’',
        '更新引號：「 」、『 』 → “ ”、‘ ’'),
    'Conversion Direction': _T('Conversion Direction', '转换方向', '轉換方向'),
    'No Conversion': _T('No Conversion', '不转换', '不轉換'),
    'Traditional to Simplified': _T('Traditional to Simplified', '繁体转简体', '繁體轉簡體'),
    'Simplified to Traditional': _T('Simplified to Traditional', '简体转繁体', '簡體轉繁體'),
    'Traditional to Traditional': _T('Traditional to Traditional', '繁体转繁体', '繁體轉繁體'),
    'Traditional to Traditional help': _T(
        'Still traditional Chinese; adjusts wording or character forms between regional varieties '
        '(e.g. Mainland / Hong Kong / Taiwan).',
        '仍是繁体字，只在不同地区繁体之间调整用词或字形习惯（如大陆/香港/台湾）。',
        '仍是繁體字，只在不同地區繁體之間調整用詞或字形習慣（如大陸/香港/臺灣）。'),
    'Language Styles': _T('Language Styles', '语言风格', '語言風格'),
    'Input:': _T('Input:', '输入：', '輸入：'),
    'Output:': _T('Output:', '输出：', '輸出：'),
    'Mainland': _T('Mainland', '大陆', '大陸'),
    'Hong Kong': _T('Hong Kong', '香港', '香港'),
    'Taiwan': _T('Taiwan', '台湾', '臺灣'),
    'Japan': _T('Japan', '日本', '日本'),
    'Select the origin region of the input': _T(
        'Select the origin region of the input', '选择输入文本的来源地区', '選擇輸入文字的來源地區'),
    'Select the desired region of the output': _T(
        'Select the desired region of the output', '选择输出文本的目标地区', '選擇輸出文字的目標地區'),
    'Use output target phrases if possible': _T(
        'Use output target phrases if possible', '尽可能使用目标地区的惯用词语', '盡可能使用目標地區的慣用詞語'),
    'Use target region phrases help': _T(
        'Besides character conversion, replace whole phrases with the target region’s usual wording '
        '(e.g. 软件 → 軟體, 程序 → 程式); unchecked means mostly single-character changes only. '
        'Only some input/output combinations support this.',
        '除简繁字形外，还会把整词改成输出地区常用说法（例如「软件」→「軟體」、「程序」→「程式」）；'
        '不勾选则主要只改单字，不改这类词语；且仅部分「输入/输出」组合支持。',
        '除簡繁字形外，還會把整詞改成輸出地區常用說法（例如「软件」→「軟體」、「程序」→「程式」）；'
        '不勾選則主要只改單字，不改這類詞語；且僅部分「輸入/輸出」組合支援。'),
    'Check to allow region specific word replacements if available': _T(
        'Check to allow region specific word replacements if available',
        '勾选以在可用时进行地区惯用词语替换', '勾選以在可用時進行地區慣用詞語替換'),
    'Quotation Marks': _T('Quotation Marks', '引号', '引號'),
    'Other Changes': _T('Other Changes', '其他更改', '其他變更'),
    'Text Direction:': _T('Text Direction:', '文字方向：', '文字方向：'),
    'Horizontal': _T('Horizontal', '横排', '橫排'),
    'Vertical': _T('Vertical', '直排', '直排'),
    'Select the desired text orientation': _T(
        'Select the desired text orientation', '选择所需的文字排版方向', '選擇所需的文字排版方向'),
    'Update punctuation': _T('Update punctuation', '更新标点', '更新標點'),
    'Settings...': _T('Settings...', '设置…', '設定…'),
    'Entire eBook': _T('Entire eBook', '整本电子书', '整本電子書'),
    'Current File': _T('Current File', '当前文件', '目前檔案'),
    'Tagged Text in Current File': _T('Tagged Text in Current File', '当前文件中的标记文本', '目前檔案中的標記文字'),
    '“Tagged Text” is bracketed by <!--PI_SELTEXT_START--> and <!--PI_SELTEXT_END-->': _T(
        '“Tagged Text” is bracketed by <!--PI_SELTEXT_START--> and <!--PI_SELTEXT_END-->',
        '“标记文本”由 <!--PI_SELTEXT_START--> 与 <!--PI_SELTEXT_END--> 括起',
        '「標記文字」由 <!--PI_SELTEXT_START--> 與 <!--PI_SELTEXT_END--> 括起'),
    'Source': _T('Source', '来源', '來源'),
    'Punctuation': _T('Punctuation', '标点', '標點'),
    'Clear All': _T('Clear All', '全部清除', '全部清除'),
    'Set All': _T('Set All', '全部选中', '全部選取'),
    'Default': _T('Default', '默认', '預設'),
    'Valid input/output combinations:\nNot Applicable': _T(
        'Valid input/output combinations:\nNot Applicable',
        '有效的输入/输出组合：\n不适用', '有效的輸入/輸出組合：\n不適用'),
    'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Mainland\nTaiwan/Mainland\nMainland/Japan': _T(
        'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Mainland\nTaiwan/Mainland\nMainland/Japan',
        '有效的输入/输出组合：\n香港/大陆\n大陆/大陆\n台湾/大陆\n大陆/日本',
        '有效的輸入/輸出組合：\n香港/大陸\n大陸/大陸\n臺灣/大陸\n大陸/日本'),
    'Valid input/output combinations:\nMainland/Hong Kong\nMainland/Mainland\nMainland/Taiwan\nJapan/Mainland': _T(
        'Valid input/output combinations:\nMainland/Hong Kong\nMainland/Mainland\nMainland/Taiwan\nJapan/Mainland',
        '有效的输入/输出组合：\n大陆/香港\n大陆/大陆\n大陆/台湾\n日本/大陆',
        '有效的輸入/輸出組合：\n大陸/香港\n大陸/大陸\n大陸/臺灣\n日本/大陸'),
    'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan': _T(
        'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan',
        '有效的输入/输出组合：\n香港/大陆\n大陆/香港\n台湾/大陆\n大陆/台湾\n大陆/大陆\n香港/香港\n台湾/台湾',
        '有效的輸入/輸出組合：\n香港/大陸\n大陸/香港\n臺灣/大陸\n大陸/臺灣\n大陸/大陸\n香港/香港\n臺灣/臺灣'),
    'Convert Chinese Text Simplified/Traditional': _T(
        'Convert Chinese Text Simplified/Traditional', '简繁中文转换', '簡繁中文轉換'),
    'No book open': _T('No book open', '未打开书籍', '未開啟書籍'),
    'Need to have a book open first.': _T(
        'Need to have a book open first.', '请先打开一本书。', '請先開啟一本書。'),
    'Before: Text Conversion': _T('Before: Text Conversion', '之前：文字转换', '之前：文字轉換'),
    'No Changes': _T('No Changes', '无更改', '無變更'),
    'The output configuration selected is not supported.\n Please use a different Input/Output Language Styles combination': _T(
        'The output configuration selected is not supported.\n Please use a different Input/Output Language Styles combination',
        '所选输出配置不受支持。\n请使用其他输入/输出语言风格组合。',
        '所選輸出設定不受支援。\n請使用其他輸入/輸出語言風格組合。'),
    'Failed': _T('Failed', '失败', '失敗'),
    'Failed to convert Chinese, click "Show details" for more info': _T(
        'Failed to convert Chinese, click "Show details" for more info',
        '中文转换失败，点击“显示详情”了解更多信息',
        '中文轉換失敗，點擊「顯示詳情」了解更多資訊'),
    'No text meeting your criteria was found to change.\nNo changes made.': _T(
        'No text meeting your criteria was found to change.\nNo changes made.',
        '未找到符合您条件的可更改文本。\n未进行任何更改。',
        '未找到符合您條件的可變更文字。\n未進行任何變更。'),
    'Cannot Process': _T('Cannot Process', '无法处理', '無法處理'),
    'No file open for editing or the current file is not an (x)html file.': _T(
        'No file open for editing or the current file is not an (x)html file.',
        '没有打开可编辑的文件，或当前文件不是 (x)html 文件。',
        '沒有開啟可編輯的檔案，或目前檔案不是 (x)html 檔案。'),
    'Converting': _T('Converting', '正在转换', '正在轉換'),
    'OK': _T('OK', '确定', '確定'),
    'Start Processing': _T('Start Processing', '开始处理', '開始處理'),
    'Cancel': _T('Cancel', '取消', '取消'),
    'Processing…': _T('Processing…', '处理中…', '處理中…'),
    'Processing complete': _T('Processing complete', '处理完成', '處理完成'),
    'Result preview': _T('Result preview', '处理结果预览', '處理結果預覽'),
    'New books will be added to the library; original files are not modified.': _T(
        'New books will be added to the library; original files are not modified.',
        '将在书库中新建书籍，不会修改原书文件。',
        '將在書庫中新建書籍，不會修改原書檔案。'),
    'Processing ({}/{}): {}': _T(
        'Processing ({}/{}): {}', '正在处理（{}/{}）：{}', '正在處理（{}/{}）：{}'),
    'No changes for “{}”; no new book created.': _T(
        'No changes for “{}”; no new book created.',
        '《{}》无可用更改，未创建新书。',
        '《{}》無可用變更，未建立新書。'),
    '—— {} ——': _T('—— {} ——', '—— {} ——', '—— {} ——'),
    'Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}\nSuffix: {}': _T(
        'Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}\nSuffix: {}',
        '原书：{}\n新书：{}\n书库编号：{}\n格式：{}\n后缀：{}',
        '原書：{}\n新書：{}\n書庫編號：{}\n格式：{}\n後綴：{}'),
    'File: ': _T('File: ', '文件：', '檔案：'),
    'Changed files: ': _T('Changed files: ', '已更改文件：', '已變更檔案：'),
    'No text excerpt available.': _T(
        'No text excerpt available.', '无文字预览。', '無文字預覽。'),
    'Created as a new library book by Chinese Text Conversion (source book id: {}).': _T(
        'Created as a new library book by Chinese Text Conversion (source book id: {}).',
        '由「简繁中文转换」插件新建入库（来源书籍编号：{}）。',
        '由「簡繁中文轉換」外掛新建入庫（來源書籍編號：{}）。'),
    'Unknown': _T('Unknown', '未知', '未知'),
    'No changes (originals kept):': _T(
        'No changes (originals kept):', '无更改（保留原书）：', '無變更（保留原書）：'),
    'Failed:': _T('Failed:', '失败：', '失敗：'),
    'Created 1 new book in the library:': _T(
        'Created 1 new book in the library:',
        '已在书库中新建 1 本书：',
        '已在書庫中新建 1 本書：'),
    'Created {} new books in the library:': _T(
        'Created {} new books in the library:',
        '已在书库中新建 {} 本书：',
        '已在書庫中新建 {} 本書：'),
    'Failed: {}': _T('Failed: {}', '失败：{}', '失敗：{}'),
    'Conversion succeeded. The new book is already in your library. Open the library and check the most recently added book (sort by Date).': _T(
        'Conversion succeeded. The new book is already in your library. Open the library and check the most recently added book (sort by Date).',
        '转换已成功，新书已加入书库。请打开书库，按「日期」排序或查看最新一本书即可。',
        '轉換已成功，新書已加入書庫。請開啟書庫，按「日期」排序或查看最新一本書即可。'),
    'Conversion succeeded. {} new books are already in your library. Open the library and check the most recently added entries (sort by Date).': _T(
        'Conversion succeeded. {} new books are already in your library. Open the library and check the most recently added entries (sort by Date).',
        '转换已成功，{} 本新书已加入书库。请打开书库，按「日期」排序或查看最新书籍即可。',
        '轉換已成功，{} 本新書已加入書庫。請開啟書庫，按「日期」排序或查看最新書籍即可。'),
    'Changed Files': _T('Changed Files', '已更改的文件', '已變更的檔案'),
    'See what changed': _T('See what changed', '查看更改', '查看變更'),
    'Close': _T('Close', '关闭', '關閉'),
    'Plugin version: ': _T('Plugin version: ', '插件版本：', '外掛版本：'),
    'Configuration file: ': _T('Configuration file: ', '配置文件：', '設定檔：'),
    'Output direction: ': _T('Output direction: ', '输出方向：', '輸出方向：'),
    'No change': _T('No change', '不更改', '不變更'),
    'No Change': _T('No Change', '不更改', '不變更'),
    'Traditional->Simplified': _T('Traditional->Simplified', '繁体→简体', '繁體→簡體'),
    'Simplified->Traditional': _T('Simplified->Traditional', '简体→繁体', '簡體→繁體'),
    'Traditional->Traditional': _T('Traditional->Traditional', '繁体→繁体', '繁體→繁體'),
    'Input locale: ': _T('Input locale: ', '输入地区：', '輸入地區：'),
    'Output locale: ': _T('Output locale: ', '输出地区：', '輸出地區：'),
    'Use destination phrases: ': _T('Use destination phrases: ', '使用目标惯用语：', '使用目標慣用語：'),
    'Quotation Mark Style: ': _T('Quotation Mark Style: ', '引号样式：', '引號樣式：'),
    'Western': _T('Western', '西式', '西式'),
    'East Asian': _T('East Asian', '东亚', '東亞'),
    'Text direction: ': _T('Text direction: ', '文字方向：', '文字方向：'),
    'Update punctuation to match text direction: ': _T(
        'Update punctuation to match text direction: ',
        '更新标点以匹配文字方向：', '更新標點以符合文字方向：'),
    'Output directory: Overwrite existing file': _T(
        'Output directory: Overwrite existing file', '输出目录：覆盖现有文件', '輸出目錄：覆寫現有檔案'),
    'Output directory: Same directory as input file': _T(
        'Output directory: Same directory as input file',
        '输出目录：与输入文件相同目录', '輸出目錄：與輸入檔案相同目錄'),
    'Output directory: ': _T('Output directory: ', '输出目录：', '輸出目錄：'),
    'Output file basename suffix: ': _T(
        'Output file basename suffix: ', '输出文件主名后缀：', '輸出檔案主檔名後綴：'),
    ' File(s) will be converted:': _T(' File(s) will be converted:', ' 个文件将被转换：', ' 個檔案將被轉換：'),
    'Convert Chinese characters between traditional/simplified types and/or change text style.\n'
    'Generally run as: calibre-debug --run-plugin "Chinese Text Conversion" -- [options] ebook-filepath\n'
    'Plugin Version: ': _T(
        'Convert Chinese characters between traditional/simplified types and/or change text style.\n'
        'Generally run as: calibre-debug --run-plugin "Chinese Text Conversion" -- [options] ebook-filepath\n'
        'Plugin Version: ',
        '在繁体/简体中文及其他文字样式之间转换。\n'
        '通常运行：calibre-debug --run-plugin "Chinese Text Conversion" -- [选项] 电子书路径\n'
        '插件版本：',
        '在繁體/簡體中文及其他文字樣式之間轉換。\n'
        '通常執行：calibre-debug --run-plugin "Chinese Text Conversion" -- [選項] 電子書路徑\n'
        '外掛版本：'),
    'Set to the ebook origin locale if known (Default: cn)': _T(
        'Set to the ebook origin locale if known (Default: cn)',
        '若已知，设置电子书来源地区（默认：cn）', '若已知，設定電子書來源地區（預設：cn）'),
    'Set to the ebook target locale (Default: cn)': _T(
        'Set to the ebook target locale (Default: cn)',
        '设置电子书目标地区（默认：cn）', '設定電子書目標地區（預設：cn）'),
    'Set to the ebook conversion direction (Default: none)': _T(
        'Set to the ebook conversion direction (Default: none)',
        '设置电子书转换方向（默认：none）', '設定電子書轉換方向（預設：none）'),
    'Convert phrases to target locale versions (Default: False)': _T(
        'Convert phrases to target locale versions (Default: False)',
        '将短语转换为目标地区版本（默认：False）', '將片語轉換為目標地區版本（預設：False）'),
    'Set to Western or East Asian (Default: no_change)': _T(
        'Set to Western or East Asian (Default: no_change)',
        '设置为西式或东亚引号（默认：no_change）', '設定為西式或東亞引號（預設：no_change）'),
    'Set to the ebook origin locale if known (Default: no_change)': _T(
        'Set to the ebook origin locale if known (Default: no_change)',
        '设置文字方向（默认：no_change）', '設定文字方向（預設：no_change）'),
    'Update punctuation to match direction change (Default: False)': _T(
        'Update punctuation to match direction change (Default: False)',
        '更新标点以匹配方向更改（默认：False）', '更新標點以符合方向變更（預設：False）'),
    'Print out details as the conversion progresses (Default: False)': _T(
        'Print out details as the conversion progresses (Default: False)',
        '在转换过程中打印详情（默认：False）', '在轉換過程中印出詳情（預設：False）'),
    'Run conversion operations without saving results (Default: False)': _T(
        'Run conversion operations without saving results (Default: False)',
        '运行转换但不保存结果（默认：False）', '執行轉換但不儲存結果（預設：False）'),
    'Do not print anything, ignore warnings - this option overrides the -s option (Default: False)': _T(
        'Do not print anything, ignore warnings - this option overrides the -s option (Default: False)',
        '不打印任何内容，忽略警告（覆盖 -s 选项，默认：False）',
        '不印出任何內容，忽略警告（覆寫 -s 選項，預設：False）'),
    'Set to the ebook output file directory (Default: overwrite existing ebook file)': _T(
        'Set to the ebook output file directory (Default: overwrite existing ebook file)',
        '设置电子书输出目录（默认：覆盖原文件）', '設定電子書輸出目錄（預設：覆寫原檔案）'),
    'Append a suffix to the output file basename (Default: )': _T(
        'Append a suffix to the output file basename (Default: )',
        '为输出文件主名添加后缀（默认：空）', '為輸出檔案主檔名新增後綴（預設：空）'),
    'Force processing by ignoring warnings (e.g. allow overwriting files with no prompt)': _T(
        'Force processing by ignoring warnings (e.g. allow overwriting files with no prompt)',
        '强制处理并忽略警告（例如允许无提示覆盖文件）',
        '強制處理並忽略警告（例如允許無提示覆寫檔案）'),
    'Show the settings based on user cmdline options and exit (Default: False)': _T(
        'Show the settings based on user cmdline options and exit (Default: False)',
        '显示根据命令行选项得出的设置并退出（默认：False）',
        '顯示根據命令列選項得出的設定並結束（預設：False）'),
    'One or more epub and/or azw3 ebook filepaths - UNIX style wildcards accepted': _T(
        'One or more epub and/or azw3 ebook filepaths - UNIX style wildcards accepted',
        '一个或多个 epub 和/或 azw3 电子书路径（支持 UNIX 通配符）',
        '一個或多個 epub 和/或 azw3 電子書路徑（支援 UNIX 萬用字元）'),
    'Output directory not found': _T(
        'Output directory not found', '未找到输出目录', '未找到輸出目錄'),
    'Multiple output directory not found - only one allowed:': _T(
        'Multiple output directory not found - only one allowed:',
        '找到多个输出目录——仅允许一个：', '找到多個輸出目錄——僅允許一個：'),
    'Output directory not a directory': _T(
        'Output directory not a directory', '输出路径不是目录', '輸出路徑不是目錄'),
    'Discarding - Not a file: ': _T(
        'Discarding - Not a file: ', '已丢弃——不是文件：', '已捨棄——不是檔案：'),
    "Discarding - Does not end in '.epub' or '.azw3': ": _T(
        "Discarding - Does not end in '.epub' or '.azw3': ",
        "已丢弃——扩展名不是 '.epub' 或 '.azw3'：",
        "已捨棄——副檔名不是 '.epub' 或 '.azw3'："),
    'The input/output/direction combination selected is not supported.\n Please use a different input/output/direction combination': _T(
        'The input/output/direction combination selected is not supported.\n Please use a different input/output/direction combination',
        '所选输入/输出/方向组合不受支持。\n请使用其他组合。',
        '所選輸入/輸出/方向組合不受支援。\n請使用其他組合。'),
    'No hanzi conversion': _T('No hanzi conversion', '不进行汉字转换', '不進行漢字轉換'),
    'Using opencc-python conversion configuration file: ': _T(
        'Using opencc-python conversion configuration file: ',
        '使用 opencc-python 转换配置文件：', '使用 opencc-python 轉換設定檔：'),
    'No output directory specified, original ebook file will be overwritten. Is this OK? [N] or Y: ': _T(
        'No output directory specified, original ebook file will be overwritten. Is this OK? [N] or Y: ',
        '未指定输出目录，将覆盖原电子书文件。是否继续？[N] 或 Y：',
        '未指定輸出目錄，將覆寫原電子書檔案。是否繼續？[N] 或 Y：'),
    'Exiting without changes': _T('Exiting without changes', '退出，未做任何更改', '結束，未做任何變更'),
    'No ebook files specified!': _T('No ebook files specified!', '未指定电子书文件！', '未指定電子書檔案！'),
    'Converting ebook: ': _T('Converting ebook: ', '正在转换电子书：', '正在轉換電子書：'),
    'Changed': _T('Changed', '已更改', '已變更'),
    'Unchanged - No file written': _T(
        'Unchanged - No file written', '未更改——未写入文件', '未變更——未寫入檔案'),
    '   Overwriting file with changes: ': _T(
        '   Overwriting file with changes: ', '   正在用更改覆盖文件：', '   正在用變更覆寫檔案：'),
    '   --- TEST MODE - No Changes Written': _T(
        '   --- TEST MODE - No Changes Written', '   --- 测试模式——未写入更改', '   --- 測試模式——未寫入變更'),
    '   Saving file to: ': _T('   Saving file to: ', '   正在保存到：', '   正在儲存到：'),
    'Chinese Text Conversion': _T(
        'Chinese Text Conversion', '简繁中文转换', '簡繁中文轉換'),
    'No library open': _T('No library open', '未打开书库', '未開啟書庫'),
    'Open a calibre library first.': _T(
        'Open a calibre library first.', '请先打开 Calibre 书库。', '請先開啟 Calibre 書庫。'),
    'No books selected': _T('No books selected', '未选中书籍', '未選取書籍'),
    'Select one or more books in the library, then run Chinese Conversion.': _T(
        'Select one or more books in the library, then run Chinese Conversion.',
        '在书库中选中一本或多本书，然后运行中文转换。',
        '在書庫中選取一本或多本書，然後執行中文轉換。'),
    'No conversion options were selected.': _T(
        'No conversion options were selected.', '未选择任何转换选项。', '未選擇任何轉換選項。'),
    'Skipped (no EPUB/AZW3):': _T(
        'Skipped (no EPUB/AZW3):', '已跳过（无 EPUB/AZW3）：', '已略過（無 EPUB/AZW3）：'),
    'Conversion complete': _T('Conversion complete', '转换完成', '轉換完成'),
    'Converted text in one book:': _T(
        'Converted text in one book:', '已转换 1 本书中的文字：', '已轉換 1 本書中的文字：'),
    'Converted text in {} books:': _T(
        'Converted text in {} books:', '已转换 {} 本书中的文字：', '已轉換 {} 本書中的文字：'),
    'Failed to convert one or more books, click "Show details" for more info': _T(
        'Failed to convert one or more books, click "Show details" for more info',
        '有一本或多本书转换失败，点击“显示详情”了解更多信息',
        '有一本或多本書轉換失敗，點擊「顯示詳情」了解更多資訊'),
    'Convert traditional/simplified Chinese in selected books': _T(
        'Convert traditional/simplified Chinese in selected books',
        '转换所选书籍中的简繁中文',
        '轉換所選書籍中的簡繁中文'),
    'None of the selected books have an EPUB or AZW3 format.': _T(
        'None of the selected books have an EPUB or AZW3 format.',
        '所选书籍中没有 EPUB 或 AZW3 格式。',
        '所選書籍中沒有 EPUB 或 AZW3 格式。'),
    'The output configuration selected is not supported.\n Please use a different Input/Output Language Styles combination': _T(
        'The output configuration selected is not supported.\n'
        ' Please use a different Input/Output Language Styles combination',
        '所选输出配置不受支持。\n请使用其他输入/输出语言风格组合。',
        '所選輸出設定不受支援。\n請使用其他輸入/輸出語言風格組合。'),
    'About': _T('About', '关于', '關於'),
    'About Chinese Text Conversion': _T(
        'About Chinese Text Conversion', '关于简繁中文转换', '關於簡繁中文轉換'),
    'Version {}': _T('Version {}', '版本 {}', '版本 {}'),
    'About welcome first run': _T(
        'Welcome! This short guide appears once after you install the plugin. '
        'You can open it again anytime using About at the bottom left of the conversion window.',
        '欢迎使用！本说明在首次安装后显示一次。之后可随时在转换窗口左下角点击「关于」再次查看。',
        '歡迎使用！本說明在首次安裝後顯示一次。之後可隨時在轉換視窗左下角點擊「關於」再次查看。'),
    'About offline highlight': _T(
        'Offline by design: conversions use the OpenCC word lists shipped inside the plugin. '
        'No AI, no cloud service, and no internet connection is required.',
        '全程离线：使用插件内置的 OpenCC 字库进行转换，无需人工智能、无需联网。',
        '全程離線：使用外掛內建的 OpenCC 字庫進行轉換，無需人工智慧、無需連線。'),
    'About features': _T(
        'About features',
        '主要功能',
        '主要功能'),
    'About features list': _T(
        '• Traditional ↔ Simplified, plus regional Traditional wording (Mainland / Hong Kong / Taiwan)\n'
        '• Quotation marks, vertical/horizontal layout, and punctuation\n'
        '• Batch convert EPUB/AZW3 in the library; adds new books, originals unchanged\n'
        '• UI: English, Simplified Chinese, Traditional Chinese (Taiwan / Hong Kong)',
        '• 繁体 ↔ 简体，以及繁体地区用词互转（大陆 / 香港 / 台湾）\n'
        '• 引号样式、横竖排版与标点调整\n'
        '• 在书库中批量处理 EPUB / AZW3；生成新书，不修改原书\n'
        '• 界面可选 English / 简体中文 / 繁体（台湾）/ 繁体（香港）',
        '• 繁體 ↔ 簡體，以及繁體地區用詞互轉（大陸 / 香港 / 臺灣）\n'
        '• 引號樣式、橫豎排版與標點調整\n'
        '• 在書庫中批次處理 EPUB / AZW3；產生新書，不修改原書\n'
        '• 介面可選 English / 簡體中文 / 繁體（台灣）/ 繁體（香港）'),
    'About quick start': _T(
        'About quick start',
        '快速上手',
        '快速上手'),
    'About quick start steps': _T(
        '1. In Calibre, add this plugin to the main toolbar (Preferences → Toolbars & menus).\n'
        '2. Select one or more books (EPUB or AZW3) in your library.\n'
        '3. Click Chinese Conversion, choose options, then Start Processing.\n'
        '4. When finished, find the new copy in your library (title includes a time suffix).',
        '1. 在 Calibre「偏好设置 → 工具栏和菜单」中，把本插件加到主工具栏。\n'
        '2. 在书库选中一本或多本书（需为 EPUB 或 AZW3）。\n'
        '3. 点击「中文转换」，选好选项后点「开始处理」。\n'
        '4. 完成后在书库中查看新书（书名会带时间后缀，原书不变）。',
        '1. 在 Calibre「偏好設定 → 工具列和選單」中，把本外掛加到主工具列。\n'
        '2. 在書庫選取一本或多本書（需為 EPUB 或 AZW3）。\n'
        '3. 點擊「中文轉換」，選好選項後點「開始處理」。\n'
        '4. 完成後在書庫中查看新書（書名會帶時間後綴，原書不變）。'),
    'About lineage': _T(
        'Developed from Hopkins’ Chinese Text Conversion plugin for Calibre.\n'
        'https://github.com/Hopkins1/TradSimpChinese',
        '本插件在 Hopkins 的 Chinese Text Conversion（Calibre 简繁转换插件）基础上继续开发。\n'
        'https://github.com/Hopkins1/TradSimpChinese',
        '本外掛在 Hopkins 的 Chinese Text Conversion（Calibre 簡繁轉換外掛）基礎上繼續開發。\n'
        'https://github.com/Hopkins1/TradSimpChinese'),
    'Got it': _T('Got it', '知道了', '知道了'),
    'Please confirm the current book language is Chinese.': _T(
        'Please confirm the current book language is Chinese.',
        '请确认当前书籍语言为中文。',
        '請確認當前書籍語言為中文。'),
    'Language check': _T('Language check', '语言检查', '語言檢查'),
    'Continue': _T('Continue', '继续', '繼續'),
    'Book: {}\nLanguage: {}': _T(
        'Book: {}\nLanguage: {}',
        '书籍：{}\n语言：{}',
        '書籍：{}\n語言：{}'),
    'The following {} book(s) are not marked as Chinese:': _T(
        'The following {} book(s) are not marked as Chinese:',
        '以下 {} 本书未标记为中文：',
        '以下 {} 本書未標記為中文：'),
}

_finalize_message_catalog()


def normalize_ui_language(lang_index):
    if lang_index in (UI_LANG_EN, UI_LANG_ZH_CN, UI_LANG_ZH_TW, UI_LANG_ZH_HK):
        return lang_index
    return detect_calibre_ui_language()


def ui_language_combo_items():
    return [
        _('English'),
        _('Simplified Chinese'),
        _('Traditional Chinese (Taiwan)'),
        _('Traditional Chinese (Hong Kong)'),
    ]


def set_ui_language(lang_index):
    global _current_ui_lang
    _current_ui_lang = normalize_ui_language(lang_index)


def get_ui_language():
    return _current_ui_lang


def detect_calibre_ui_language():
    '''Map Calibre GUI language to plugin UI language (EN / zh_CN / zh_TW / zh_HK).'''
    try:
        from calibre.utils.localization import get_lang
        lang = (get_lang() or '').replace('-', '_').lower()
    except Exception:
        return UI_LANG_EN
    if lang in ('zh_cn', 'zh_sg', 'zh'):
        return UI_LANG_ZH_CN
    if lang in ('zh_hk', 'zh_mo'):
        return UI_LANG_ZH_HK
    if lang in ('zh_tw',):
        return UI_LANG_ZH_TW
    if lang == 'zh_hant':
        return UI_LANG_ZH_TW
    if lang.startswith('zh'):
        return UI_LANG_ZH_CN
    return UI_LANG_EN


def apply_ui_language_from_prefs(prefs):
    lang = normalize_ui_language(prefs.get('ui_language', detect_calibre_ui_language()))
    set_ui_language(lang)


def _(message):
    entry = _MESSAGES.get(message)
    if entry is None:
        return message
    return entry.get(_current_ui_lang, message)


def ngettext(singular, plural, n):
    '''Plugin-catalog plural strings (English / 简体 / 繁体台湾 / 繁体香港).'''
    if n == 1:
        return _(singular)
    return _(plural)
