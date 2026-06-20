#!/bin/bash
# aitutor/run.sh
# 一键启动 AITutor 前后端服务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到项目目录，确保 .env / 相对路径正确
cd "$SCRIPT_DIR"

echo "🚀 启动 AITutor..."
echo ""

# ---- Python ----
PYTHON=""
for c in python3.12 python3.11 python3.13 python3 python; do
    if command -v "$c" &>/dev/null; then PYTHON="$c"; break; fi
done
if [ -z "$PYTHON" ]; then echo "❌ 找不到 Python 3！"; exit 1; fi
echo "🔍 $($PYTHON --version 2>&1)"

# 国内镜像加速
MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"
MIRROR_FLAGS="-i $MIRROR --trusted-host pypi.tuna.tsinghua.edu.cn"

# venv

if [ -f "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    PIP="pip"
else
    echo "⚠️  虚拟环境不存在，自动创建中..."
    "$PYTHON" -m venv "$SCRIPT_DIR/.venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
    PIP="pip"
    echo "📥 安装依赖..."
    pip install -r "$SCRIPT_DIR/requirements.txt" $MIRROR_FLAGS --quiet 2>/dev/null || \
    pip install -r "$SCRIPT_DIR/requirements.txt" --quiet 2>/dev/null || \
    echo "   ⚠️  依赖安装失败，继续尝试启动..."
fi

# ---- 依赖 ----
echo ""
echo "📦 检测依赖..."
ensure_pkg() {
    if "$PYTHON" -c "import $1" 2>/dev/null; then echo "   ✅ $2"; return 0; fi
    echo "   ⚠️  缺少 $2，正在安装..."
    $PIP install "$2" $MIRROR_FLAGS --quiet 2>/dev/null && echo "   ✅ $2 安装完成" || \
    { $PIP install "$2" --quiet 2>/dev/null && echo "   ✅ $2 安装完成"; } || \
    echo "   ❌ 安装失败"
}
ensure_pkg fastapi   fastapi
ensure_pkg uvicorn   uvicorn
ensure_pkg streamlit streamlit
ensure_pkg httpx     httpx

# ---- 后端 ----
echo ""
echo "📡 启动 FastAPI 后端 (端口 8000)..."
PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH" \
    "$PYTHON" -m uvicorn aitutor.backend.main:app \
    --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "   等待后端就绪..."
for i in $(seq 1 15); do
    sleep 1
    if curl -s http://localhost:8000/docs &>/dev/null; then echo "   ✅ 后端就绪！"; break; fi
done

# ---- 前端 ----
echo "🎨 启动 Streamlit 前端 (端口 8501)..."
PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH" \
    "$PYTHON" -m streamlit run "$SCRIPT_DIR/frontend/app.py" \
    --server.port 8501 --server.headless true &
FRONTEND_PID=$!

sleep 3

# ---- 验证 & 浏览器 ----
if curl -s http://localhost:8501 &>/dev/null; then
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║   ✅ 启动成功！ http://localhost:8501    ║"
    echo "║   按 Ctrl+C 停止                        ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    open "http://localhost:8501" && echo "🌐 浏览器已打开！"
else
    echo "⚠️  启动异常，请检查上面的错误信息"
fi

cleanup() {
    echo ""
    echo "🛑 停止服务..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "👋 拜拜~"
    exit 0
}
trap cleanup SIGINT SIGTERM
wait
