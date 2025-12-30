#!/bin/bash

# 企业知识助手启动脚本
# 这个脚本会同时启动 Flask API 后端和 React 前端

echo "🚀 启动企业知识助手..."

# 检查 Ollama 是否运行
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama 服务未运行，请先启动 Ollama："
    echo "   ollama serve"
    echo "   ollama pull qwen2:0.5b"
    exit 1
fi

# 检查 Python 依赖
if ! python -c "import flask, chromadb, ollama" 2>/dev/null; then
    echo "📦 安装 Python 依赖..."
    pip install -r requirements.txt
fi

# 检查 Node.js 依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend && npm install && cd ..
fi

echo "🔧 启动 Flask API 后端..."
python app.py &
FLASK_PID=$!
sleep 2  # 等待Flask启动

echo "⚛️  启动 React 前端..."
cd frontend && PORT=3001 npm start &
REACT_PID=$!
sleep 3  # 等待React启动

echo ""
echo "✅ 服务启动完成！"
echo "📱 前端界面: http://localhost:3001"
echo "🔌 API 后端: http://localhost:5000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 停止服务...'; kill $FLASK_PID $REACT_PID 2>/dev/null; exit" INT
wait