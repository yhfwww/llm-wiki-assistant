# src/knowledge_graph.py
"""知识图谱系统"""

from datetime import datetime
import json
from pathlib import Path
import os

class KnowledgeGraph:
    """知识图谱"""
    
    def __init__(self):
        """初始化知识图谱"""
        self.graph_path = Path(os.getenv("KNOWLEDGE_GRAPH_PATH", "knowledge_graph"))
        self.graph_path.mkdir(parents=True, exist_ok=True)
        self.entities_file = self.graph_path / "entities.json"
        self.relationships_file = self.graph_path / "relationships.json"
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        # 加载实体
        if self.entities_file.exists():
            with open(self.entities_file, "r", encoding="utf-8") as f:
                self.entities = json.load(f)
        else:
            self.entities = {}
        
        # 加载关系
        if self.relationships_file.exists():
            with open(self.relationships_file, "r", encoding="utf-8") as f:
                self.relationships = json.load(f)
        else:
            self.relationships = {}
    
    def _save_data(self):
        """保存数据"""
        # 保存实体
        with open(self.entities_file, "w", encoding="utf-8") as f:
            json.dump(self.entities, f, ensure_ascii=False, indent=2)
        
        # 保存关系
        with open(self.relationships_file, "w", encoding="utf-8") as f:
            json.dump(self.relationships, f, ensure_ascii=False, indent=2)
    
    def add_entity(self, entity_id, entity_type, properties):
        """添加实体
        
        Args:
            entity_id: 实体ID
            entity_type: 实体类型
            properties: 实体属性
            
        Returns:
            添加结果
        """
        self.entities[entity_id] = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "properties": properties,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "relationships": []
        }
        
        self._save_data()
        return {
            "status": "success",
            "message": "实体添加成功"
        }
    
    def update_entity(self, entity_id, properties):
        """更新实体
        
        Args:
            entity_id: 实体ID
            properties: 实体属性
            
        Returns:
            更新结果
        """
        if entity_id not in self.entities:
            return {
                "status": "error",
                "message": "实体不存在"
            }
        
        self.entities[entity_id]["properties"].update(properties)
        self.entities[entity_id]["last_updated"] = datetime.now().isoformat()
        
        self._save_data()
        return {
            "status": "success",
            "message": "实体更新成功"
        }
    
    def add_relationship(self, relationship_id, source_id, target_id, relationship_type, properties=None):
        """添加关系
        
        Args:
            relationship_id: 关系ID
            source_id: 源实体ID
            target_id: 目标实体ID
            relationship_type: 关系类型
            properties: 关系属性
            
        Returns:
            添加结果
        """
        if source_id not in self.entities:
            return {
                "status": "error",
                "message": "源实体不存在"
            }
        
        if target_id not in self.entities:
            return {
                "status": "error",
                "message": "目标实体不存在"
            }
        
        self.relationships[relationship_id] = {
            "relationship_id": relationship_id,
            "source_id": source_id,
            "target_id": target_id,
            "relationship_type": relationship_type,
            "properties": properties or {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # 更新源实体的关系列表
        self.entities[source_id]["relationships"].append({
            "relationship_id": relationship_id,
            "target_id": target_id,
            "relationship_type": relationship_type
        })
        
        # 更新目标实体的关系列表
        self.entities[target_id]["relationships"].append({
            "relationship_id": relationship_id,
            "source_id": source_id,
            "relationship_type": relationship_type
        })
        
        self._save_data()
        return {
            "status": "success",
            "message": "关系添加成功"
        }
    
    def get_entity(self, entity_id):
        """获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            实体信息
        """
        if entity_id in self.entities:
            return self.entities[entity_id]
        return None
    
    def get_relationship(self, relationship_id):
        """获取关系
        
        Args:
            relationship_id: 关系ID
            
        Returns:
            关系信息
        """
        if relationship_id in self.relationships:
            return self.relationships[relationship_id]
        return None
    
    def get_entities_by_type(self, entity_type):
        """按类型获取实体
        
        Args:
            entity_type: 实体类型
            
        Returns:
            实体列表
        """
        entities = []
        for entity_id, entity_info in self.entities.items():
            if entity_info["entity_type"] == entity_type:
                entities.append(entity_info)
        return entities
    
    def get_relationships_by_type(self, relationship_type):
        """按类型获取关系
        
        Args:
            relationship_type: 关系类型
            
        Returns:
            关系列表
        """
        relationships = []
        for relationship_id, relationship_info in self.relationships.items():
            if relationship_info["relationship_type"] == relationship_type:
                relationships.append(relationship_info)
        return relationships
    
    def get_relationships_for_entity(self, entity_id):
        """获取实体的关系
        
        Args:
            entity_id: 实体ID
            
        Returns:
            关系列表
        """
        if entity_id not in self.entities:
            return []
        
        entity_relationships = []
        for rel_info in self.entities[entity_id]["relationships"]:
            relationship_id = rel_info["relationship_id"]
            if relationship_id in self.relationships:
                entity_relationships.append(self.relationships[relationship_id])
        
        return entity_relationships
    
    def get_related_entities(self, entity_id, relationship_type=None):
        """获取相关实体
        
        Args:
            entity_id: 实体ID
            relationship_type: 关系类型（可选）
            
        Returns:
            相关实体列表
        """
        if entity_id not in self.entities:
            return []
        
        related_entities = []
        for rel_info in self.entities[entity_id]["relationships"]:
            if not relationship_type or rel_info["relationship_type"] == relationship_type:
                related_id = rel_info.get("target_id", rel_info.get("source_id"))
                if related_id and related_id in self.entities:
                    related_entities.append(self.entities[related_id])
        
        return related_entities
    
    def remove_entity(self, entity_id):
        """移除实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            移除结果
        """
        if entity_id not in self.entities:
            return {
                "status": "error",
                "message": "实体不存在"
            }
        
        # 移除相关关系
        relationships_to_remove = []
        for relationship_id, relationship_info in self.relationships.items():
            if relationship_info["source_id"] == entity_id or relationship_info["target_id"] == entity_id:
                relationships_to_remove.append(relationship_id)
        
        for relationship_id in relationships_to_remove:
            del self.relationships[relationship_id]
        
        # 移除其他实体中对该实体的引用
        for other_entity_id, other_entity_info in self.entities.items():
            if other_entity_id != entity_id:
                new_relationships = []
                for rel_info in other_entity_info["relationships"]:
                    if rel_info.get("target_id") != entity_id and rel_info.get("source_id") != entity_id:
                        new_relationships.append(rel_info)
                other_entity_info["relationships"] = new_relationships
        
        # 移除实体
        del self.entities[entity_id]
        
        self._save_data()
        return {
            "status": "success",
            "message": "实体移除成功"
        }
    
    def remove_relationship(self, relationship_id):
        """移除关系
        
        Args:
            relationship_id: 关系ID
            
        Returns:
            移除结果
        """
        if relationship_id not in self.relationships:
            return {
                "status": "error",
                "message": "关系不存在"
            }
        
        relationship_info = self.relationships[relationship_id]
        source_id = relationship_info["source_id"]
        target_id = relationship_info["target_id"]
        
        # 从源实体中移除关系
        if source_id in self.entities:
            new_relationships = []
            for rel_info in self.entities[source_id]["relationships"]:
                if rel_info["relationship_id"] != relationship_id:
                    new_relationships.append(rel_info)
            self.entities[source_id]["relationships"] = new_relationships
        
        # 从目标实体中移除关系
        if target_id in self.entities:
            new_relationships = []
            for rel_info in self.entities[target_id]["relationships"]:
                if rel_info["relationship_id"] != relationship_id:
                    new_relationships.append(rel_info)
            self.entities[target_id]["relationships"] = new_relationships
        
        # 移除关系
        del self.relationships[relationship_id]
        
        self._save_data()
        return {
            "status": "success",
            "message": "关系移除成功"
        }
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        total_entities = len(self.entities)
        total_relationships = len(self.relationships)
        entity_types = {}
        relationship_types = {}
        
        for entity_info in self.entities.values():
            entity_type = entity_info["entity_type"]
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        for relationship_info in self.relationships.values():
            rel_type = relationship_info["relationship_type"]
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        return {
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "entity_types": entity_types,
            "relationship_types": relationship_types
        }

class KnowledgeGraphManager:
    """知识图谱管理器"""
    
    def __init__(self):
        """初始化知识图谱管理器"""
        self.knowledge_graph = KnowledgeGraph()
    
    def add_entity(self, entity_id, entity_type, properties):
        """添加实体
        
        Args:
            entity_id: 实体ID
            entity_type: 实体类型
            properties: 实体属性
            
        Returns:
            添加结果
        """
        return self.knowledge_graph.add_entity(entity_id, entity_type, properties)
    
    def update_entity(self, entity_id, properties):
        """更新实体
        
        Args:
            entity_id: 实体ID
            properties: 实体属性
            
        Returns:
            更新结果
        """
        return self.knowledge_graph.update_entity(entity_id, properties)
    
    def add_relationship(self, relationship_id, source_id, target_id, relationship_type, properties=None):
        """添加关系
        
        Args:
            relationship_id: 关系ID
            source_id: 源实体ID
            target_id: 目标实体ID
            relationship_type: 关系类型
            properties: 关系属性
            
        Returns:
            添加结果
        """
        return self.knowledge_graph.add_relationship(relationship_id, source_id, target_id, relationship_type, properties)
    
    def get_entity(self, entity_id):
        """获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            实体信息
        """
        return self.knowledge_graph.get_entity(entity_id)
    
    def get_relationship(self, relationship_id):
        """获取关系
        
        Args:
            relationship_id: 关系ID
            
        Returns:
            关系信息
        """
        return self.knowledge_graph.get_relationship(relationship_id)
    
    def get_entities_by_type(self, entity_type):
        """按类型获取实体
        
        Args:
            entity_type: 实体类型
            
        Returns:
            实体列表
        """
        return self.knowledge_graph.get_entities_by_type(entity_type)
    
    def get_relationships_by_type(self, relationship_type):
        """按类型获取关系
        
        Args:
            relationship_type: 关系类型
            
        Returns:
            关系列表
        """
        return self.knowledge_graph.get_relationships_by_type(relationship_type)
    
    def get_relationships_for_entity(self, entity_id):
        """获取实体的关系
        
        Args:
            entity_id: 实体ID
            
        Returns:
            关系列表
        """
        return self.knowledge_graph.get_relationships_for_entity(entity_id)
    
    def get_related_entities(self, entity_id, relationship_type=None):
        """获取相关实体
        
        Args:
            entity_id: 实体ID
            relationship_type: 关系类型（可选）
            
        Returns:
            相关实体列表
        """
        return self.knowledge_graph.get_related_entities(entity_id, relationship_type)
    
    def remove_entity(self, entity_id):
        """移除实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            移除结果
        """
        return self.knowledge_graph.remove_entity(entity_id)
    
    def remove_relationship(self, relationship_id):
        """移除关系
        
        Args:
            relationship_id: 关系ID
            
        Returns:
            移除结果
        """
        return self.knowledge_graph.remove_relationship(relationship_id)
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        return self.knowledge_graph.get_statistics()
