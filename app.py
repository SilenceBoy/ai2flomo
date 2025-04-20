from fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import json
import requests
import logging
import sys

# 导入配置
from config import (
    FLOMO_WEBHOOK_URL,
    DATA_DIR,
    NOTES_FILE,
    DEFAULT_TAGS,
    SSE_PORT,
    SSE_HOST
)

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("flomo-notes")

# 打印系统信息
logger.info(f"Python版本: {sys.version}")
logger.info(f"当前工作目录: {os.getcwd()}")
logger.info(f"命令行参数: {sys.argv}")

# 创建MCP服务器实例
mcp = FastMCP(
    name="Flomo笔记服务",
    instructions="这是一个简单的Flomo风格笔记服务，可以发送笔记到Flomo，并查询历史发送记录"
)

logger.info(f"历史发送笔记文件路径: {NOTES_FILE}")

# 确保数据目录存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.info(f"创建数据目录: {DATA_DIR}")

# 初始化笔记文件
if not os.path.exists(NOTES_FILE):
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)
    logger.info(f"初始化空历史发送笔记文件: {NOTES_FILE}")

# 读取历史发送笔记
def load_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
            logger.debug(f"读取了 {len(notes)} 条历史发送笔记")
            return notes
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"读取历史发送笔记文件错误: {str(e)}")
        return []

# 保存历史发送笔记
def save_notes(notes):
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        logger.debug(f"保存了 {len(notes)} 条历史发送笔记")
    except Exception as e:
        logger.error(f"保存历史发送笔记文件错误: {str(e)}")

# 定义历史发送笔记结构
class Note(BaseModel):
    id: Optional[int] = None
    content: str
    tags: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# 函数：添加历史发送笔记到本地（内部使用，不作为工具对外提供）
def add_note_internal(content: str, tags: str = "") -> dict:
    """
    添加一条新历史发送笔记到本地（内部函数，不对外暴露）
    
    参数:
        content: 笔记内容
        tags: 标签，多个标签用空格分隔
    
    返回:
        包含新历史发送笔记信息的字典
    """
    logger.info(f"内部添加历史发送笔记: '{content[:30]}...' 标签: {tags}")
    notes = load_notes()
    
    # 解析标签
    tag_list = [tag.strip() for tag in tags.split() if tag.strip()]
    # 如果有默认标签，添加到标签列表
    for default_tag in DEFAULT_TAGS:
        if default_tag not in tag_list:
            tag_list.append(default_tag)
    
    # 创建新历史发送笔记
    note_id = len(notes) + 1
    now = datetime.now().isoformat()
    new_note = {
        "id": note_id,
        "content": content,
        "tags": tag_list,
        "created_at": now,
        "updated_at": now
    }
    
    # 添加到历史发送笔记列表
    notes.append(new_note)
    save_notes(notes)
    
    return new_note

# 工具：发送笔记到Flomo
@mcp.tool()
def send_to_flomo(content: str, tags: str = "") -> dict:
    """
    将笔记发送到Flomo并保存到本地
    
    参数:
        content: 笔记内容
        tags: 标签，多个标签用空格分隔，会自动转换为Flomo的#tag格式
    
    返回:
        包含发送结果的字典
    """
    logger.info(f"发送笔记到Flomo: '{content[:30]}...' 标签: {tags}")
    
    # 处理标签格式，从空格分隔转换为Flomo的#tag格式
    tag_list = [f"#{tag.strip()}" for tag in tags.split() if tag.strip()]
    # 添加默认标签
    for default_tag in DEFAULT_TAGS:
        if f"#{default_tag}" not in tag_list:
            tag_list.append(f"#{default_tag}")
    
    tag_text = " ".join(tag_list)
    
    # 组合完整内容
    full_content = f"{content}\n\n{tag_text}" if tag_text else content
    
    # 调用Flomo API
    try:
        logger.info(f"调用Flomo API: {FLOMO_WEBHOOK_URL}")
        response = requests.post(
            FLOMO_WEBHOOK_URL,
            json={"content": full_content},
            headers={"Content-Type": "application/json"}
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            logger.info(f"成功发送到Flomo: {result}")
            
            # 同时保存到本地
            local_note = add_note_internal(content, tags)
            
            return {
                "success": True,
                "message": "成功发送到Flomo并保存到本地",
                "flomo_response": result,
                "local_note": local_note
            }
        else:
            logger.error(f"发送到Flomo失败: {response.status_code}, {response.text}")
            return {
                "success": False,
                "message": f"发送到Flomo失败: {response.status_code}",
                "error": response.text
            }
    except Exception as e:
        logger.error(f"发送到Flomo出错: {str(e)}")
        return {
            "success": False,
            "message": "发送到Flomo出错",
            "error": str(e)
        }

# 工具：查询历史发送笔记
@mcp.tool()
def search_notes(query: str = "", tag: str = "") -> list:
    """
    搜索历史发送笔记
    
    参数:
        query: 搜索内容文本
        tag: 按标签搜索
    
    返回:
        符合条件的历史发送笔记列表
    """
    logger.info(f"搜索历史发送笔记: 内容='{query}' 标签='{tag}'")
    notes = load_notes()
    
    # 过滤结果
    if query and tag:
        # 同时按内容和标签搜索
        results = [note for note in notes 
                  if query.lower() in note["content"].lower() 
                  and tag.lower() in [t.lower() for t in note["tags"]]]
    elif query:
        # 仅按内容搜索
        results = [note for note in notes if query.lower() in note["content"].lower()]
    elif tag:
        # 仅按标签搜索
        results = [note for note in notes if tag.lower() in [t.lower() for t in note["tags"]]]
    else:
        # 返回所有历史发送笔记
        results = notes
    
    logger.info(f"找到 {len(results)} 条历史发送笔记")
    return results

# 工具：获取所有标签
@mcp.tool()
def get_all_tags() -> list:
    """获取所有历史发送笔记中使用的标签列表"""
    logger.info("获取所有历史发送笔记标签")
    notes = load_notes()
    
    # 收集所有标签
    all_tags = set()
    for note in notes:
        all_tags.update(note["tags"])
    
    tags_list = sorted(list(all_tags))
    logger.info(f"找到 {len(tags_list)} 个历史发送笔记标签")
    return tags_list

# 资源：最近5条历史发送笔记
@mcp.resource("notes://recent")
def get_recent_notes() -> list:
    """获取最近添加的5条历史发送笔记"""
    logger.info("获取最近历史发送笔记")
    notes = load_notes()
    recent = sorted(notes, key=lambda x: x["created_at"], reverse=True)[:5]
    logger.info(f"返回 {len(recent)} 条最近历史发送笔记")
    return recent

# 资源：按ID获取历史发送笔记
@mcp.resource("notes://{note_id}")
def get_note_by_id(note_id: int) -> dict:
    """通过ID获取单条历史发送笔记"""
    logger.info(f"获取历史发送笔记: ID={note_id}")
    notes = load_notes()
    
    for note in notes:
        if note["id"] == note_id:
            return note
    
    logger.warning(f"未找到ID为 {note_id} 的历史发送笔记")
    return {"error": f"未找到ID为 {note_id} 的历史发送笔记"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Flomo笔记MCP服务")
    parser.add_argument("--sse", action="store_true", help="使用SSE传输方式")
    parser.add_argument("--port", type=int, default=SSE_PORT, help="SSE服务的端口号")
    args = parser.parse_args()
    
    try:
        if args.sse:
            port = args.port
            logger.info(f"使用SSE传输方式启动服务，端口: {port}")
            mcp.run(transport="sse", transport_kwargs={"port": port, "host": SSE_HOST})
        else:
            logger.info("使用stdio传输方式启动服务")
            mcp.run()
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}", exc_info=True) 