# src/schema.py
"""Schema 定义系统"""

from pathlib import Path
import os
import json
from datetime import datetime

class SchemaDefinition:
    """Schema 定义管理"""
    
    def __init__(self):
        """初始化 Schema 定义"""
        self.schema_path = Path(os.getenv("SCHEMA_PATH", "schema"))
        self.schema_path.mkdir(parents=True, exist_ok=True)
        self.schema_file = self.schema_path / "schema.json"
        self.version_file = self.schema_path / "version.json"
        self._load_schema()
        self._load_version()
    
    def _load_schema(self):
        """加载 Schema"""
        if self.schema_file.exists():
            with open(self.schema_file, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
        else:
            self._initialize_default_schema()
    
    def _load_version(self):
        """加载版本信息"""
        if self.version_file.exists():
            with open(self.version_file, "r", encoding="utf-8") as f:
                self.version_info = json.load(f)
        else:
            self.version_info = {
                "current_version": "1.0",
                "history": [
                    {
                        "version": "1.0",
                        "created_at": datetime.now().isoformat(),
                        "description": "初始版本"
                    }
                ]
            }
            self._save_version()
    
    def _initialize_default_schema(self):
        """初始化默认 Schema"""
        self.schema = {
            "version": "1.0",
            "entities": {
                "Person": {
                    "properties": [
                        {"name": "name", "type": "string", "required": True},
                        {"name": "birth_date", "type": "date", "required": False},
                        {"name": "death_date", "type": "date", "required": False},
                        {"name": "occupation", "type": "string", "required": False},
                        {"name": "nationality", "type": "string", "required": False},
                        {"name": "description", "type": "text", "required": True},
                        {"name": "achievements", "type": "list", "required": False}
                    ],
                    "relationships": [
                        {"name": "works_at", "target": "Organization", "cardinality": "many"},
                        {"name": "founded", "target": "Organization", "cardinality": "many"},
                        {"name": "invented", "target": "Concept", "cardinality": "many"},
                        {"name": "collaborated_with", "target": "Person", "cardinality": "many"}
                    ]
                },
                "Organization": {
                    "properties": [
                        {"name": "name", "type": "string", "required": True},
                        {"name": "founded_date", "type": "date", "required": False},
                        {"name": "industry", "type": "string", "required": True},
                        {"name": "location", "type": "string", "required": False},
                        {"name": "description", "type": "text", "required": True},
                        {"name": "products", "type": "list", "required": False}
                    ],
                    "relationships": [
                        {"name": "founded_by", "target": "Person", "cardinality": "many"},
                        {"name": "employs", "target": "Person", "cardinality": "many"},
                        {"name": "partners_with", "target": "Organization", "cardinality": "many"}
                    ]
                },
                "Concept": {
                    "properties": [
                        {"name": "name", "type": "string", "required": True},
                        {"name": "definition", "type": "text", "required": True},
                        {"name": "examples", "type": "list", "required": False},
                        {"name": "applications", "type": "list", "required": False},
                        {"name": "description", "type": "text", "required": True},
                        {"name": "related_concepts", "type": "list", "required": False}
                    ],
                    "relationships": [
                        {"name": "related_to", "target": "Concept", "cardinality": "many"},
                        {"name": "part_of", "target": "Concept", "cardinality": "one"},
                        {"name": "invented_by", "target": "Person", "cardinality": "many"},
                        {"name": "used_by", "target": "Organization", "cardinality": "many"}
                    ]
                },
                "Event": {
                    "properties": [
                        {"name": "name", "type": "string", "required": True},
                        {"name": "date", "type": "date", "required": True},
                        {"name": "location", "type": "string", "required": False},
                        {"name": "description", "type": "text", "required": True},
                        {"name": "participants", "type": "list", "required": False},
                        {"name": "outcome", "type": "text", "required": False}
                    ],
                    "relationships": [
                        {"name": "involves", "target": "Person", "cardinality": "many"},
                        {"name": "involves_org", "target": "Organization", "cardinality": "many"},
                        {"name": "related_to", "target": "Event", "cardinality": "many"}
                    ]
                }
            },
            "page_types": [
                "entities",
                "concepts",
                "summaries",
                "timelines",
                "comparisons",
                "events"
            ],
            "quality_standards": {
                "min_length": 100,
                "max_length": 5000,
                "required_sections": {
                    "entities": ["概述", "详细信息", "关系网络", "参考资料"],
                    "concepts": ["概述", "定义", "应用", "相关概念", "参考资料"],
                    "summaries": ["概述", "主要内容", "关键观点", "参考资料"],
                    "timelines": ["概述", "时间线", "重要事件", "参考资料"],
                    "comparisons": ["概述", "比较维度", "详细对比", "参考资料"],
                    "events": ["概述", "详细信息", "参与方", "影响", "参考资料"]
                },
                "formatting": {
                    "headings": True,
                    "bullet_points": True,
                    "links": True,
                    "references": True
                }
            },
            "conflict_resolution": {
                "strategy": "latest_wins",  # latest_wins, highest_confidence, human_approval
                "confidence_threshold": 0.7,
                "conflict_types": {
                    "factual": "resolve_automatically",
                    "interpretive": "flag_for_review",
                    "temporal": "latest_wins"
                }
            },
            "forgetting_curve": {
                "decay_rate": 0.1,
                "min_confidence": 0.3,
                "review_period": "30d",
                "importance_factors": {
                    "usage_frequency": 0.4,
                    "recency": 0.3,
                    "source_quality": 0.3
                }
            },
            "source_tracking": {
                "required_fields": ["source_id", "source_type", "extracted_date", "confidence"],
                "allowed_sources": ["document", "website", "paper", "interview", "social_media"]
            }
        }
        self._save_schema()
    
    def _save_schema(self):
        """保存 Schema"""
        with open(self.schema_file, "w", encoding="utf-8") as f:
            json.dump(self.schema, f, ensure_ascii=False, indent=2)
    
    def _save_version(self):
        """保存版本信息"""
        with open(self.version_file, "w", encoding="utf-8") as f:
            json.dump(self.version_info, f, ensure_ascii=False, indent=2)
    
    def get_schema(self):
        """获取 Schema
        
        Returns:
            Schema 对象
        """
        return self.schema
    
    def update_schema(self, schema, version_description="Schema 更新"):
        """更新 Schema
        
        Args:
            schema: 新的 Schema
            version_description: 版本描述
        """
        # 生成新版本号
        current_version = self.version_info["current_version"]
        major, minor = map(int, current_version.split("."))
        new_version = f"{major}.{minor + 1}"
        
        # 更新 Schema
        schema["version"] = new_version
        self.schema = schema
        self._save_schema()
        
        # 更新版本信息
        self.version_info["current_version"] = new_version
        self.version_info["history"].append({
            "version": new_version,
            "created_at": datetime.now().isoformat(),
            "description": version_description
        })
        self._save_version()
    
    def validate_entity(self, entity_type, entity_data):
        """验证实体数据
        
        Args:
            entity_type: 实体类型
            entity_data: 实体数据
            
        Returns:
            (是否有效, 错误信息)
        """
        if entity_type not in self.schema.get("entities", {}):
            return False, f"无效的实体类型: {entity_type}"
        
        entity_def = self.schema["entities"][entity_type]
        
        # 检查必需属性
        for prop in entity_def.get("properties", []):
            if prop.get("required", False) and prop["name"] not in entity_data:
                return False, f"缺少必需属性: {prop['name']}"
        
        # 检查属性类型
        for prop in entity_def.get("properties", []):
            prop_name = prop["name"]
            if prop_name in entity_data:
                prop_value = entity_data[prop_name]
                prop_type = prop["type"]
                
                if prop_type == "string" and not isinstance(prop_value, str):
                    return False, f"属性 {prop_name} 类型错误，应为字符串"
                elif prop_type == "text" and not isinstance(prop_value, str):
                    return False, f"属性 {prop_name} 类型错误，应为文本"
                elif prop_type == "date" and prop_value:
                    # 简单的日期格式检查
                    try:
                        datetime.fromisoformat(prop_value)
                    except:
                        return False, f"属性 {prop_name} 格式错误，应为 ISO 日期格式"
                elif prop_type == "list" and not isinstance(prop_value, list):
                    return False, f"属性 {prop_name} 类型错误，应为列表"
        
        return True, "验证通过"
    
    def validate_page(self, page_type, content):
        """验证页面内容
        
        Args:
            page_type: 页面类型
            content: 页面内容
            
        Returns:
            (是否有效, 错误信息)
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
        required_sections = self.schema.get("quality_standards", {}).get("required_sections", {}).get(page_type, [])
        for section in required_sections:
            if f"## {section}" not in content:
                return False, f"缺少必需章节: {section}"
        
        # 检查格式
        formatting = self.schema.get("quality_standards", {}).get("formatting", {})
        if formatting.get("headings", False) and "## " not in content:
            return False, "缺少标题格式"
        
        return True, "验证通过"
    
    def resolve_conflict(self, conflict_type, old_data, new_data, confidence):
        """解决冲突
        
        Args:
            conflict_type: 冲突类型
            old_data: 旧数据
            new_data: 新数据
            confidence: 新数据的置信度
            
        Returns:
            解决后的数据
        """
        resolution_strategy = self.schema.get("conflict_resolution", {})
        
        # 根据冲突类型选择策略
        conflict_strategies = resolution_strategy.get("conflict_types", {})
        strategy = conflict_strategies.get(conflict_type, resolution_strategy.get("strategy", "latest_wins"))
        
        if strategy == "latest_wins":
            return new_data
        elif strategy == "highest_confidence":
            threshold = resolution_strategy.get("confidence_threshold", 0.7)
            if confidence >= threshold:
                return new_data
            return old_data
        elif strategy == "flag_for_review":
            # 标记为需要人工审核
            return {
                "_conflict": True,
                "_old_data": old_data,
                "_new_data": new_data,
                "_confidence": confidence
            }
        elif strategy == "resolve_automatically":
            # 自动解决事实性冲突
            if confidence >= resolution_strategy.get("confidence_threshold", 0.7):
                return new_data
            return old_data
        else:
            return new_data
    
    def calculate_importance(self, page_data):
        """计算页面重要性
        
        Args:
            page_data: 页面数据
            
        Returns:
            重要性分数 (0-1)
        """
        factors = self.schema.get("forgetting_curve", {}).get("importance_factors", {})
        
        # 计算各因素分数
        usage_frequency = page_data.get("usage_count", 0) / 10.0  # 假设最多10次使用
        usage_score = usage_frequency * factors.get("usage_frequency", 0.4)
        
        # 计算新鲜度分数
        if "last_updated" in page_data:
            try:
                last_updated = datetime.fromisoformat(page_data["last_updated"])
                days_since_update = (datetime.now() - last_updated).days
                recency_score = max(0, 1 - days_since_update / 365) * factors.get("recency", 0.3)
            except:
                recency_score = 0
        else:
            recency_score = 0
        
        # 源质量分数
        source_quality = page_data.get("source_quality", 0.8) * factors.get("source_quality", 0.3)
        
        total_score = usage_score + recency_score + source_quality
        return min(1.0, max(0.0, total_score))
    
    def get_entity_template(self, entity_type):
        """获取实体模板
        
        Args:
            entity_type: 实体类型
            
        Returns:
            实体模板
        """
        if entity_type not in self.schema.get("entities", {}):
            return None
        
        entity_def = self.schema["entities"][entity_type]
        template = {}
        
        for prop in entity_def.get("properties", []):
            prop_name = prop["name"]
            if prop.get("required", False):
                template[prop_name] = ""
            else:
                template[prop_name] = None
        
        return template

class SchemaManager:
    """Schema 管理器"""
    
    def __init__(self):
        """初始化 Schema 管理器"""
        self.schema_def = SchemaDefinition()
    
    def get_schema(self):
        """获取 Schema
        
        Returns:
            Schema 对象
        """
        return self.schema_def.get_schema()
    
    def update_schema(self, schema, version_description="Schema 更新"):
        """更新 Schema
        
        Args:
            schema: 新的 Schema
            version_description: 版本描述
        """
        self.schema_def.update_schema(schema, version_description)
    
    def validate_entity(self, entity_type, entity_data):
        """验证实体数据
        
        Args:
            entity_type: 实体类型
            entity_data: 实体数据
            
        Returns:
            (是否有效, 错误信息)
        """
        return self.schema_def.validate_entity(entity_type, entity_data)
    
    def validate_page(self, page_type, content):
        """验证页面内容
        
        Args:
            page_type: 页面类型
            content: 页面内容
            
        Returns:
            (是否有效, 错误信息)
        """
        return self.schema_def.validate_page(page_type, content)
    
    def resolve_conflict(self, conflict_type, old_data, new_data, confidence):
        """解决冲突
        
        Args:
            conflict_type: 冲突类型
            old_data: 旧数据
            new_data: 新数据
            confidence: 新数据的置信度
            
        Returns:
            解决后的数据
        """
        return self.schema_def.resolve_conflict(conflict_type, old_data, new_data, confidence)
    
    def calculate_importance(self, page_data):
        """计算页面重要性
        
        Args:
            page_data: 页面数据
            
        Returns:
            重要性分数 (0-1)
        """
        return self.schema_def.calculate_importance(page_data)
    
    def get_entity_template(self, entity_type):
        """获取实体模板
        
        Args:
            entity_type: 实体类型
            
        Returns:
            实体模板
        """
        return self.schema_def.get_entity_template(entity_type)
    
    def get_page_types(self):
        """获取页面类型
        
        Returns:
            页面类型列表
        """
        return self.schema_def.get_schema().get("page_types", [])
    
    def get_entity_types(self):
        """获取实体类型
        
        Returns:
            实体类型列表
        """
        return list(self.schema_def.get_schema().get("entities", {}).keys())
