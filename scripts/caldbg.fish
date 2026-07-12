# tradsimp — Calibre 本地调试（fish）
# 用法（任选其一）：
#   source scripts/caldbg.fish
#   soufish                    # 若已在 ~/.config/fish/config.fish 中 source 本文件
#   ~/tradsimp/bin/caldbg-tsc-ag   # 任意 shell 可直接运行
# 本机可选覆盖：
#   set -gx TRADSIMP_CALIBRE_BIN /Applications/calibre.app/Contents/MacOS
#   set -gx TRADSIMP_ROOT ~/tradsimp

test -n "$FISH_VERSION" || echo "scripts/caldbg.fish is fish-only. Run: fish, then source ~/tradsimp/scripts/caldbg.fish"
test -n "$FISH_VERSION" || return 0 2>/dev/null || exit 0

function __tradsimp_caldbg_anchor; end
set -l _caldbg_fish (functions --details __tradsimp_caldbg_anchor)
functions -e __tradsimp_caldbg_anchor
if set -q TRADSIMP_ROOT; and test -f "$TRADSIMP_ROOT/__init__.py"
    set -gx TRADSIMP_ROOT (path resolve -- "$TRADSIMP_ROOT")
else if test -f "$_caldbg_fish"
    set -gx TRADSIMP_ROOT (path dirname -- (path dirname -- (path resolve -- $_caldbg_fish)))
else
    set -gx TRADSIMP_ROOT (path resolve -- .)
end

if test -f "$TRADSIMP_ROOT/scripts/caldbg.local.fish"
    source "$TRADSIMP_ROOT/scripts/caldbg.local.fish"
end

function __tradsimp_add_calibre_path
    set -l candidates
    if set -q TRADSIMP_CALIBRE_BIN
        set -a candidates "$TRADSIMP_CALIBRE_BIN"
    end
    set -a candidates /Applications/calibre.app/Contents/MacOS /opt/calibre

    for candidate in $candidates
        if test -x "$candidate/calibre-customize"
            fish_add_path -m "$candidate"
            return 0
        end
    end
    return 1
end

if not type -q calibre-customize
    __tradsimp_add_calibre_path
end

function soufish
    source "$TRADSIMP_ROOT/scripts/caldbg.fish"
end

function __tradsimp_check_dir
    if test -z "$TRADSIMP_ROOT"
        echo "错误: TRADSIMP_ROOT 为空"
        return 1
    end
    if not test -f "$TRADSIMP_ROOT/__init__.py"
        echo "错误: 插件目录无效: $TRADSIMP_ROOT"
        return 1
    end
    echo "tradsimp 目录: $TRADSIMP_ROOT"
end

function __tradsimp_install_plugin
    __tradsimp_check_dir; or return 1
    set -l plugin_name "Chinese Conversion · 简繁转换"
    calibre-customize -r "$plugin_name" 2>/dev/null
    calibre-customize -b "$TRADSIMP_ROOT"; or return 1
    set -l list_output (calibre-customize -l 2>/dev/null)
    set -l lines (string match '*Chinese Conversion · 简繁转换*' -- $list_output)
    if test (count $lines) -eq 0
        echo "警告: calibre-customize -l 中未找到 Chinese Conversion · 简繁转换"
        return 1
    end
    set -l line $lines[1]
    echo $line
    # Edit book tool（en / zh / zh-TW）— 不会出现在主工具栏
    if string match -qr '(?i)edit book tool|编辑书籍|編輯書籍' -- $line
        echo "警告: 仍是 Edit book tool，不会出现在 The main toolbar"
        return 1
    end
    echo "OK: 插件已安装 — 在 Toolbars & menus 搜索 Chinese / Chinese Conversion"
    return 0
end

function caldbg-env
    echo "TRADSIMP_ROOT=$TRADSIMP_ROOT"
    if set -q TRADSIMP_CALIBRE_BIN
        echo "TRADSIMP_CALIBRE_BIN=$TRADSIMP_CALIBRE_BIN"
    end
    echo "calibre-customize="(command -v calibre-customize 2>/dev/null)
    echo "calibre-debug="(command -v calibre-debug 2>/dev/null)
end

function caldbg-tsc
    __tradsimp_install_plugin; or return 1
    calibre-debug --gui
end

function caldbg-tsc-ag
    calibre-debug -s
    __tradsimp_install_plugin; or return 1
    calibre-debug --gui
end

function caldbg-tsc-p
    __tradsimp_check_dir; or return 1
    cd "$TRADSIMP_ROOT"
    python3 setup.py -b
    set -l zip (find ./dist -maxdepth 1 -name 'chinese_text_conversion-*.zip' 2>/dev/null | sort -r | head -1)
    if test -z "$zip"
        echo "未找到 dist/chinese_text_conversion-*.zip"
        return 1
    end
    calibre-customize -r "Chinese Conversion · 简繁转换" 2>/dev/null
    if not string match -q '/*' -- $zip
        set zip "$TRADSIMP_ROOT/$zip"
    end
    calibre-customize -a "$zip"
    calibre-customize -l 2>/dev/null | string match '*Chinese Conversion · 简繁转换*'
    calibre-debug --gui
end

function caldbg-tsc-pag
    calibre-debug -s
    caldbg-tsc-p
end

echo "tradsimp — source scripts/caldbg.fish"
echo "  soufish         重新 source 本文件"
echo "  caldbg-env      显示本机调试路径"
echo "  caldbg-tsc      源码安装 + 启动"
echo "  caldbg-tsc-ag   结束旧进程 + 源码安装 + 启动"
echo "  caldbg-tsc-p    打包 dist + 安装 zip + 启动"
echo "  caldbg-tsc-pag  同 caldbg-tsc-p，但先结束旧进程"
