# tests/test_agent.py
"""测试核心代理模块"""

import pytest
from src.agent import WikiAgent
import tempfile
import os

class TestWikiAgent:
    
    def setup_method(self):
        """设置测试环境"""
        self.agent = WikiAgent()
        
    def test_ingest_source(self):
        """测试摄入源文件"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is a test document.")
            test_file = f.name
        
        try:
            result = self.agent.ingest_source(test_file)
            assert "成功" in result
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_query(self):
        """测试查询功能"""
        # 这里只是测试代理是否能正常响应
        result = self.agent.query("你好")
        assert result is not None
    
    def test_maintain(self):
        """测试维护功能"""
        result = self.agent.maintain()
        assert "完成" in result
