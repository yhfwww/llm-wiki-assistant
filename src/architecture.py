# src/architecture.py
"""LLM Wiki 三层架构实现"""

from pathlib import Path
import os
from datetime import datetime
import json

class RawSourceLayer:
    """原始资料层"""
    
    def __init__(self):
        """初始化原始资料层"""
        self.source_path = Path(os.getenv("SOURCE_PATH", "sources"))
        self.source_path.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.source_path / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """加载元数据"""
        if self.meta_file.exists():
            with open(self.meta_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"sources": {}}
    
    def _save_metadata(self):
        """保存元数据"""
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def add_source(self, file_path, source_type="document"):
        """添加源文件
        
        Args:
            file_path: 源文件路径
            source_type: 源文件类型
            
        Returns:
            源文件ID
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        # 复制到原始资料目录
        source_id = f"{source_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        dest_file = self.source_path / f"{source_id}{file_path.suffix}"
        
        with open(file_path, "rb") as src, open(dest_file, "wb") as dst:
            dst.write(src.read())
        
        # 更新元数据
        self.metadata["sources"][source_id] = {
            "file_name": file_path.name,
            "path": str(dest_file.relative_to(self.source_path)),
            "type": source_type,
            "added_at": datetime.now().isoformat(),
            "size": dest_file.stat().st_size
        }
        
        self._save_metadata()
        return source_id
    
    def get_source(self, source_id):
        """获取源文件
        
        Args:
            source_id: 源文件ID
            
        Returns:
            源文件路径
        """
        if source_id in self.metadata["sources"]:
            source_info = self.metadata["sources"][source_id]
            source_path = self.source_path / source_info["path"]
            if source_path.exists():
                return str(source_path)
        return None
    
    def list_sources(self):
        """列出所有源文件
        
        Returns:
            源文件列表
        """
        return list(self.metadata["sources"].items())

class WikiLayer:
    """维基层"""
    
    def __init__(self):
        """初始化维基层"""
        self.wiki_path = Path(os.getenv("WIKI_PATH", "wiki"))
        self.pages_path = self.wiki_path / "pages"
        self.pages_path.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.wiki_path / "wiki_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """加载元数据"""
        if self.meta_file.exists():
            with open(self.meta_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"pages": {}}
    
    def _save_metadata(self):
        """保存元数据"""
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def create_page(self, page_type, page_name, content, source_ids=None):
        """创建维基页面
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            content: 页面内容
            source_ids: 关联的源文件ID列表
            
        Returns:
            页面路径
        """
        page_dir = self.pages_path / page_type
        page_dir.mkdir(parents=True, exist_ok=True)
        page_file = page_dir / f"{page_name}.md"
        
        # 添加元数据到内容
        metadata_header = f"""---
created_at: {datetime.now().isoformat()}
source_ids: {source_ids or []}
confidence: 0.8
last_updated: {datetime.now().isoformat()}
---

"""
        full_content = metadata_header + content
        
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        # 更新元数据
        page_id = f"{page_type}_{page_name}"
        self.metadata["pages"][page_id] = {
            "path": str(page_file.relative_to(self.wiki_path)),
            "type": page_type,
            "name": page_name,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "source_ids": source_ids or []
        }
        
        self._save_metadata()
        return str(page_file)
    
    def update_page(self, page_type, page_name, content, source_ids=None):
        """更新维基页面
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            content: 页面内容
            source_ids: 关联的源文件ID列表
            
        Returns:
            页面路径
        """
        page_file = self.pages_path / page_type / f"{page_name}.md"
        if not page_file.exists():
            return None
        
        # 添加元数据到内容
        metadata_header = f"""---
created_at: {datetime.now().isoformat()}
source_ids: {source_ids or []}
confidence: 0.8
last_updated: {datetime.now().isoformat()}
---

"""
        full_content = metadata_header + content
        
        with open(page_file, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        # 更新元数据
        page_id = f"{page_type}_{page_name}"
        if page_id in self.metadata["pages"]:
            self.metadata["pages"][page_id].update({
                "last_updated": datetime.now().isoformat(),
                "source_ids": source_ids or []
            })
        
        self._save_metadata()
        return str(page_file)
    
    def get_page(self, page_type, page_name):
        """获取维基页面
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            
        Returns:
            页面内容
        """
        page_file = self.pages_path / page_type / f"{page_name}.md"
        if page_file.exists():
            with open(page_file, "r", encoding="utf-8") as f:
                return f.read()
        return None
    
    def list_pages(self, page_type=None):
        """列出维基页面
        
        Args:
            page_type: 页面类型
            
        Returns:
            页面列表
        """
        pages = []
        if page_type:
            page_dir = self.pages_path / page_type
            if page_dir.exists():
                for file in page_dir.glob("*.md"):
                    pages.append((page_type, file.stem))
        else:
            for page_type_dir in self.pages_path.iterdir():
                if page_type_dir.is_dir():
                    for file in page_type_dir.glob("*.md"):
                        pages.append((page_type_dir.name, file.stem))
        return pages

class SchemaLayer:
    """模式（Schema）层"""
    
    def __init__(self):
        """初始化模式层"""
        self.schema_path = Path(os.getenv("SCHEMA_PATH", "schema"))
        self.schema_path.mkdir(parents=True, exist_ok=True)
        self.schema_file = self.schema_path / "schema.json"
        self._load_schema()
    
    def _load_schema(self):
        """加载模式"""
        if self.schema_file.exists():
            with open(self.schema_file, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        else:
            # 默认模式
            self.schema = {
                "version": "1.0",
                "entities": {
                    "Person": {
                        "properties": ["name", "birth_date", "occupation", "description"],
                        "relationships": ["works_at", "founded", "invented"]
                    },
                    "Organization": {
                        "properties": ["name", "founded_date", "industry", "description"],
                        "relationships": ["founded_by", "employs"]
                    },
                    "Concept": {
                        "properties": ["name", "definition", "examples", "related_concepts"],
                        "relationships": ["related_to", "part_of"]
                    }
                },
                "page_types": ["entities", "concepts", "summaries", "timelines", "comparisons"],
                "quality_standards": {
                    "min_length": 100,
                    "max_length": 5000,
                    "required_sections": ["概述", "详细信息", "参考资料"]
                },
                "conflict_resolution": {
                    "strategy": "latest_wins",
                    "confidence_threshold": 0.7
                },
                "forgetting_curve": {
                    "decay_rate": 0.1,
                    "min_confidence": 0.3
                }
            }
            self._save_schema()
    
    def _save_schema(self):
        """保存模式"""
        with open(self.schema_file, "w", encoding="utf-8") as f:
            json.dump(self.schema, f, ensure_ascii=False, indent=2)
    
    def get_schema(self):
        """获取模式
        
        Returns:
            模式对象
        """
        return self.schema
    
    def update_schema(self, schema):
        """更新模式
        
        Args:
            schema: 新的模式
        """
        self.schema = schema
        self._save_schema()
    
    def validate_page(self, page_type, content):
        """验证页面内容
        
        Args:
            page_type: 页面类型
            content: 页面内容
            
        Returns:
            验证结果
        """
        # 检查页面类型是否有效
        if page_type not in self.schema.get("page_types", []):
            return False, f"无效的页面类型: {page_type}"
        
        # 检查长度
        min_length = self.schema.get("quality_standards", {}).get("min_length", 100)
        max_length = self.schema.get("quality_standards", {}).get("max_length", 5000)
        
        if len(content) < min_length:
            return False, f"内容长度不足，至少需要 {min_length} 字符"
        
        if len(content) > max_length:
            return False, f"内容长度过长，最多允许 {max_length} 字符"
        
        # 检查必需章节
        required_sections = self.schema.get("quality_standards", {}).get("required_sections", [])
        for section in required_sections:
            if f"## {section}" not in content:
                return False, f"缺少必需章节: {section}"
        
        return True, "验证通过"

class Architecture:
    """LLM Wiki 架构管理"""
    
    def __init__(self):
        """初始化架构"""
        self.raw_source_layer = RawSourceLayer()
        self.wiki_layer = WikiLayer()
        self.schema_layer = SchemaLayer()
    
    def add_source(self, file_path, source_type="document"):
        """添加源文件
        
        Args:
            file_path: 源文件路径
            source_type: 源文件类型
            
        Returns:
            源文件ID
        """
        return self.raw_source_layer.add_source(file_path, source_type)
    
    def create_wiki_page(self, page_type, page_name, content, source_ids=None):
        """创建维基页面
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            content: 页面内容
            source_ids: 关联的源文件ID列表
            
        Returns:
            页面路径
        """
        # 验证页面
        valid, message = self.schema_layer.validate_page(page_type, content)
        if not valid:
            raise ValueError(f"页面验证失败: {message}")
        
        return self.wiki_layer.create_page(page_type, page_name, content, source_ids)
    
    def update_wiki_page(self, page_type, page_name, content, source_ids=None):
        """更新维基页面
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            content: 页面内容
            source_ids: 关联的源文件ID列表
            
        Returns:
            页面路径
        """
        # 验证页面
        valid, message = self.schema_layer.validate_page(page_type, content)
        if not valid:
            raise ValueError(f"页面验证失败: {message}")
        
        return self.wiki_layer.update_page(page_type, page_name, content, source_ids)
    
    def get_wiki_page(self, page_type, page_name):
        """获取维基页面
        
        Args:
            page_type: 页面类型
            page_name: 页面名称
            
        Returns:
            页面内容
        """
        return self.wiki_layer.get_page(page_type, page_name)
    
    def list_wiki_pages(self, page_type=None):
        """列出维基页面
        
        Args:
            page_type: 页面类型
            
        Returns:
            页面列表
        """
        return self.wiki_layer.list_pages(page_type)
    
    def get_schema(self):
        """获取模式
        
        Returns:
            模式对象
        """
        return self.schema_layer.get_schema()
    
    def update_schema(self, schema):
        """更新模式
        
        Args:
            schema: 新的模式
        """
        self.schema_layer.update_schema(schema)
