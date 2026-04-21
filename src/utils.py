# src/utils.py
"""辅助函数模块"""

import re
from pathlib import Path

def extract_entities(text):
    """从文本中提取实体
    
    Args:
        text: 文本内容
        
    Returns:
        实体列表
    """
    # 简单的实体提取逻辑
    # 实际应用中可以使用更复杂的 NER 模型
    entities = []
    # 提取大写开头的单词或短语
    pattern = r'\b[A-Z][a-zA-Z0-9-]+(?:\s+[A-Z][a-zA-Z0-9-]+)*\b'
    matches = re.findall(pattern, text)
    entities.extend(matches)
    return list(set(entities))

def extract_concepts(text):
    """从文本中提取概念
    
    Args:
        text: 文本内容
        
    Returns:
        概念列表
    """
    # 简单的概念提取逻辑
    # 实际应用中可以使用更复杂的方法
    concepts = []
    # 提取可能的概念
    # 对于中文，使用字符匹配，不使用词边界
    chinese_patterns = ['概念', '理论', '方法', '原理', '思想']
    for pattern in chinese_patterns:
        if pattern in text:
            concepts.append(pattern)
    # 对于英文，使用词边界
    english_pattern = r'\b(idea|theory|principle|method)\b'
    matches = re.findall(english_pattern, text, re.IGNORECASE)
    concepts.extend(matches)
    return list(set(concepts))

def sanitize_filename(name):
    """清理文件名
    
    Args:
        name: 原始名称
        
    Returns:
        清理后的文件名
    """
    # 替换特殊字符
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    # 去除多余的下划线
    name = re.sub(r'_+', '_', name)
    # 去除首尾下划线
    name = name.strip('_')
    return name

def read_file(file_path):
    """读取文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件内容
    """
    file_path = Path(file_path)
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
