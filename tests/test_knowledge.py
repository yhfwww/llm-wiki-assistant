# tests/test_knowledge.py
"""测试知识管理模块"""

import pytest
from src.knowledge import KnowledgeManager
import tempfile
import os

class TestKnowledgeManager:
    
    def setup_method(self):
        """设置测试环境"""
        self.km = KnowledgeManager()
        
    def test_add_source(self):
        """测试添加源文件"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is a test document.")
            test_file = f.name
        
        try:
            result = self.km.add_source(test_file)
            assert result == True
        finally:
            # 清理临时文件
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def test_search(self):
        """测试搜索功能"""
        # 添加测试内容
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Document\n\nThis is a test document about AI.")
            test_file = f.name
        
        try:
            self.km.add_source(test_file)
            results = self.km.search("AI")
            assert results is not None
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
