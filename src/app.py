"""
LLM Wiki Assistant 应用 - AG-UI 集成
使用 Agno 的 AgentOS 和 AGUI 接口暴露知识库助手
"""
from pathlib import Path
from dotenv import load_dotenv
from agno.agent.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.knowledge.knowledge import Knowledge

# 加载环境变量
load_dotenv()

# 创建维基知识库代理
def create_wiki_agent():
    # 配置向量数据库
    lance_db_path = Path("tmp/lancedb")
    lance_db_path.mkdir(parents=True, exist_ok=True)
    
    # 配置 OpenAI 模型（使用环境变量或默认值）
    import os
    llm_model = os.getenv("LLM_MODEL_ID", "Qwen/Qwen3.5-4B")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
    embedding_model = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-4B")
    
    # 设置知识库
    knowledge = Knowledge(
        vector_db=LanceDb(
            uri=str(lance_db_path),
            table_name="wiki_knowledge",
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id=embedding_model),
        ),
    )
    
    # 创建代理
    agent = Agent(
        name="LLM Wiki Assistant",
        model=OpenAIChat(id=llm_model, base_url=openai_base_url),
        description="你是一个知识库管理助手，负责维护和管理 Wiki 知识库。",
        instructions=[
            "始终基于 Wiki 内容回答问题",
            "保持回答准确和相关",
            "在回答中包含相关的 Wiki 页面链接",
            "使用 Markdown 格式展示答案"
        ],
        knowledge=knowledge,
        add_history_to_context=True,
        add_datetime_to_context=True,
        markdown=True,
    )
    
    return agent

if __name__ == "__main__":
    # 创建维基知识库代理
    wiki_agent = create_wiki_agent()
    
    # 配置 AgentOS 和 AGUI 接口
    agent_os = AgentOS(
        agents=[wiki_agent],
        interfaces=[AGUI(agent=wiki_agent)]
    )
    
    app = agent_os.get_app()
    
    # 启动服务
    print("启动 LLM Wiki Assistant 服务...")
    print("访问前端界面请查看 README.md 文档")
    agent_os.serve(app="app:app", host="0.0.0.0", port=7777, reload=True)
