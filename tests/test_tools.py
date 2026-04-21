# tests/test_tools.py
"""测试工具集成模块"""

import pytest
from src.tools import ToolManager

class TestToolManager:
    
    def setup_method(self):
        """设置测试环境"""
        self.tool_manager = ToolManager()
    
    def test_get_tools(self):
        """测试获取工具列表"""
        tools = self.tool_manager.get_tools()
        assert len(tools) >= 2
