#!/bin/bash

# 设置PATH以包含miniconda环境
export PATH="/opt/miniconda3/bin:$PATH"

# 定位脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 使用系统Python
PYTHON=python3

echo "使用Python: $($PYTHON --version)"
echo "当前目录: $(pwd)"

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo "警告: 找不到requirements.txt文件"
else
    echo "检查依赖..."
    $PYTHON -m pip install -r requirements.txt
fi

# 创建数据和日志目录
mkdir -p data logs
echo "确保数据和日志目录存在"

# 启动服务
echo "启动Flomo笔记服务..."
$PYTHON app.py "$@"

# 如果需要SSE模式，则注释上面的行，取消注释下面的行
# python app.py --sse --port 3000 