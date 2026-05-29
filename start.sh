#!/bin/bash
# 高明区产业链知识图谱 - 一键启动脚本
cd "$(dirname "$0")"

echo "========================================="
echo "  高明区产业链知识图谱 v1.0"
echo "========================================="

# 检查依赖
echo "[1/3] 检查依赖..."
python3 -c "import fastapi, uvicorn, networkx, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  -> 安装依赖..."
    pip3 install -r requirements.txt -q
fi

# 初始化数据
echo "[2/3] 初始化数据库..."
python3 -c "from backend.data_collector import seed_database; seed_database()" 2>/dev/null

# 启动服务
echo "[3/3] 启动服务器..."
echo ""
echo "  🌐 前端界面:  http://localhost:8001"
echo "  📊 API文档:    http://localhost:8001/docs"
echo "  🖥️ 交互图谱:  file://$(pwd)/data/gaoming_graph.html"
echo ""
echo "  按 Ctrl+C 停止服务器"
echo "========================================="
echo ""

python3 -c "
import uvicorn
from backend.main import app
uvicorn.run(app, host='0.0.0.0', port=8001)
"
