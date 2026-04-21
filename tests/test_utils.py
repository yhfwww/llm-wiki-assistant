# tests/test_utils.py
"""测试辅助函数模块"""

import pytest
from src.utils import extract_entities, extract_concepts, sanitize_filename, read_file
import tempfile
import os

class TestUtils:
    
    def test_extract_entities(self):
        """测试提取实体"""
        text = "OpenAI 开发了 GPT-4 模型，这是一个强大的 AI 系统。"
        entities = extract_entities(text)
        assert "OpenAI" in entities
        assert "GPT-4" in entities
    
    def test_extract_concepts(self):
        """测试提取概念"""
        text = "这个理论基于一个重要的概念，即机器学习中的监督学习方法。"
        concepts = extract_concepts(text)
        assert "理论" in concepts
        assert "概念" in concepts
        assert "方法" in concepts
    
    def test_sanitize_filename(self):
        """测试清理文件名"""
        test_name = "Test: File/Name*With?Special|Chars"
        sanitized = sanitize_filename(test_name)
        assert ":" not in sanitized
        assert "/" not in sanitized
        assert "*" not in sanitized
        assert "?" not in sanitized
        assert "|" not in sanitized
    
    def test_read_file(self):
        """测试读取文件"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            test_content = "Test content"
            f.write(test_content)
            test_file = f.name
        
        try:
            content = read_file(test_file)
            assert content == test_content
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
