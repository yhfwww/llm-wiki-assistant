# src/tools.py
"""工具集成模块"""

from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.knowledge import KnowledgeTools
from src.knowledge import KnowledgeManager

class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        """初始化工具管理器"""
        self.knowledge_manager = KnowledgeManager()
        self.web_search_tool = DuckDuckGoTools()
        self.knowledge_tool = KnowledgeTools(
            knowledge=self.knowledge_manager.knowledge,
            enable_think=True,
            enable_search=True,
            enable_analyze=True,
            add_few_shot=True,
        )
    
    def get_tools(self):
        """获取所有工具
        
        Returns:
            工具列表
        """
        return [self.web_search_tool, self.knowledge_tool]
