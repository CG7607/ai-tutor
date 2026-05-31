#!/bin/bash
# ============================================================
#  AITutor 一键安装脚本 (macOS / Linux)
#  自动检测环境 → 创建虚拟环境 → 安装依赖 → 配置 API Key
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🤖 AI导师 安装程序 v2.1               ║"
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
    echo "   ❌ 未找到 Python 3.11+，请先安装："
    echo "      macOS: brew install python@3.12"
    echo "      官网:  https://www.python.org/downloads/"
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
if pip install -r "$SCRIPT_DIR/requirements.txt" --quiet; then
    echo "   ✅ 依赖安装成功。"
else
    echo "   ❌ 依赖安装失败，请检查网络连接。"
    echo "   你可以稍后手动运行：pip install -r requirements.txt"
    exit 1
fi

# ---- 4. 配置 API Key ----
echo ""
echo "🔑 [4/5] 配置 LLM API Key..."
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "   ⚠️  .env 已存在，跳过配置。"
    echo "   如需修改请直接编辑 aitutor/.env"
else
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo ""
    read -p "   请输入你的 API Key（回车跳过，稍后手动配置）: " api_key
    if [ -n "$api_key" ]; then
        # macOS 用 sed -i ''，Linux 用 sed -i
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/your-api-key-here/$api_key/" "$SCRIPT_DIR/.env"
        else
            sed -i "s/your-api-key-here/$api_key/" "$SCRIPT_DIR/.env"
        fi
        echo "   ✅ API Key 已写入 .env"
    else
        echo "   📝 已生成 .env 模板，请稍后编辑填入 API Key。"
    fi
fi

# ---- 5. 生成桌面快捷方式 ----
echo ""
echo "🔗 [5/5] 生成快捷启动方式..."
DESKTOP_FILE="$HOME/Desktop/AITutor.command"

cat > "$DESKTOP_FILE" << 'CMDEOF'
#!/bin/bash
cd "$(dirname "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 找到 aitutor 目录
AITUTOR_DIR=""
for guess in \
    "$SCRIPT_DIR/../aitutor" \
    "$SCRIPT_DIR/../../Desktop/cc/aitutor" \
    "$(dirname "$0")/aitutor"; do
    if [ -f "$guess/run.sh" ]; then
        AITUTOR_DIR="$guess"
        break
    fi
done
if [ -z "$AITUTOR_DIR" ]; then
    echo "❌ 找不到 AITutor 安装目录，请手动运行 run.sh"
    read -p "按回车退出..."
    exit 1
fi
cd "$AITUTOR_DIR"
source .venv/bin/activate 2>/dev/null || true
bash run.sh
CMDEOF

chmod +x "$DESKTOP_FILE"
echo "   ✅ 桌面快捷方式已创建：$DESKTOP_FILE"

# ---- 完成 ----
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   🎉 安装完成！                         ║"
echo "║                                          ║"
echo "║   启动方式：                             ║"
echo "║   1. 双击桌面 AITutor.command           ║"
echo "║   2. 终端运行：cd aitutor && bash run.sh ║"
echo "║                                          ║"
echo "║   浏览器打开 http://localhost:8501       ║"
echo "╚══════════════════════════════════════════╝"
echo ""
