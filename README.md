# LLM Wiki Assistant

基于 Agno 框架实现的个人知识库管理 AI 工具，遵循 llm-wiki 的理念，支持知识的增量积累和智能管理。

## 功能特性

- **知识摄入**: 处理新的源文件，提取关键信息并集成到现有 wiki 中
- **知识查询**: 基于 wiki 内容回答用户问题，支持多种输出格式
- **知识维护**: 定期检查 wiki 健康状况，识别矛盾、过时信息等
- **索引与日志**: 维护 index.md 和 log.md 文件，方便导航和追踪

## 安装与配置

1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填写 OpenAI API Key
   ```

3. 初始化知识库
   ```bash
   python src/init.py
   ```

## 使用方法

### 添加源文件
将文件放入 `raw/sources/` 目录

### 摄入知识
```bash
python src/ingest.py raw/sources/your_file.md
```

### 查询知识
```bash
python src/query.py "你的问题"
```

### 维护知识
```bash
python src/maintain.py
```

## 目录结构

```
llm-wiki-assistant/
├── src/              # 源代码
├── config/           # 配置文件
├── raw/              # 原始源文件
│   ├── assets/       # 图片等资源
│   └── sources/      # 源文档
├── wiki/             # LLM生成的Wiki
│   ├── index.md      # 内容索引
│   ├── log.md        # 操作日志
│   ├── entities/     # 实体页面
│   ├── concepts/     # 概念页面
│   └── summaries/    # 摘要页面
├── tests/            # 测试文件
├── requirements.txt  # 依赖文件
└── README.md         # 项目说明
```

## 技术栈

- **核心框架**: Agno
- **向量数据库**: LanceDB
- **嵌入模型**: OpenAI Embeddings
- **语言模型**: OpenAI GPT
- **存储格式**: Markdown
- **搜索引擎**: qmd

## 未来扩展

- **多用户支持**: 支持团队协作
- **多语言支持**: 处理多语言内容
- **高级分析**: 提供知识图谱和趋势分析
- **自动化工作流**: 基于事件的自动化处理
- **扩展工具集成**: 集成更多第三方工具
