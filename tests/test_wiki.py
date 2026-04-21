# tests/test_wiki.py
"""测试 Wiki 管理模块"""

import pytest
from src.wiki import WikiManager
import tempfile
import os
import shutil

class TestWikiManager:
    
    def setup_method(self):
        """设置测试环境"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        os.environ["WIKI_PATH"] = self.temp_dir
        self.wm = WikiManager()
        
    def teardown_method(self):
        """清理测试环境"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_page(self):
        """测试创建页面"""
        content = "# Test Entity\n\nThis is a test entity."
        result = self.wm.create_page("entities", "test_entity", content)
        assert result is not None
        assert os.path.exists(result)
    
    def test_update_page(self):
        """测试更新页面"""
        # 先创建页面
        content1 = "# Test Entity\n\nThis is a test entity."
        self.wm.create_page("entities", "test_entity", content1)
        
        # 更新页面
        content2 = "# Test Entity\n\nThis is an updated test entity."
        result = self.wm.update_page("entities", "test_entity", content2)
        assert result is not None
        
        # 验证内容已更新
        updated_content = self.wm.get_page("entities", "test_entity")
        assert "updated" in updated_content
    
    def test_get_page(self):
        """测试获取页面"""
        content = "# Test Entity\n\nThis is a test entity."
        self.wm.create_page("entities", "test_entity", content)
        
        retrieved_content = self.wm.get_page("entities", "test_entity")
        assert retrieved_content == content
    
    def test_list_pages(self):
        """测试列出页面"""
        # 创建多个页面
        self.wm.create_page("entities", "entity1", "# Entity 1")
        self.wm.create_page("entities", "entity2", "# Entity 2")
        
        pages = self.wm.list_pages("entities")
        assert len(pages) == 2
        assert "entity1" in pages
        assert "entity2" in pages
