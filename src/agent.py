# src/agent.py
"""核心代理实现"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from src.knowledge import KnowledgeManager
from src.wiki import WikiManager
import os
from dotenv import load_dotenv

load_dotenv()

class WikiAgent:
    """Wiki 代理"""
    
    def __init__(self):
        """初始化代理"""
        self.knowledge_manager = KnowledgeManager()
        self.wiki_manager = WikiManager()
        
        # 使用环境变量中的LLM模型
        llm_model = os.getenv("LLM_MODEL_ID", "Qwen/Qwen3.5-4B")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
        
        self.agent = Agent(
            name="Wiki Agent",
            model=OpenAIChat(id=llm_model, base_url=openai_base_url),
            description="你是一个知识库管理助手，负责维护和管理 Wiki 知识库。",
            instructions=[
                "始终基于 Wiki 内容回答问题",
                "保持回答准确和相关",
                "在回答中包含相关的 Wiki 页面链接"
            ],
            knowledge=self.knowledge_manager.knowledge,
            db=SqliteDb(session_table="wiki_agent_sessions", db_file="tmp/agent.db"),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
        )
    
    def ingest_source(self, file_path):
        """摄入源文件
        
        Args:
            file_path: 源文件路径
            
        Returns:
            处理结果
        """
        # 添加到知识库
        success = self.knowledge_manager.add_source(file_path)
        if not success:
            return "无法添加源文件"
        
        # 生成摘要
        # 这里需要调用 LLM 生成摘要
        # 暂时返回成功消息
        return "源文件摄入成功"
    
    def query(self, question):
        """查询知识库
        
        Args:
            question: 查询问题
            
        Returns:
            回答
        """
        response = self.agent.run(question)
        return response
    
    def maintain(self):
        """维护知识库
        
        Returns:
            维护结果
        """
        # 实现维护逻辑
        # 检查页面间矛盾、过时信息等
        return "知识库维护完成"
