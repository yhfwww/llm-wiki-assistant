# src/knowledge.py
"""知识管理模块"""

from pathlib import Path
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.openai import OpenAIEmbedder
import os
from dotenv import load_dotenv

load_dotenv()

class KnowledgeManager:
    """知识管理器"""
    
    def __init__(self):
        """初始化知识管理器"""
        self.lance_db_path = os.getenv("LANCE_DB_PATH", "tmp/lancedb")
        # 使用环境变量中的嵌入模型
        embedding_model = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-4B")
        self.knowledge = Knowledge(
            vector_db=LanceDb(
                uri=self.lance_db_path,
                table_name="wiki_knowledge",
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(id=embedding_model),
            ),
        )
    
    def add_source(self, file_path):
        """添加源文件
        
        Args:
            file_path: 源文件路径
        """
        file_path = Path(file_path)
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.knowledge.add_content(
                text_content=content,
                name=file_path.name
            )
            return True
        return False
    
    def search(self, query):
        """搜索知识
        
        Args:
            query: 查询语句
            
        Returns:
            搜索结果
        """
        return self.knowledge.search(query)
    
    def get_all_sources(self):
        """获取所有源文件
        
        Returns:
            源文件列表
        """
        # 实现获取所有源文件的逻辑
        pass
