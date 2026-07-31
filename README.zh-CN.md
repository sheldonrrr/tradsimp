**语言：** [English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md)

# tradsimp

**Chinese Conversion · 简繁转换** · 适用于 Calibre

面向 Calibre 的简繁中文转换插件：电子书转换在本地使用内置 **OpenCC** 字库完成；另提供可选的**繁化姬在线短文本工具**，仅处理用户手动输入的片段，不读取或上传书籍。

本仓库在 Hopkins 的 [Chinese Text Conversion](https://www.mobileread.com/forums/showthread.php?t=275572) 插件基础上继续开发与维护。

**当前版本：3.9.1** · 适用于 Calibre 6.0 及以上 · 类型：**主书库工具栏动作**

---

## 下载与安装

请在本仓库 **Releases** 页面下载最新的 `chinese_text_conversion-x.y.z.zip`（位于构建产物 `dist/`），然后在 Calibre 中：

1. 打开 **偏好设置 → 插件 → 从文件安装插件**，选择下载的 zip。
2. 按提示重启 Calibre。
3. 打开 **偏好设置 → 工具栏和菜单 → 主工具栏**，搜索 **Chinese Conversion**（中文转换）并添加到工具栏。

首次打开转换窗口时会显示 **关于** 说明；之后可随时在窗口左下角 **关于** 再次查看。

若升级后工具栏找不到按钮，或从旧版 import 名（`chinese_text`）升级，请先移除旧版再安装：

```text
calibre-customize -r "Chinese Conversion · 简繁转换"
```

再通过 **从文件安装插件** 安装新 zip。

**3.2.0 起**插件 Python 模块名由 `calibre_plugins.chinese_text` 改为 `calibre_plugins.chinese_text_conversion`（与 zip 文件名 `chinese_text_conversion-*.zip` 一致）。升级前务必卸载旧版；已保存的转换偏好（`plugins/chinese_text_conversion_ChineseConversion_settings`）通常可保留，但工具栏按钮需重新添加。

---

## 能做什么

- **繁体 ↔ 简体**，以及**繁体地区互转**（大陆 / 香港 / 台湾用词习惯）
- **引号**（西式 / 东亚）、**横竖排版**与**标点**调整
- 在书库中处理 **EPUB / AZW3**：转换后**新增一本书**，**不修改**你原来的文件
- 界面语言：**English**、**简体中文**、**繁体中文（台湾）**、**繁体中文（香港）**
- 转换默认使用 OpenCC **mmseg** 分词（与上游 OpenCC 对齐）；可选实验性 **Jieba** 分词选项，有助于提升部分文本的词组转换准确度（首次启用加载词典可能稍慢）
- **强制转换（覆盖优先）**会先把混合简繁文本统一到简体枢轴，再重建所选繁体；它只使用内置 OpenCC 规则，能扩大转换面积，但可能牺牲地区用词精度，并不等同于错别字校对。此选项必须配合双语批注，以便在下方保留原文；新安装时两个选项均默认开启。
- 新生成的书籍默认增加识别后缀，例如 `_繁体中文_香港_双语标注_07-29_21-34`；末尾记录本地月、日、小时和分钟，同一分钟生成多本时依次增加 `_2`、`_3`。可在高级选项中关闭此后缀。
- 工具栏按钮菜单另提供可选的**繁化姬在线短文本转换**窗口，支持简体、繁体、中国、香港、台湾及 Wiki 简繁模式。

### 隐私与在线功能

电子书转换仍在您的电脑上使用内置 OpenCC 词典与规则完成，不调用在线接口，也不上传书籍内容。只有您在可选的繁化姬窗口中手动输入并明确发送的文字才会离开电脑。

在线窗口使用第三方[繁化姬 API](https://zhconvert.org/)。其公开文档未说明文字留存方式，请勿提交隐私或敏感内容；繁化姬亦提示转换结果可能出错，正式使用前应人工校阅。本程序使用了繁化姬的 API 服务；繁化姬商用必须付费。

---

## 怎么用（书库）

1. 在 Calibre 书库里选中一本或多本书（需包含 EPUB 或 AZW3）。
2. 点击工具栏上的 **Chinese Conversion** / **中文转换**。
3. 在对话框中选择转换方向、语言风格等（可先阅读左下角 **关于**）。
4. 点开始后，等待处理结束。
5. 在书库中按日期排序或搜索，找到书名带时间后缀的**新书**（原书仍在）。

默认快捷键：`Ctrl+Shift+Alt+C`（可在 Calibre **偏好设置 → 键盘快捷键** 中修改）。

### 可选的在线短文本转换

打开工具栏按钮的菜单，选择**繁化姬在线短文本转换**。粘贴短篇纯文字、选择模式并明确点击发送；窗口会显示结果、使用的模块及服务器词库版本，不会修改任何书籍。

---

## 从源码构建

在仓库根目录执行：

```bash
python3 setup.py -b
```

会在 `dist/` 下生成 `chinese_text_conversion-{version}.zip`（例如 `dist/chinese_text_conversion-3.6.0.zip`）。安装方式：

```bash
calibre-customize -a "dist/chinese_text_conversion-3.6.0.zip"
```

其他常用命令：

```bash
python3 setup.py          # 构建 zip 并打印安装提示
python3 setup.py -d       # 构建、安装 zip、启动 Calibre 图形界面
python3 setup.py -s       # 从源码目录安装（不打包 zip）并启动图形界面
```

---

## 本地开发（macOS / fish）

`scripts/caldbg.fish` 可在 macOS 上配置 Calibre 路径，并提供安装与启动的快捷命令：

```fish
source scripts/caldbg.fish
```

| 命令 | 说明 |
|------|------|
| `caldbg-tsc` | 从源码安装并启动图形界面 |
| `caldbg-tsc-ag` | 结束旧 Calibre 进程后，从源码安装并启动 |
| `caldbg-tsc-p` | 打包（`python3 setup.py -b`）、安装 zip、启动图形界面 |
| `caldbg-tsc-pag` | 同 `caldbg-tsc-p`，但先结束旧进程 |

---

## 许可

- 插件代码：[GPL v3](LICENSE)
- OpenCC 数据与 opencc-python 组件：Apache License 2.0（见 `resources/opencc_python/`）
- 可选 Jieba 分词：MIT（精简内置副本见 `resources/jieba/`，基于 [fxsjy/jieba](https://github.com/fxsjy/jieba) v0.42.1）
