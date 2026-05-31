#!/bin/bash
# aitutor/run.sh
# 一键启动 AITutor 前后端服务

echo "🚀 启动 AITutor..."
echo ""

# Determine script directory (aitutor/)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Project root (parent of aitutor/) — needed for aitutor.* imports
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Start FastAPI backend
echo "📡 启动 FastAPI 后端 (端口 8000)..."
cd "$SCRIPT_DIR/backend"
PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH" uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start Streamlit frontend
echo "🎨 启动 Streamlit 前端 (端口 8501)..."
cd "$SCRIPT_DIR/frontend"
PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH" streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ AITutor 已启动！"
echo "   后端: http://localhost:8000"
echo "   前端: http://localhost:8501"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# Trap SIGINT to cleanup
trap "echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT

wait
