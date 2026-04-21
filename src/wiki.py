# src/wiki.py
"""Wiki 管理模块"""

from pathlib import Path
import os
from datetime import datetime

class WikiManager:
    """Wiki 管理器"""
    
    def __init__(self):
        """初始化 Wiki 管理器"""
        self.wiki_path = Path(os.getenv("WIKI_PATH", "wiki"))
        self.index_file = self.wiki_path / "index.md"
        self.log_file = self.wiki_path / "log.md"
        
    def create_page(self, page_type, page_name, content):
        """创建 Wiki 页面
        
        Args:
            page_type: 页面类型 (entities, concepts, summaries)
            page_name: 页面名称
            content: 页面内容
        """
        page_dir = self.wiki_path / page_type
        page_dir.mkdir(parents=True, exist_ok=True)
        page_file = page_dir / f"{page_name}.md"
        
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        self.update_index()
        self.log_operation(f"create | {page_type}/{page_name}")
        return str(page_file)
    
    def update_page(self, page_type, page_name, content):
        """更新 Wiki 页面
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            content: 页面内容
        """
        page_file = self.wiki_path / page_type / f"{page_name}.md"
        if page_file.exists():
            with open(page_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.update_index()
            self.log_operation(f"update | {page_type}/{page_name}")
            return str(page_file)
        return None
    
    def get_page(self, page_type, page_name):
        """获取 Wiki 页面内容
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            
        Returns:
            页面内容
        """
        page_file = self.wiki_path / page_type / f"{page_name}.md"
        if page_file.exists():
            with open(page_file, "r", encoding="utf-8") as f:
                return f.read()
        return None
    
    def update_index(self):
        """更新索引文件"""
        index_content = "# Wiki Index\n\n"
        
        # 实体页面
        entities_dir = self.wiki_path / "entities"
        if entities_dir.exists():
            index_content += "## 实体\n"
            for file in entities_dir.glob("*.md"):
                entity_name = file.stem
                index_content += f"- [{entity_name}](entities/{entity_name}.md)\n"
            index_content += "\n"
        
        # 概念页面
        concepts_dir = self.wiki_path / "concepts"
        if concepts_dir.exists():
            index_content += "## 概念\n"
            for file in concepts_dir.glob("*.md"):
                concept_name = file.stem
                index_content += f"- [{concept_name}](concepts/{concept_name}.md)\n"
            index_content += "\n"
        
        # 摘要页面
        summaries_dir = self.wiki_path / "summaries"
        if summaries_dir.exists():
            index_content += "## 摘要\n"
            for file in summaries_dir.glob("*.md"):
                summary_name = file.stem
                index_content += f"- [{summary_name}](summaries/{summary_name}.md)\n"
        
        with open(self.index_file, "w", encoding="utf-8") as f:
            f.write(index_content)
    
    def log_operation(self, operation):
        """记录操作日志
        
        Args:
            operation: 操作描述
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"## [{timestamp}] {operation}\n"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    def list_pages(self, page_type):
        """列出指定类型的所有页面
        
        Args:
            page_type: 页面类型
            
        Returns:
            页面列表
        """
        page_dir = self.wiki_path / page_type
        if page_dir.exists():
            return [file.stem for file in page_dir.glob("*.md")]
        return []
