# Flomo笔记 MCP 服务

这是一个使用FastMCP框架构建的 MCP 服务，可以让AI助手(如Claude, Cherry Studio等)将你想要的信息发送到Flomo，并查询历史发送记录。这个服务充当AI助手与Flomo笔记应用之间的桥梁，让你能够通过对话方式快速记录灵感和想法。

## 功能概述

- **发送笔记到Flomo**：通过对话直接发送笔记内容到你的Flomo账户
- **标签支持**：添加标签进行分类整理，自动转换为Flomo的#tag格式
- **历史记录查询**：可按内容或标签搜索历史发送记录
- **自动同步**：笔记同时保存到Flomo和本地，实现双向备份

## 快速开始

### 1. 安装准备

**系统要求**：
- Python 3.8+
- pip包管理器
- 有效的Flomo Webhook URL

**安装步骤**：

1. 克隆或下载本项目到本地
2. 安装必要依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置Flomo Webhook URL（见下文配置部分）

### 2. 配置服务

打开`config.py`文件，根据需要修改以下配置项：

```python
# Flomo API配置 - 必须替换为你自己的Webhook URL
FLOMO_WEBHOOK_URL = "https://flomoapp.com/iwh/你的ID/你的WEBHOOK_KEY/"

# 数据存储路径 - 通常无需修改
DATA_DIR = "data"  # 数据存储目录
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")  # 历史记录文件名

# 默认标签 - 可以添加你常用的标签
DEFAULT_TAGS = []  # 例如 ["重要", "工作", "学习"]

# SSE服务配置 - 如果端口被占用可以修改
SSE_PORT = 3000  # 默认端口
SSE_HOST = "0.0.0.0"  # 监听地址
```

**配置Flomo Webhook URL的步骤**：

1. 登录你的Flomo账户
2. 访问API页面：https://flomoapp.com/mine?source=incoming_webhook 
3. 点击"添加新的Webhook"
4. 复制生成的URL
5. 将该URL粘贴到配置文件的`FLOMO_WEBHOOK_URL`处

### 3. 启动服务

有两种启动方式，根据需求选择：

**方法1：Stdio模式（推荐）**
```bash
./start_flomo.sh
```

**方法2：SSE模式（高级用途）**
```bash
./start_flomo.sh --sse --port 3000
```

### 4. 在AI助手中配置

#### Claude桌面版配置方法

1. 打开Claude桌面应用
2. 打开setting -> Developer
3. 点击选项"Edit Config"
4. 进入 Claude 目录打开文件"claude_desktop_config.json"
5. 填写以下信息：
```json
{
  "mcpServers": {
    "ai2flomo": {
      "name": "Flomo笔记服务",
      "type": "stdio",
      "description": "一个用于添加和管理笔记的工具，支持与Flomo同步",
      "isActive": true,
      "command": "/Users/username/workspace/mcp_space/ai2flomo/start_flomo.sh",
      "args": [],
      "env": {
        "PATH": "/opt/miniconda3/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
      }
    }
  }
}
```
6. 替换"start_flomo.sh"文件的路径与环境变量"env"为你的电脑设置。
7. 点击"保存"

#### Cherry Studio配置方法

1. 打开Cherry Studio应用
2. 点击"设置"图标
3. 在左侧菜单中选择"MCP服务器"
4. 点击"添加服务器"按钮
5. 填写以下信息：
   - **名称**：Flomo笔记服务
   - **描述**：通过AI助手发送笔记到Flomo并管理历史记录
   - **类型**：标准输入/输出(stdio)
   - **命令**：填写`start_flomo.sh`脚本的完整路径
   - **环境变量**：可填写你系统的环境变量
6. 点击"保存"
7. 点击"保存"按钮左侧的开关，确认服务能正常连接

**Cherry Studio的JSON配置示例**：

在Cherry Studio中，你也可以直接编辑JSON配置。点击"编辑JSON"按钮，可以看到类似以下的配置：

```json
{
  "mcpServers": {
    "MDzXVj9bhliofwJ8eCHs9": {
      "name": "Flomo笔记服务",
      "type": "stdio",
      "description": "一个用于添加和管理笔记的工具，支持与Flomo同步",
      "isActive": true,
      "command": "/Users/username/workspace/mcp_space/ai2flomo/start_flomo.sh",
      "args": [],
      "env": {
        "PATH": "/opt/miniconda3/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
      }
    }
  }
}
```

确保将路径`/Users/username/workspace/mcp_space/ai2flomo/start_flomo.sh`替换为你系统上实际的`start_flomo.sh`脚本路径。

如果你使用SSE模式，配置方式略有不同：
1. 选择"类型"为"SSE"
2. 在"URL"字段中填入：`http://localhost:3000/sse`（如果修改了端口号，请相应调整）
3. 其他步骤与上述相同

## 使用指南

当服务启动并在AI助手中配置完成后，你可以通过以下方式使用：

### 发送笔记到Flomo

简单地告诉AI助手你想记录的内容：

- "将'这个想法很有意思，我应该进一步研究'发送到Flomo"
- "帮我添加笔记：'今天学习了MCP协议的基础知识'，标签为'学习 编程'"

### 搜索历史记录

你可以按内容或标签搜索之前发送过的笔记：

- "查找包含'Python'的历史发送记录"
- "显示所有带'学习'标签的历史发送记录"
- "列出所有历史发送记录的标签"
- "展示我最近发送的5条记录"

## 项目结构

```
.
├── app.py               # 主程序文件，包含所有MCP工具和资源定义
├── config.py            # 配置文件，包含API密钥、路径和其他设置
├── start_flomo.sh       # 启动脚本
├── requirements.txt     # 项目依赖
├── data/                # 数据存储目录
│   └── notes.json       # 历史发送记录数据文件
├── logs/                # 日志目录
└── README.md            # 项目文档
```

## 技术细节

### API与工具

服务提供以下MCP工具和资源：

#### 工具 (Tools)

1. **send_to_flomo(content, tags)**
   - 将笔记发送到Flomo并保存到本地
   - 参数：
     - `content`: 笔记内容
     - `tags`: 标签，多个标签用空格分隔

2. **search_notes(query, tag)**
   - 搜索历史发送记录
   - 参数：
     - `query`: 内容搜索关键字
     - `tag`: 标签搜索关键字

3. **get_all_tags()**
   - 获取所有历史发送记录中使用的标签列表

#### 资源 (Resources)

1. **notes://recent**
   - 获取最近添加的5条历史发送记录

2. **notes://{note_id}**
   - 通过ID获取特定历史发送记录

### 数据存储

服务使用简单的JSON文件作为存储，位于`data/notes.json`。每条记录包含：
- 唯一ID
- 内容
- 标签列表
- 创建和更新时间戳

### 标签处理

- 输入格式：标签以空格分隔，如`"学习 编程 Python"`
- Flomo格式：自动转换为Flomo的#tag格式，如`#学习 #编程 #Python`
- 默认标签：如果在配置文件中设置了`DEFAULT_TAGS`，这些标签会自动添加到每条笔记中

## 常见问题解答

**Q: 我的Flomo Webhook URL在哪里可以找到？**  
A: 登录Flomo网站，访问https://flomoapp.com/mine?source=incoming_webhook 即可查看和创建。

**Q: 发送笔记失败怎么办？**  
A: 检查你的Webhook URL是否正确，以及网络连接是否正常。错误信息会在服务日志中显示。

**Q: 如何添加默认标签？**  
A: 编辑`config.py`文件，修改`DEFAULT_TAGS`列表，如`DEFAULT_TAGS = ["日常", "AI助手"]`。

**Q: 如何备份历史发送记录？**  
A: 所有记录都保存在`data/notes.json`文件中，可以定期备份此文件。

## 关于MCP

Model Context Protocol (MCP) 是一种标准化协议，允许AI模型安全地与外部工具和服务进行交互。通过MCP，AI助手可以：

1. 使用工具(Tools) - 执行操作，如发送笔记到Flomo
2. 访问资源(Resources) - 获取信息，如历史发送记录
3. 使用提示模板(Prompts) - 按照预定义模式进行交互

## 参考资源

- [Flomo官网](https://flomoapp.com/)
- [Flomo API文档](https://help.flomoapp.com/extension/api.html)
- [FastMCP框架](https://github.com/jlowin/fastmcp)
- [Model Context Protocol规范](https://modelcontextprotocol.io/)  
