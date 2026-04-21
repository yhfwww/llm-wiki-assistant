# src/init.py
"""初始化知识库"""

import os
from datetime import datetime
from pathlib import Path

# 创建目录结构
dirs = [
    "raw/sources",
    "raw/assets",
    "wiki/entities",
    "wiki/concepts",
    "wiki/summaries",
    "config",
    "tests"
]

for dir_path in dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

# 创建初始文件

# 创建 index.md
index_content = """# Wiki Index

## 实体

## 概念

## 摘要
"""
with open("wiki/index.md", "w") as f:
    f.write(index_content)

# 创建 log.md
log_content = """# Wiki Log

## [{}] 初始化
- 知识库系统初始化完成
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
with open("wiki/log.md", "w") as f:
    f.write(log_content)

# 创建 schema.md
schema_content = """# Wiki Schema

## 结构约定
- 实体页面: wiki/entities/{entity}.md
- 概念页面: wiki/concepts/{concept}.md
- 摘要页面: wiki/summaries/{source}.md

## 工作流程
1. 知识摄入: 处理新源文件，生成或更新Wiki页面
2. 知识查询: 基于Wiki内容回答问题
3. 知识维护: 定期检查Wiki健康状况

## 页面格式
### 实体页面
```markdown
# {实体名称}

## 描述
{实体描述}

## 相关概念
- [{概念名称}](概念链接)

## 来源
- [{来源名称}](来源链接)
```

### 概念页面
```markdown
# {概念名称}

## 定义
{概念定义}

## 相关实体
- [{实体名称}](实体链接)

## 相关概念
- [{概念名称}](概念链接)

## 来源
- [{来源名称}](来源链接)
```

### 摘要页面
```markdown
# {来源名称}

## 来源信息
- 类型: {文件类型}
- 日期: {摄入日期}

## 摘要
{内容摘要}

## 关键实体
- [{实体名称}](实体链接)

## 关键概念
- [{概念名称}](概念链接)
```
"""
with open("config/schema.md", "w") as f:
    f.write(schema_content)

# 创建 .env.example
env_content = """# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Database paths
LANCE_DB_PATH=tmp/lancedb
WIKI_PATH=wiki
RAW_PATH=raw
"""
with open(".env.example", "w") as f:
    f.write(env_content)

print("知识库初始化完成")
