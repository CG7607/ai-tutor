#!/bin/bash
# ============================================================
#  AITutor 一键安装脚本 (macOS / Linux)
#  自动检测环境 → 创建虚拟环境 → 安装依赖 → 配置 API Key → 创建桌面 App
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🤖 AI导师 安装程序 v2.5               ║"
echo "║   基于多智能体协作的 AI 课程助教          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ---- 1. 检测 Python ----
echo "🔍 [1/5] 检测 Python 环境..."
PYTHON=""
for candidate in python3.11 python3.12 python3 python; do
    if command -v "$candidate" &>/dev/null; then
        ver=$("$candidate" --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
            PYTHON="$candidate"
            echo "   ✅ 找到 $candidate (版本 $ver)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "   ❌ 未找到 Python 3.11+"
    echo "      macOS: brew install python@3.12"
    exit 1
fi

# ---- 2. 创建虚拟环境 ----
echo ""
echo "📦 [2/5] 创建虚拟环境..."
if [ -d "$VENV_DIR" ]; then
    echo "   ⚠️  .venv 已存在，跳过创建。"
else
    "$PYTHON" -m venv "$VENV_DIR"
    echo "   ✅ 虚拟环境创建完成。"
fi
source "$VENV_DIR/bin/activate"

# ---- 3. 安装依赖 ----
echo ""
echo "📥 [3/5] 安装 Python 依赖..."

# 优先使用清华镜像（国内访问更快），失败则回退直连
MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"
if pip install -r "$SCRIPT_DIR/requirements.txt" -i "$MIRROR" --trusted-host pypi.tuna.tsinghua.edu.cn --quiet; then
    echo "   ✅ 依赖安装成功（清华镜像）。"
elif pip install -r "$SCRIPT_DIR/requirements.txt" --quiet; then
    echo "   ✅ 依赖安装成功（直连）。"
else
    echo "   ❌ 安装失败，请检查网络。"
    exit 1
fi

# ---- 4. 配置 API Key ----
echo ""
echo "🔑 [4/5] 配置 LLM API Key..."
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "   ⚠️  .env 已存在，跳过。"
else
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo ""
    read -p "   请输入 API Key（回车跳过）: " api_key
    if [ -n "$api_key" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/your-api-key-here/$api_key/" "$SCRIPT_DIR/.env"
        else
            sed -i "s/your-api-key-here/$api_key/" "$SCRIPT_DIR/.env"
        fi
        echo "   ✅ API Key 已写入"
    else
        echo "   📝 已生成模板，请稍后编辑 .env"
    fi
fi

# ---- 5. 创建桌面启动 App ----
echo ""
echo "🔗 [5/5] 创建桌面一键启动..."

DESKTOP_APP="$HOME/Desktop/AITutor.app"
rm -rf "$DESKTOP_APP"
rm -f "$HOME/Desktop/AITutor.command" 2>/dev/null

# A. 创建 .command 备用启动器（右键 → 打开 可用，无权限要求）
DESKTOP_CMD="$HOME/Desktop/AITutor.command"
cat > "$DESKTOP_CMD" << COMMANDFILE
#!/bin/bash
clear
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🤖 AI导师 一键启动                    ║"
echo "╚══════════════════════════════════════════╝"
echo ""
cd "$SCRIPT_DIR"
bash run.sh
COMMANDFILE
chmod +x "$DESKTOP_CMD"
xattr -cr "$DESKTOP_CMD" 2>/dev/null

# B. 创建 .app（AppleScript 方式，首次需允许自动化权限）
if command -v osacompile &>/dev/null; then
    osacompile -o "$DESKTOP_APP" \
        -e "tell application \"Terminal\"
            activate
            do script \"clear; echo ''; echo '╔══════════════════════════════════════════╗'; echo '║   🤖 AI导师 一键启动                    ║'; echo '╚══════════════════════════════════════════╝'; echo ''; cd '$SCRIPT_DIR'; bash run.sh\"
        end tell"

    xattr -cr "$DESKTOP_APP" 2>/dev/null
    codesign --force --sign - "$DESKTOP_APP" 2>/dev/null

    echo "   ✅ $DESKTOP_APP"
    echo "   ✅ $DESKTOP_CMD"
else
    echo "   ⚠️  osacompile 不可用，仅创建 .command"
    echo "   ✅ $DESKTOP_CMD"
fi

echo ""
echo "   ┌──────────────────────────────────────────┐"
echo "   │  🚀 启动方式（任选其一）                  │"
echo "   │                                          │"
echo "   │  方式一：双击 AITutor.app                │"
echo "   │    → 首次弹出权限框，点「允许」即可       │"
echo "   │    → 如被拒绝：系统设置 → 隐私 → 自动化   │"
echo "   │      找到 AITutor → 开启 Terminal ✅      │"
echo "   │                                          │"
echo "   │  方式二：右键 AITutor.command → 打开     │"
echo "   │    → 直接启动，无需额外授权               │"
echo "   └──────────────────────────────────────────┘"

# ---- 完成 ----
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🎉 安装完成！                         ║"
echo "║   双击 AITutor.app（首次需允许自动化） 🚀  ║"
echo "║   或右键 AITutor.command → 打开（免授权） ║"
echo "╚══════════════════════════════════════════╝"
echo ""
