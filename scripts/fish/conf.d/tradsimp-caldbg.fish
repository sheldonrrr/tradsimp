# tradsimp — 自动加载 Calibre 本地调试命令（caldbg-tsc-ag 等）
# 安装：ln -sf ~/tradsimp/scripts/fish/conf.d/tradsimp-caldbg.fish ~/.config/fish/conf.d/

function __tradsimp_conf_anchor; end
set -l _tradsimp_conf (functions --details __tradsimp_conf_anchor)
functions -e __tradsimp_conf_anchor
# .../tradsimp/scripts/fish/conf.d/tradsimp-caldbg.fish → 上跳 4 层到仓库根
set -l _tradsimp_root (path dirname -- (path dirname -- (path dirname -- (path dirname -- (path resolve -- $_tradsimp_conf)))))

if set -q TRADSIMP_ROOT; and test -f "$TRADSIMP_ROOT/scripts/caldbg.fish"
    set _tradsimp_root $TRADSIMP_ROOT
end

if test -f "$_tradsimp_root/scripts/caldbg.fish"
    # 静默加载函数；需要看用法时执行 soufish
    source "$_tradsimp_root/scripts/caldbg.fish" >/dev/null
    fish_add_path -m "$_tradsimp_root/bin"
end
