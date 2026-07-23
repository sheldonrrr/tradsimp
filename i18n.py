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
    'Chinese Conversion': _T('Chinese Conversion', '简繁中文转换', '簡繁中文轉換'),
    # Plugin catalog metadata (English defaults; mirrors __init__.py for Calibre / MobileRead)
    'Plugin catalog name': _T(
        'Chinese Conversion',
        'Chinese Conversion · 简繁转换',
        'Chinese Conversion · 簡繁轉換'),
    'Plugin catalog description': _T(
        'Fully offline conversion between Simplified and Traditional Chinese. '
        'Community-maintained version powered by OpenCC.',
        '简体与繁体中文之间的完全离线转换。基于 OpenCC 的社区维护版本。',
        '簡體與繁體中文之間的完全離線轉換。基於 OpenCC 的社群維護版本。'),
    'Plugin catalog author': _T(
        'Sheldon (community fork of Hopkins1)',
        'Sheldon（Hopkins1 社区分支维护）',
        'Sheldon（Hopkins1 社群分支維護）'),
    'Plugin catalog released': _T(
        'Released: 22 Jul, 2026',
        '发布：2026年7月22日',
        '發佈：2026年7月22日'),
    'Plugin catalog calibre requirement': _T(
        'Requires calibre 6.0.0 or later',
        '需要 calibre 6.0.0 或更高版本',
        '需要 calibre 6.0.0 或更高版本'),
    'Plugin catalog platforms': _T(
        'Platforms: linux, osx, windows',
        '平台：linux、osx、windows',
        '平台：linux、osx、windows'),
    'Brand dialog tagline': _T(
        'Fully offline conversion between Simplified and Traditional Chinese',
        '简体与繁体中文完全离线转换',
        '簡體與繁體中文完全離線轉換'),
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
    'Conversion Direction': _T('Set conversion direction', '设置转换方向', '設定轉換方向'),
    'No Conversion': _T('No Conversion', '不转换', '不轉換'),
    'Traditional to Simplified': _T('Traditional to Simplified', '繁体转简体', '繁體轉簡體'),
    'Simplified to Traditional': _T('Simplified to Traditional', '简体转繁体', '簡體轉繁體'),
    'Traditional to Traditional': _T('Traditional to Traditional', '繁体转繁体', '繁體轉繁體'),
    'Traditional to Traditional help': _T(
        'Still traditional Chinese; adjusts character forms between regional varieties '
        '(Mainland, Hong Kong, Taiwan), including Hong Kong ↔ Taiwan.',
        '仍是繁体字，在不同地区繁体之间调整字形习惯（大陆/香港/台湾），含香港与台湾互转。',
        '仍是繁體字，在不同地區繁體之間調整字形習慣（大陸/香港/臺灣），含香港與臺灣互轉。'),
    'Language Styles': _T('Set language styles', '设置语言风格', '設定語言風格'),
    'Input:': _T('Input:', '输入：', '輸入：'),
    'Output:': _T('Output:', '输出：', '輸出：'),
    'Mainland': _T(
        'Simplified Chinese (Mainland)',
        '简体中文（大陆）',
        '簡體中文（大陸）'),
    'Hong Kong': _T(
        'Traditional Chinese (Hong Kong)',
        '繁体中文（香港）',
        '繁體中文（香港）'),
    'Taiwan': _T(
        'Traditional Chinese (Taiwan)',
        '繁体中文（台湾）',
        '繁體中文（臺灣）'),
    'Japan': _T('Japan', '日本', '日本'),
    'Japanese Kanji': _T(
        'Japanese Kanji',
        '日本汉字',
        '日本漢字'),
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
    'Quotation Marks': _T('Set language symbols', '设置语言符号', '設定語言符號'),
    'Advanced options': _T('Advanced options', '高级选项', '進階選項'),
    'Text Direction:': _T('Set text direction:', '设置文字方向：', '設定文字方向：'),
    'Horizontal': _T('Left to right (horizontal)', '从左到右（横排）', '從左到右（橫排）'),
    'Vertical': _T('Top to bottom (vertical)', '从上到下（竖排）', '從上到下（直排）'),
    'Select the desired text orientation': _T(
        'Choose left-to-right or top-to-bottom reading order',
        '选择从左到右或从上到下的阅读顺序',
        '選擇從左到右或從上到下的閱讀順序'),
    'Update punctuation': _T('Update punctuation', '更新标点', '更新標點'),
    'Include metadata': _T(
        'Include metadata',
        '包含 Metadata 信息',
        '包含 Metadata 資訊'),
    'Include metadata help': _T(
        'Converts Title, Author(s), Tags, and Publisher in the calibre library and in the ebook’s '
        'OPF (Open Packaging Format) metadata.',
        '转换 calibre 书库与电子书 OPF（Open Packaging Format，开放包装格式）中的'
        '标题、作者、标签、出版商。',
        '轉換 calibre 書庫與電子書 OPF（Open Packaging Format，開放包裝格式）中的'
        '標題、作者、標籤、出版商。'),
    'Bilingual annotation': _T(
        'Bilingual annotation (keep original)',
        '双语批注（保留原文）',
        '雙語批註（保留原文）'),
    'Bilingual annotation help': _T(
        'Keeps the original characters in the ebook body and mounts the converted form as small text '
        'at the bottom-right of each changed phrase (immersive-translation style). Conversion still '
        'uses full-sentence OpenCC context to reduce ambiguity. Metadata is not annotated.',
        '正文保留原文字，仅在变化片段的右下角以小字挂载转换结果（沉浸式翻译风格）；'
        '仍按整句上下文做 OpenCC 转换以降低歧义。不应用于 Metadata。',
        '正文保留原文字，僅在變化片段的右下角以小字掛載轉換結果（沉浸式翻譯風格）；'
        '仍按整句上下文做 OpenCC 轉換以降低歧義。不套用於 Metadata。'),
    'Enable Vision OCR image enhancement': _T(
        'Enable Vision OCR image enhancement',
        '启用 Vision OCR 的图片增强功能',
        '啟用 Vision OCR 的圖片增強功能'),
    'Vision OCR unsupported': _T(
        'Vision OCR Unsupported',
        'Vision OCR 不受支持',
        'Vision OCR 不受支援'),
    'Vision OCR unsupported message': _T(
        'Vision OCR requires macOS 12 or later and a working local Vision Framework. OCR has been disabled for this conversion.',
        'Vision OCR 需要 macOS 12 或更高版本，并且本地 Vision Framework 可用。本次转换已禁用 OCR。',
        'Vision OCR 需要 macOS 12 或更高版本，且本機 Vision Framework 可用。本次轉換已停用 OCR。'),
    'Vision OCR language notice': _T(
        'Vision OCR Language Notice',
        'Vision OCR 语言支持提醒',
        'Vision OCR 語言支援提醒'),
    'Vision OCR language notice summary': _T(
        'The preferred OCR language is not currently available on this macOS device.',
        '当前设备缺少本次 OCR 识别所需的优先语言支持。',
        '目前裝置缺少本次 OCR 辨識所需的優先語言支援。'),
    'OCR language missing problem': _T(
        'Preferred OCR language ({}) is missing on this system.',
        '由于识别语言（{}）缺失，OCR 识别结果可能不稳定。',
        '由於辨識語言（{}）缺失，OCR 辨識結果可能不穩定。'),
    'OCR language missing suggestion': _T(
        'It is recommended to disable Vision OCR enhancement for this conversion.',
        '建议本次不要勾选 OCR 识别增强功能。',
        '建議本次不要勾選 OCR 辨識增強功能。'),
    'OCR language missing action': _T(
        'Open macOS Settings > General > Language & Region, add/download the required language pack, then retry OCR.',
        '前往 macOS「系统设置 > 通用 > 语言与地区」，添加并下载对应语言支持后再开启 OCR。',
        '前往 macOS「系統設定 > 一般 > 語言與地區」，新增並下載對應語言支援後再啟用 OCR。'),
    'Vision OCR large job notice': _T(
        'Large Vision OCR Job',
        '大量图片 OCR 提醒',
        '大量圖片 OCR 提醒'),
    'Vision OCR large job summary': _T(
        'Detected {} image(s). OCR may take a long time. Do you want to run OCR for this conversion?',
        '检测到 {} 张图片。OCR 可能耗时较长，是否对本次转换执行 OCR？',
        '偵測到 {} 張圖片。OCR 可能耗時較長，是否對本次轉換執行 OCR？'),
    'Vision OCR large job details': _T(
        'Choosing “Skip OCR” keeps the other conversion settings and disables OCR for this run only.',
        '选择“跳过 OCR”会保留其他转换设置，并且仅本次运行禁用 OCR。',
        '選擇「略過 OCR」會保留其他轉換設定，且僅本次執行停用 OCR。'),
    'Run OCR': _T('Run OCR', '执行 OCR', '執行 OCR'),
    'Skip OCR': _T('Skip OCR', '跳过 OCR', '略過 OCR'),
    'OCR notice problem line': _T(
        'Problem: {}',
        '问题：{}',
        '問題：{}'),
    'OCR notice suggestion line': _T(
        'Suggestion: {}',
        '建议：{}',
        '建議：{}'),
    'OCR notice action line': _T(
        'Action: {}',
        'Action：{}',
        'Action：{}'),
    'OCR disabled preview': _T(
        'OCR is disabled; no recognition preview is available.',
        'OCR 没有开启，暂无识别结果预览',
        'OCR 未啟用，暫無辨識結果預覽'),
    'OCR enabled but no preview': _T(
        'Vision OCR ran but no image text sample was captured.',
        'Vision OCR 已开启，但暂无可展示的识别样本。',
        'Vision OCR 已啟用，但暫無可顯示的辨識樣本。'),
    'OCR preview header': _T(
        'Recent OCR samples (latest 3):',
        '最近 3 条图片 OCR 结果：',
        '最近 3 筆圖片 OCR 結果：'),
    'OCR preview item': _T(
        '[{}] Image: {}',
        '[{}] 图片：{}',
        '[{}] 圖片：{}'),
    'OCR preview recognized': _T(
        'Recognized: {}',
        '识别结果：{}',
        '辨識結果：{}'),
    'OCR preview converted': _T(
        'Converted: {}',
        '转换结果：{}',
        '轉換結果：{}'),
    'No OCR sample text': _T(
        'No sample text',
        '无示例文本',
        '無示例文字'),
    'OCR summary line': _T(
        'OCR triggered: recognized {} image(s), generated {} text result(s). Samples: {}',
        'OCR 已触发：识别了 {} 张图片，汇总了 {} 个文字结果。示例：{}',
        'OCR 已觸發：辨識了 {} 張圖片，彙整了 {} 個文字結果。示例：{}'),
    'OCR summary images line': _T(
        'Image count: {}, names (up to 3): {}',
        '图片数量：{}，名称（最多 3 个）：{}',
        '圖片數量：{}，名稱（最多 3 個）：{}'),
    'OCR enabled but not used summary': _T(
        'OCR is enabled but was not used in this conversion (no eligible image text found).',
        'OCR 已开启，但本次未触发（未找到可处理的图片文字）。',
        'OCR 已啟用，但本次未觸發（未找到可處理的圖片文字）。'),
    'OCR enabled but no image resources summary': _T(
        'OCR is enabled but this EPUB package contains no image resources.',
        'OCR 已开启，但该 EPUB 包内未检测到图片资源。',
        'OCR 已啟用，但該 EPUB 套件內未偵測到圖片資源。'),
    'OCR enabled but no delta summary': _T(
        'OCR ran, but recognized text matches existing image descriptions so no file changes were needed.',
        'OCR 已执行，但识别结果与现有图片说明一致，因此未产生文件变更。',
        'OCR 已執行，但辨識結果與現有圖片說明一致，因此未產生檔案變更。'),
    'OCR executed with no content delta; creating a new copy for review.': _T(
        'OCR executed with no content delta; creating a new copy for review.',
        'OCR 已执行且内容无差异；仍将创建一本新副本供你复核。',
        'OCR 已執行且內容無差異；仍會建立一本新副本供你複核。'),
    'Settings...': _T('Settings...', '设置…', '設定…'),
    'Entire eBook': _T('Entire eBook', '整本电子书', '整本電子書'),
    'Current File': _T('Current File', '当前文件', '目前檔案'),
    'Tagged Text in Current File': _T('Tagged Text in Current File', '当前文件中的标记文本', '目前檔案中的標記文字'),
    '“Tagged Text” is bracketed by <!--PI_SELTEXT_START--> and <!--PI_SELTEXT_END-->': _T(
        '“Tagged Text” is bracketed by <!--PI_SELTEXT_START--> and <!--PI_SELTEXT_END-->',
        '“标记文本”由 <!--PI_SELTEXT_START--> 与 <!--PI_SELTEXT_END--> 括起',
        '「標記文字」由 <!--PI_SELTEXT_START--> 與 <!--PI_SELTEXT_END--> 括起'),
    'Source': _T('Set conversion source', '设置转换范围', '設定轉換範圍'),
    'Punctuation': _T('Punctuation', '标点', '標點'),
    'Clear All': _T('Clear All', '全部清除', '全部清除'),
    'Set All': _T('Set All', '全部选中', '全部選取'),
    'Default': _T('Default', '默认', '預設'),
    'Valid input/output combinations:\nNot Applicable': _T(
        'Valid input/output combinations:\nNot Applicable',
        '有效的输入/输出组合：\n不适用', '有效的輸入/輸出組合：\n不適用'),
    'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Mainland\nTaiwan/Mainland\nMainland/Japanese Kanji': _T(
        'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Mainland\nTaiwan/Mainland\nMainland/Japanese Kanji',
        '有效的输入/输出组合：\n香港/大陆\n大陆/大陆\n台湾/大陆\n大陆/日本汉字',
        '有效的輸入/輸出組合：\n香港/大陸\n大陸/大陸\n臺灣/大陸\n大陸/日本漢字'),
    'Valid input/output combinations:\nMainland/Hong Kong\nMainland/Mainland\nMainland/Taiwan\nJapanese Kanji/Mainland': _T(
        'Valid input/output combinations:\nMainland/Hong Kong\nMainland/Mainland\nMainland/Taiwan\nJapanese Kanji/Mainland',
        '有效的输入/输出组合：\n大陆/香港\n大陆/大陆\n大陆/台湾\n日本汉字/大陆',
        '有效的輸入/輸出組合：\n大陸/香港\n大陸/大陸\n大陸/臺灣\n日本漢字/大陸'),
    'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan\nHong Kong/Taiwan\nTaiwan/Hong Kong': _T(
        'Valid input/output combinations:\nHong Kong/Mainland\nMainland/Hong Kong\nTaiwan/Mainland\nMainland/Taiwan\nMainland/Mainland\nHong Kong/Hong Kong\nTaiwan/Taiwan\nHong Kong/Taiwan\nTaiwan/Hong Kong',
        '有效的输入/输出组合：\n香港/大陆\n大陆/香港\n台湾/大陆\n大陆/台湾\n大陆/大陆\n香港/香港\n台湾/台湾\n香港/台湾\n台湾/香港',
        '有效的輸入/輸出組合：\n香港/大陸\n大陸/香港\n臺灣/大陸\n大陸/臺灣\n大陸/大陸\n香港/香港\n臺灣/臺灣\n香港/臺灣\n臺灣/香港'),
    'Target phrases not available for Hong Kong ↔ Taiwan conversion. Only character variants are adjusted; regional wording is not swapped.': _T(
        'Target phrases not available for Hong Kong ↔ Taiwan conversion. Only character variants are adjusted; regional wording is not swapped.',
        '香港与台湾互转时不适用惯用词语选项。仅调整字形/变体，不进行两岸用词替换。',
        '香港與臺灣互轉時不適用慣用詞語選項。僅調整字形/變體，不進行兩岸用詞替換。'),
    'Convert Chinese Text Simplified/Traditional': _T(
        'Convert Chinese Simplified/Traditional', '简繁中文转换', '簡繁中文轉換'),
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
    'OCR progress': _T('OCR Progress', 'OCR 进度', 'OCR 進度'),
    'Processing progress': _T('Processing Progress', '处理进度', '處理進度'),
    'OCR progress status': _T(
        'OCR progress: {}/{} image(s)',
        'OCR 进度：已处理 {}/{} 张图片',
        'OCR 進度：已處理 {}/{} 張圖片'),
    'OCR completed status': _T(
        '{} image(s) OCR completed',
        '{} 张图片 OCR 已经处理完成',
        '{} 張圖片 OCR 已經處理完成'),
    'Result preview': _T('Result preview', '处理结果预览', '處理結果預覽'),
    'New books will be added to the library; original files are not modified.': _T(
        'New books will be added to the library; original files are not modified.',
        '将在书库中新建书籍，不会修改原书文件。',
        '將在書庫中新建書籍，不會修改原書檔案。'),
    'Processing ({}/{}): {}': _T(
        'Processing ({}/{}): {}', '正在处理（{}/{}）：{}', '正在處理（{}/{}）：{}'),
    'Current book progress label': _T(
        '{}/{} “{}”',
        '{}/{}《{}》',
        '{}/{}《{}》'),
    'Preparing background conversion…': _T(
        'Preparing background conversion…',
        '正在准备后台转换…',
        '正在準備背景轉換…'),
    'Background conversion is still running. You can reopen this window when processing completes.': _T(
        'Background conversion is still running. You can reopen this window when processing completes.',
        '后台转换仍在进行。处理完成后会重新显示此窗口。',
        '背景轉換仍在進行。處理完成後會重新顯示此視窗。'),
    'Hide': _T('Hide', '隐藏', '隱藏'),
    'Library conversion is already running.': _T(
        'Library conversion is already running.',
        '书库转换正在进行中。',
        '書庫轉換正在進行中。'),
    'No changes for “{}”; no new book created.': _T(
        'No changes for “{}”; no new book created.',
        '《{}》无可用更改，未创建新书。',
        '《{}》無可用變更，未建立新書。'),
    '—— {} ——': _T('—— {} ——', '—— {} ——', '—— {} ——'),
    'Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}\nSuffix: {}': _T(
        'Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}\nSuffix: {}',
        '原书：{}\n新书：{}\n书库编号：{}\n格式：{}\n后缀：{}',
        '原書：{}\n新書：{}\n書庫編號：{}\n格式：{}\n後綴：{}'),
    'Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}': _T(
        'Source: {}\nNew book: {}\nLibrary id: {}\nFormat: {}',
        '原书：{}\n新书：{}\n书库编号：{}\n格式：{}',
        '原書：{}\n新書：{}\n書庫編號：{}\n格式：{}'),
    'Saved file log line': _T(
        'Saved file: {}, save path: {}',
        '已保存文件：{}，保存路径：{}',
        '已儲存檔案：{}，儲存路徑：{}'),
    'Log conversion id: {}': _T(
        'Conversion id: {}',
        '转换标识：{}',
        '轉換識別：{}'),
    'Log generated at (local time): {}': _T(
        'Generated at (local time): {}',
        '生成时间（本地时间）：{}',
        '產生時間（本地時間）：{}'),
    'Log suffix time hint': _T(
        'The suffix ends with hour-minute-second (HH-MM-SS); it is not the plugin version.',
        '后缀末尾为时-分-秒（HH-MM-SS），用于区分同次转换的新书，并非插件版本号。',
        '後綴末尾為時-分-秒（HH-MM-SS），用於區分同次轉換的新書，並非外掛版本號。'),
    'Converted by Chinese Conversion · 简繁转换(for calibre) plugin': _T(
        'Converted by the “Chinese Conversion · 简繁转换(for calibre)” plugin',
        '由「Chinese Conversion · 简繁转换(for calibre)」插件转换',
        '由「Chinese Conversion · 簡繁轉換(for calibre)」外掛轉換'),
    'Plugin comments tagline': _T(
        'Supports horizontal/vertical layout conversion and Traditional ↔ Simplified Chinese. '
        'Fully offline — no large language models.',
        '插件支持横竖排转换、支持繁体中文和简体中文互转，完全离线，不调用大语言模型。',
        '外掛支援橫豎排轉換、支援繁體中文和簡體中文互轉，完全離線，不呼叫大型語言模型。'),
    '----Log book info begin----': _T(
        '----Book processing info begin----',
        '----本书处理信息开始----',
        '----本書處理資訊開始----'),
    '----Log book info end----': _T(
        '----Book processing info end----',
        '----本书处理信息结束----',
        '----本書處理資訊結束----'),
    '----Log preview begin----': _T(
        '----Preview result begin----',
        '----预览结果开始----',
        '----預覽結果開始----'),
    '----Log preview end----': _T(
        '----Preview result end----',
        '----预览结果结束----',
        '----預覽結果結束----'),
    '----Log replacements begin----': _T(
        '----Replacement statistics begin----',
        '----替换统计开始----',
        '----替換統計開始----'),
    '----Log replacements end----': _T(
        '----Replacement statistics end----',
        '----替换统计结束----',
        '----替換統計結束----'),
    'OpenCC replacements: {} hits, {} unique pairs': _T(
        'OpenCC replacements: {} hits, {} unique pairs',
        'OpenCC 替换：共 {} 处，{} 组不同词对',
        'OpenCC 替換：共 {} 處，{} 組不同詞對'),
    '… and {} more unique pairs not shown': _T(
        '… and {} more unique pairs not shown',
        '……另有 {} 组未列出',
        '……另有 {} 組未列出'),
    'No OpenCC replacements recorded for this book.': _T(
        'No OpenCC replacements recorded for this book.',
        '本书未记录 OpenCC 词汇替换。',
        '本書未記錄 OpenCC 詞彙替換。'),
    '----Log summary begin----': _T(
        '----Processing summary begin----',
        '----处理汇总开始----',
        '----處理彙總開始----'),
    '----Log summary end----': _T(
        '----Processing summary end----',
        '----处理汇总结束----',
        '----處理彙總結束----'),
    'Preview length limit: {} characters': _T(
        'Preview length limit: {} characters',
        '预览字数上限：{} 字',
        '預覽字數上限：{} 字'),
    'Preview truncated hint': _T(
        'Preview text was truncated at the limit above.',
        '预览正文已在上述字数处截断。',
        '預覽正文已在上述字數處截斷。'),
    'File: ': _T('File: ', '文件：', '檔案：'),
    'Changed files: ': _T('Changed files: ', '已更改文件：', '已變更檔案：'),
    'No text excerpt available.': _T(
        'No text excerpt available.', '无文字预览。', '無文字預覽。'),
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
    'Generally run as: calibre-debug --run-plugin "Chinese Conversion · 简繁转换" -- [options] ebook-filepath\n'
    'Plugin Version: ': _T(
        'Convert Chinese characters between traditional/simplified types and/or change text style.\n'
        'Generally run as: calibre-debug --run-plugin "Chinese Conversion · 简繁转换" -- [options] ebook-filepath\n'
        'Plugin Version: ',
        '在繁体/简体中文及其他文字样式之间转换。\n'
        '通常运行：calibre-debug --run-plugin "Chinese Conversion · 简繁转换" -- [选项] 电子书路径\n'
        '插件版本：',
        '在繁體/簡體中文及其他文字樣式之間轉換。\n'
        '通常執行：calibre-debug --run-plugin "Chinese Conversion · 简繁转换" -- [選項] 電子書路徑\n'
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
    'Keep original text with converted forms as bilingual annotations (Default: False)': _T(
        'Keep original text with converted forms as bilingual annotations (Default: False)',
        '保留原文并以双语批注显示转换结果（默认：False）',
        '保留原文並以雙語批註顯示轉換結果（預設：False）'),
    'Bilingual annotation: ': _T(
        'Bilingual annotation: ', '双语批注：', '雙語批註：'),
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
    'Chinese Conversion · 简繁转换': _T(
        'Chinese Conversion · 简繁转换', 'Chinese Conversion · 简繁转换', 'Chinese Conversion · 簡繁轉換'),
    'No library open': _T('No library open', '未打开书库', '未開啟書庫'),
    'Open a calibre library first.': _T(
        'Open a calibre library first.', '请先打开 Calibre 书库。', '請先開啟 Calibre 書庫。'),
    'No books selected': _T('No books selected', '未选中书籍', '未選取書籍'),
    'Select one or more books in the library, then run Chinese Conversion.': _T(
        'Select one or more books in the library, then run Chinese Conversion.',
        '在书库中选中一本或多本书，然后运行简繁中文转换。',
        '在書庫中選取一本或多本書，然後執行簡繁中文轉換。'),
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
    'Check for updates': _T('New version features ↗', '新版本功能 ↗', '新版本功能 ↗'),
    'About Chinese Conversion · 简繁转换': _T(
        'About Chinese Conversion · 简繁转换',
        '关于 Chinese Conversion · 简繁转换',
        '關於 Chinese Conversion · 簡繁轉換'),
    'Version {}': _T('Version {}', '版本 {}', '版本 {}'),
    'Version: {}': _T('Version: {}', '版本：{}', '版本：{}'),
    'Plugin description': _T(
        'Fully offline Simplified ↔ Traditional Chinese conversion for your calibre library (OpenCC). '
        'Adds new books; originals stay unchanged.',
        '离线简繁中文转换（OpenCC），在书库中批量处理并新增书籍，不修改原书。',
        '離線簡繁中文轉換（OpenCC），在書庫中批次處理並新增書籍，不修改原書。',
        '離線簡繁中文轉換（OpenCC），在書庫中批次處理並新增書籍，不修改原書。'),
    'About MobileRead link': _T(
        '<a href="{url}">MobileRead release thread</a>',
        '<a href="{url}">MobileRead 发布帖</a>',
        '<a href="{url}">MobileRead 發佈帖</a>',
        '<a href="{url}">MobileRead 發佈帖</a>'),
    'About last updated': _T(
        'Last updated: {}',
        '最后更新：{}',
        '最後更新：{}'),
    'About welcome first run': _T(
        'Quick start:\n'
        '1. Add Chinese Conversion to the main toolbar (Preferences → Toolbars & menus).\n'
        '2. Select one or more EPUB/AZW3 books in your library.\n'
        '3. Click the button, choose options, then Start Processing.\n'
        '4. When finished, open the new library entry (the original book is unchanged).',
        '快速上手：\n'
        '1. 在「偏好设置 → 工具栏和菜单」中将「简繁中文转换」加入主工具栏。\n'
        '2. 在书库中选中一本或多本 EPUB/AZW3 书籍。\n'
        '3. 点击插件按钮，选好选项后点「开始处理」。\n'
        '4. 完成后在书库中查看新书（原书不变）。',
        '快速上手：\n'
        '1. 在「偏好設定 → 工具列和選單」中將「簡繁中文轉換」加入主工具列。\n'
        '2. 在書庫中選取一本或多本 EPUB/AZW3 書籍。\n'
        '3. 點擊外掛按鈕，選好選項後點「開始處理」。\n'
        '4. 完成後在書庫中查看新書（原書不變）。',
        '快速上手：\n'
        '1. 在「偏好設定 → 工具列和選單」中將「簡繁中文轉換」加入主工具列。\n'
        '2. 在書庫中選取一本或多本 EPUB/AZW3 書籍。\n'
        '3. 點擊外掛按鈕，選好選項後點「開始處理」。\n'
        '4. 完成後在書庫中查看新書（原書不變）。'),
    'About offline highlight': _T(
        'Fully offline conversion powered by OpenCC — no AI, no cloud, no internet required.',
        '完全离线转换，基于 OpenCC — 无需 AI、无需云端、无需联网。',
        '完全離線轉換，基於 OpenCC — 無需 AI、無需雲端、無需連線。'),
    'About features': _T(
        'About features',
        '主要功能',
        '主要功能'),
    'About features list': _T(
        '• Traditional ↔ Simplified, plus regional Traditional wording (Mainland / Hong Kong / Taiwan)\n'
        '• Hong Kong ↔ Taiwan Traditional conversion; Hong Kong / Taiwan phrase modes where supported\n'
        '• Quotation marks, left-to-right / top-to-bottom layout, and punctuation\n'
        '• Batch convert EPUB/AZW3 in the library; adds new books, originals unchanged\n'
        '• Library conversion log shows OpenCC replacement statistics (top word pairs sampled)\n'
        '• OpenCC ver.1.4.1 dictionaries; UI: English, Simplified Chinese, Traditional (Taiwan / Hong Kong)',
        '• 繁体 ↔ 简体，以及繁体地区用词互转（大陆 / 香港 / 台湾）\n'
        '• 香港 ↔ 台湾繁体互转；简繁/繁简流程中支持香港、台湾惯用词语模式\n'
        '• 引号样式、从左到右/从上到下的排版与标点调整\n'
        '• 在书库中批量处理 EPUB / AZW3；生成新书，不修改原书\n'
        '• 书库转换日志展示 OpenCC 替换统计（高频词对取样）\n'
        '• OpenCC ver.1.4.1 词库；界面可选 English / 简体中文 / 繁体（台湾）/ 繁体（香港）',
        '• 繁體 ↔ 簡體，以及繁體地區用詞互轉（大陸 / 香港 / 臺灣）\n'
        '• 香港 ↔ 臺灣繁體互轉；簡繁/繁簡流程中支援香港、臺灣慣用詞語模式\n'
        '• 引號樣式、從左到右/從上到下的排版與標點調整\n'
        '• 在書庫中批次處理 EPUB / AZW3；產生新書，不修改原書\n'
        '• 書庫轉換日誌展示 OpenCC 替換統計（高頻詞對取樣）\n'
        '• OpenCC ver.1.4.1 詞庫；介面可選 English / 簡體中文 / 繁體（台灣）/ 繁體（香港）'),
    'About quick start': _T(
        'About quick start',
        '快速上手',
        '快速上手'),
    'About quick start steps': _T(
        '1. In calibre, add this plugin to the main toolbar (Preferences → Toolbars & menus).\n'
        '2. Select one or more books (EPUB or AZW3) in your library.\n'
        '3. Click Chinese Conversion, choose options, then Start Processing.\n'
        '4. When finished, find the new copy in your library (the original book is unchanged).',
        '1. 在 calibre「偏好设置 → 工具栏和菜单」中，把本插件加到主工具栏。\n'
        '2. 在书库选中一本或多本书（需为 EPUB 或 AZW3）。\n'
        '3. 点击「简繁中文转换」，选好选项后点「开始处理」。\n'
        '4. 完成后在书库中查看新书（原书不变）。',
        '1. 在 calibre「偏好設定 → 工具列和選單」中，把本外掛加到主工具列。\n'
        '2. 在書庫選取一本或多本書（需為 EPUB 或 AZW3）。\n'
        '3. 點擊「簡繁中文轉換」，選好選項後點「開始處理」。\n'
        '4. 完成後在書庫中查看新書（原書不變）。'),
    'About lineage': _T(
        'Developed from Hopkins’ Chinese Text Conversion plugin for calibre.\n'
        'This community fork (module: chinese_text_conversion) runs from the library toolbar; '
        'the original used the book editor plugin menu (module: chinese_text).\n'
        'https://github.com/Hopkins1/TradSimpChinese',
        '本插件在 Hopkins 的 Chinese Text Conversion（calibre 简繁转换插件）基础上继续开发。\n'
        '本社区维护版（模块名 chinese_text_conversion）从书库主工具栏启动；'
        '原版从编辑书籍的插件菜单启动（模块名 chinese_text）。\n'
        'https://github.com/Hopkins1/TradSimpChinese',
        '本外掛在 Hopkins 的 Chinese Text Conversion（calibre 簡繁轉換外掛）基礎上繼續開發。\n'
        '本社群維護版（模組名 chinese_text_conversion）從書庫主工具列啟動；'
        '原版從編輯書籍的外掛選單啟動（模組名 chinese_text）。\n'
        'https://github.com/Hopkins1/TradSimpChinese'),
    'About release': _T('Release', '发布', '發佈'),
    'About release body': _T(
        'Release thread:\n'
        'https://www.mobileread.com/forums/showthread.php?t=373788\n'
        'Catalog status: not yet listed in the official calibre plugin catalog.',
        '发布地址：\n'
        'https://www.mobileread.com/forums/showthread.php?t=373788\n'
        '索引状态：暂未进入 calibre 插件索引。',
        '發佈地址：\n'
        'https://www.mobileread.com/forums/showthread.php?t=373788\n'
        '索引狀態：暫未進入 calibre 外掛索引。'),
    'About maintainer': _T('Maintainer', '维护者', '維護者'),
    'About maintainer body': _T(
        'Sheldon (community fork of Hopkins1).\n'
        'Also maintains Ask AI Plugin — '
        'https://www.mobileread.com/forums/showthread.php?p=4547202#post4547202',
        'Sheldon（Hopkins1 社区分支维护）。\n'
        '同时在维护：Ask AI Plugin — '
        'https://www.mobileread.com/forums/showthread.php?p=4547202#post4547202',
        'Sheldon（Hopkins1 社群分支維護）。\n'
        '同時在維護：Ask AI Plugin — '
        'https://www.mobileread.com/forums/showthread.php?p=4547202#post4547202'),
    'About maintenance goals': _T(
        'Maintenance goals', '维护目标', '維護目標'),
    'About maintenance goals list': _T(
        '• Improve ease of use\n'
        '• Convert by adding new library books, without modifying originals\n'
        '• Library GUI toolbar plugin instead of a hard-to-find editor-only entry',
        '• 提升插件的易用性\n'
        '• 以新增书籍方式完成转换，不破坏原有文件\n'
        '• 从编辑模式中难以定位的入口，改为书库 GUI 插件，更加方便易于调用',
        '• 提升外掛的易用性\n'
        '• 以新增書籍方式完成轉換，不破壞原有檔案\n'
        '• 從編輯模式中難以定位的入口，改為書庫 GUI 外掛，更加方便易於呼叫'),
    'Got it': _T('Got it', '知道了', '知道了'),
    'About recommendations heading': _T(
        'Nowtiny calibre plugin recommendations',
        'Nowtiny calibre 插件推荐',
        'Nowtiny calibre 外掛推薦',
        'Nowtiny calibre 外掛推薦'),
    'About section divider': _T('---', '---', '---', '---'),
    'About recommendation Markdown title': _T(
        'Markdown (for calibre)',
        'Markdown（for calibre）',
        'Markdown（for calibre）',
        'Markdown（for calibre）'),
    'About recommendation Markdown desc': _T(
        'Calibre plugin · Python · offline\n'
        'Convert books to Markdown text files and export to a target folder.',
        'Calibre 插件 · Python · 离线\n'
        '将图书转换为 Markdown 文本文件并导出到指定目录。',
        'Calibre 外掛 · Python · 離線\n'
        '將圖書轉換為 Markdown 文字檔並匯出到指定目錄。',
        'Calibre 外掛 · Python · 離線\n'
        '將圖書轉換為 Markdown 文字檔並匯出到指定目錄。'),
    'About recommendation Ask AI title': _T(
        'Ask AI Plugin (for calibre)',
        'Ask AI Plugin（for calibre）',
        'Ask AI Plugin（for calibre）',
        'Ask AI Plugin（for calibre）'),
    'About recommendation Ask AI desc': _T(
        'Calibre plugin · Python\n'
        'Ask AI questions while reading and managing ebooks.',
        'Calibre 插件 · Python\n'
        '在阅读与管理电子书时进行 AI 问答。',
        'Calibre 外掛 · Python\n'
        '在閱讀與管理電子書時進行 AI 問答。',
        'Calibre 外掛 · Python\n'
        '在閱讀與管理電子書時進行 AI 問答。'),
    'About recommendation Open button': _T(
        'MobileRead',
        'MobileRead',
        'MobileRead',
        'MobileRead'),
    'About MobileRead note': _T(
        'Note: MobileRead is the developer page for calibre plugin releases and more version updates.',
        '注：MobileRead 是 calibre 插件发布和更多版本更新信息的开发者页面。',
        '註：MobileRead 是 calibre 外掛發佈與更多版本更新資訊的開發者頁面。',
        '註：MobileRead 是 calibre 外掛發佈與更多版本更新資訊的開發者頁面。'),
    'About recommendations site link': _T(
        'Explore more on <a href="{url}">Nowtiny</a>',
        '在 <a href="{url}">Nowtiny</a> 查看更多工具',
        '在 <a href="{url}">Nowtiny</a> 查看更多工具',
        '在 <a href="{url}">Nowtiny</a> 查看更多工具'),
    'About Xiaohongshu feedback link': _T(
        '',
        '问题反馈：<a href="{url}">小红书</a>',
        '',
        ''),
    'Please confirm the current book language is Chinese or Japanese Kanji.': _T(
        'Please confirm the current book language is Chinese or Japanese Kanji.',
        '请确认当前书籍语言为中文或日本汉字。',
        '請確認目前書籍語言為中文或日本漢字。'),
    'Language check': _T('Language check', '语言检查', '語言檢查'),
    'Continue': _T('Continue', '继续', '繼續'),
    'Book: {}\nLanguage: {}\nYou can still continue if this book contains Chinese or Japanese Kanji text.': _T(
        'Book: {}\nLanguage: {}\nYou can still continue if this book contains Chinese or Japanese Kanji text.',
        '书籍：{}\n语言：{}\n如果这本书包含中文或日本汉字内容，仍可继续处理。',
        '書籍：{}\n語言：{}\n如果這本書包含中文或日本漢字內容，仍可繼續處理。'),
    'The following {} book(s) are not marked as Chinese or Japanese:': _T(
        'The following {} book(s) are not marked as Chinese or Japanese:',
        '以下 {} 本书未标记为中文或日文：',
        '以下 {} 本書未標記為中文或日文：'),
    'The following {} book(s) are not marked as Chinese or Japanese and will be skipped:': _T(
        'The following {} book(s) are not marked as Chinese or Japanese and will be skipped:',
        '以下 {} 本书未标记为中文或日文，将被跳过：',
        '以下 {} 本書未標記為中文或日文，將被略過：'),
    'Some selected books are not marked as Chinese or Japanese.': _T(
        'Some selected books are not marked as Chinese or Japanese.',
        '部分所选书籍未标记为中文或日文。',
        '部分所選書籍未標記為中文或日文。'),
    'Skip listed books': _T('Skip listed books', '跳过列出的书籍', '略過列出的書籍'),
    'Skipped (language not Chinese/Japanese):': _T(
        'Skipped (language not Chinese/Japanese):',
        '已跳过（语言不是中文/日文）：',
        '已略過（語言不是中文/日文）：'),
    'All selected books were skipped by language check.': _T(
        'All selected books were skipped by language check.',
        '所有所选书籍都已因语言检查被跳过。',
        '所有所選書籍都已因語言檢查被略過。'),
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
