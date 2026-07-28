**語言：** [English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

# tradsimp

**Chinese Conversion · 简繁转换** · 適用於 Calibre

面向 Calibre 書庫的繁簡中文轉換外掛：在本地完成字形與地區用詞轉換，**無需連網、不使用 AI**，全部依賴內建 **OpenCC** 離線字庫。

本儲存庫在 Hopkins 的 [Chinese Text Conversion](https://www.mobileread.com/forums/showthread.php?t=275572) 外掛基礎上繼續開發與維護。

**目前版本：3.7.0** · 適用於 Calibre 6.0 及以上 · 類型：**主書庫工具列動作**

---

## 下載與安裝

請在本儲存庫 **Releases** 頁面下載最新的 `chinese_text_conversion-x.y.z.zip`（位於建置產物 `dist/`），然後在 Calibre 中：

1. 開啟 **偏好設定 → 外掛 → 從檔案安裝外掛**，選取下載的 zip。
2. 依提示重新啟動 Calibre。
3. 開啟 **偏好設定 → 工具列與選單 → 主工具列**，搜尋 **Chinese Conversion**（中文轉換）並新增到工具列。

首次開啟轉換視窗時會顯示 **關於** 說明；之後可隨時在視窗左下角 **關於** 再次查看。

若升級後工具列找不到按鈕，或從舊版 import 名稱（`chinese_text`）升級，請先移除舊版再安裝：

```text
calibre-customize -r "Chinese Conversion · 简繁转换"
```

再透過 **從檔案安裝外掛** 安裝新 zip。

**自 3.2.0 起**外掛 Python 模組名稱由 `calibre_plugins.chinese_text` 改為 `calibre_plugins.chinese_text_conversion`（與 zip 檔名 `chinese_text_conversion-*.zip` 一致）。升級前務必解除安裝舊版；已儲存的轉換偏好（`plugins/chinese_text_conversion_ChineseConversion_settings`）通常可保留，但工具列按鈕需重新新增。

---

## 能做什麼

- **繁體 ↔ 簡體**，以及**繁體地區互轉**（大陸 / 香港 / 台灣用詞習慣）
- **引號**（西式 / 東亞）、**橫豎排版**與**標點**調整
- 在書庫中處理 **EPUB / AZW3**：轉換後**新增一本書**，**不修改**你原來的檔案
- 介面語言：**English**、**简体中文**、**繁体中文（台湾）**、**繁体中文（香港）**
- 轉換預設使用 OpenCC **mmseg** 分詞（與上游 OpenCC 對齊）；可選實驗性 **Jieba** 分詞選項，有助於提升部分文本的詞組轉換準確度（首次啟用載入詞典可能稍慢）

### 為什麼放心用：全程離線

轉換過程在您的電腦上完成，使用外掛自帶的 OpenCC 詞典與規則，**不呼叫任何線上介面或人工智慧服務**，沒有書稿上傳，適合注重隱私與穩定性的使用者。

---

## 怎麼用（書庫）

1. 在 Calibre 書庫中選取一本或多本書（需包含 EPUB 或 AZW3）。
2. 點擊工具列上的 **Chinese Conversion** / **中文轉換**。
3. 在對話框中選擇轉換方向、語言風格等（可先閱讀左下角 **關於**）。
4. 點開始後，等待處理結束。
5. 在書庫中按日期排序或搜尋，找到書名帶時間後綴的**新書**（原書仍在）。

預設快速鍵：`Ctrl+Shift+Alt+C`（可在 Calibre **偏好設定 → 鍵盤快速鍵** 中修改）。

---

## 從原始碼建置

在儲存庫根目錄執行：

```bash
python3 setup.py -b
```

會在 `dist/` 下產生 `chinese_text_conversion-{version}.zip`（例如 `dist/chinese_text_conversion-3.6.0.zip`）。安裝方式：

```bash
calibre-customize -a "dist/chinese_text_conversion-3.6.0.zip"
```

其他常用命令：

```bash
python3 setup.py          # 建置 zip 並列印安裝提示
python3 setup.py -d       # 建置、安裝 zip、啟動 Calibre 圖形介面
python3 setup.py -s       # 從原始碼目錄安裝（不打包 zip）並啟動圖形介面
```

---

## 本地開發（macOS / fish）

`scripts/caldbg.fish` 可在 macOS 上設定 Calibre 路徑，並提供安裝與啟動的快捷命令：

```fish
source scripts/caldbg.fish
```

| 命令 | 說明 |
|------|------|
| `caldbg-tsc` | 從原始碼安裝並啟動圖形介面 |
| `caldbg-tsc-ag` | 結束舊 Calibre 行程後，從原始碼安裝並啟動 |
| `caldbg-tsc-p` | 打包（`python3 setup.py -b`）、安裝 zip、啟動圖形介面 |
| `caldbg-tsc-pag` | 同 `caldbg-tsc-p`，但先結束舊行程 |

---

## 授權

- 外掛程式碼：[GPL v3](LICENSE)
- OpenCC 資料與 opencc-python 元件：Apache License 2.0（見 `resources/opencc_python/`）
- 可選 Jieba 分詞：MIT（精簡內建副本見 `resources/jieba/`，基於 [fxsjy/jieba](https://github.com/fxsjy/jieba) v0.42.1）
