"""
Flomo笔记服务配置文件
"""
import os

# Flomo API配置
FLOMO_WEBHOOK_URL = "https://flomoapp.com/iwh/MTUzOTExNA/"

# 数据存储路径
DATA_DIR = "data"
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")

# 默认标签
DEFAULT_TAGS = []  # 可以添加预设标签列表，如 ["重要", "工作", "生活"]

# SSE服务配置
SSE_PORT = 3000
SSE_HOST = "0.0.0.0" 