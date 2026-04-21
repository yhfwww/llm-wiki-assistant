# LLM Wiki Assistant

基于 Agno 框架实现的个人知识库管理 AI 工具，遵循 llm-wiki 的理念，支持知识的增量积累和智能管理。

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Git
- (可选) Node.js 和 pnpm（用于运行前端）

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填写你的 API Key 配置
```

### 3. 初始化知识库
```bash
python src/init.py
```

### 4. 启动服务

#### 方式一：启动 Web 界面（推荐）
```bash
python src/app.py
```
然后参照 [前端部署指南](docs/frontend-setup.md) 启动前端界面。

#### 方式二：使用命令行工具
```bash
# 摄入知识
python src/ingest.py raw/sources/your_file.md

# 查询知识
python src/query.py "你的问题"

# 维护知识
python src/maintain.py
```

## 📋 功能特性

- **知识摄入**: 处理新的源文件，提取关键信息并集成到现有 wiki 中
- **知识查询**: 基于 wiki 内容回答用户问题，支持多种输出格式
- **知识维护**: 定期检查 wiki 健康状况，识别矛盾、过时信息等
- **索引与日志**: 维护 index.md 和 log.md 文件，方便导航和追踪
- **Web 界面**: 集成 Agno AG-UI 协议，提供友好的图形界面

## 📖 详细文档

- [设计文档](docs/llm-wiki-assistant-design.md) - 系统设计架构
- [实现计划](docs/llm-wiki-assistant-implementation-plan.md) - 实现路线图
- [前端部署指南](docs/frontend-setup.md) - Web 界面部署说明

## 📂 项目结构

```
llm-wiki-assistant/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── agent.py           # 核心代理实现
│   ├── knowledge.py       # 知识管理模块
│   ├── wiki.py            # Wiki 操作模块
│   ├── tools.py           # 工具集成
│   ├── utils.py           # 辅助函数
│   ├── app.py             # AG-UI Web 服务
│   ├── init.py            # 初始化脚本
│   ├── ingest.py          # 知识摄入脚本
│   ├── query.py           # 知识查询脚本
│   └── maintain.py        # 知识维护脚本
├── config/               # 配置文件
├── raw/                  # 原始源文件
│   ├── assets/           # 图片等资源
│   └── sources/          # 源文档
├── wiki/                 # LLM 生成的 Wiki
│   ├── index.md          # 内容索引
│   ├── log.md            # 操作日志
│   ├── entities/         # 实体页面
│   ├── concepts/         # 概念页面
│   └── summaries/        # 摘要页面
├── tests/                # 测试文件
├── docs/                 # 文档
├── requirements.txt      # 依赖文件
└── README.md             # 项目说明
```

## 🛠️ 技术栈

- **核心框架**: Agno
- **向量数据库**: LanceDB
- **嵌入模型**: OpenAI Embeddings
- **语言模型**: OpenAI GPT
- **存储格式**: Markdown
- **搜索引擎**: qmd
- **Web 界面**: AG-UI 协议 + Dojo

## 📝 使用方法

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

### 启动 Web 界面
1. 启动后端服务：
   ```bash
   python src/app.py
   ```
2. 按照 [前端部署指南](docs/frontend-setup.md) 启动前端

## 🔮 未来扩展

- **多用户支持**: 支持团队协作
- **多语言支持**: 处理多语言内容
- **高级分析**: 提供知识图谱和趋势分析
- **自动化工作流**: 基于事件的自动化处理
- **扩展工具集成**: 集成更多第三方工具

## 🐛 问题反馈

如果遇到问题，请检查以下几点：
1. 确保 .env 文件中的 API Key 配置正确
2. 检查 Python 版本是否为 3.8+
3. 确认所有依赖已通过 requirements.txt 安装
4. 查看项目文档是否有相关说明

## 📜 许可证

请查看 LICENSE 文件了解许可证信息。
