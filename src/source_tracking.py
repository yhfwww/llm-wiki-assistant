# src/source_tracking.py
"""来源追踪功能"""

from datetime import datetime
import json
from pathlib import Path
import os

class SourceTracker:
    """来源追踪器"""
    
    def __init__(self):
        """初始化来源追踪器"""
        self.tracking_path = Path(os.getenv("SOURCE_TRACKING_PATH", "source_tracking"))
        self.tracking_path.mkdir(parents=True, exist_ok=True)
        self.sources_file = self.tracking_path / "sources.json"
        self.page_sources_file = self.tracking_path / "page_sources.json"
        self._load_data()
    
    def _load_data(self):
        """加载数据"""
        # 加载来源信息
        if self.sources_file.exists():
            with open(self.sources_file, "r", encoding="utf-8") as f:
                self.sources = json.load(f)
        else:
            self.sources = {}
        
        # 加载页面-来源映射
        if self.page_sources_file.exists():
            with open(self.page_sources_file, "r", encoding="utf-8") as f:
                self.page_sources = json.load(f)
        else:
            self.page_sources = {}
    
    def _save_data(self):
        """保存数据"""
        # 保存来源信息
        with open(self.sources_file, "w", encoding="utf-8") as f:
            json.dump(self.sources, f, ensure_ascii=False, indent=2)
        
        # 保存页面-来源映射
        with open(self.page_sources_file, "w", encoding="utf-8") as f:
            json.dump(self.page_sources, f, ensure_ascii=False, indent=2)
    
    def register_source(self, source_id, source_type, file_path=None, metadata=None):
        """注册来源
        
        Args:
            source_id: 来源ID
            source_type: 来源类型
            file_path: 文件路径
            metadata: 元数据
            
        Returns:
            注册结果
        """
        self.sources[source_id] = {
            "source_id": source_id,
            "source_type": source_type,
            "file_path": str(file_path) if file_path else None,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "reliability_score": self._calculate_reliability_score(source_type, metadata),
            "usage_count": 0
        }
        
        self._save_data()
        return {
            "status": "success",
            "message": "来源注册成功"
        }
    
    def _calculate_reliability_score(self, source_type, metadata):
        """计算来源可靠性分数
        
        Args:
            source_type: 来源类型
            metadata: 元数据
            
        Returns:
            可靠性分数 (0-1)
        """
        # 基础分数
        base_score = 0.5
        
        # 来源类型加成
        type_scores = {
            "paper": 0.9,
            "document": 0.7,
            "website": 0.6,
            "interview": 0.75,
            "social_media": 0.4
        }
        
        base_score = type_scores.get(source_type, base_score)
        
        # 元数据加成
        if metadata:
            # 检查是否有作者信息
            if "author" in metadata:
                base_score += 0.1
            # 检查是否有发布日期
            if "publish_date" in metadata:
                try:
                    publish_date = datetime.fromisoformat(metadata["publish_date"])
                    # 近期发布的内容更可靠
                    days_since_publish = (datetime.now() - publish_date).days
                    if days_since_publish < 365:
                        base_score += 0.1
                except:
                    pass
            # 检查是否有引用信息
            if "citations" in metadata and metadata["citations"] > 0:
                base_score += 0.1
        
        return min(1.0, max(0.1, base_score))
    
    def associate_source(self, page_id, source_id, confidence=0.8, extracted_date=None):
        """关联来源到页面
        
        Args:
            page_id: 页面ID
            source_id: 来源ID
            confidence: 置信度
            extracted_date: 提取日期
            
        Returns:
            关联结果
        """
        if source_id not in self.sources:
            return {
                "status": "error",
                "message": "来源不存在"
            }
        
        if page_id not in self.page_sources:
            self.page_sources[page_id] = []
        
        # 检查是否已关联
        for association in self.page_sources[page_id]:
            if association["source_id"] == source_id:
                return {
                    "status": "error",
                    "message": "来源已关联"
                }
        
        # 添加关联
        self.page_sources[page_id].append({
            "source_id": source_id,
            "confidence": confidence,
            "extracted_date": extracted_date or datetime.now().isoformat(),
            "added_at": datetime.now().isoformat()
        })
        
        # 更新来源使用计数
        self.sources[source_id]["usage_count"] += 1
        
        self._save_data()
        return {
            "status": "success",
            "message": "来源关联成功"
        }
    
    def get_page_sources(self, page_id):
        """获取页面的来源
        
        Args:
            page_id: 页面ID
            
        Returns:
            来源列表
        """
        if page_id not in self.page_sources:
            return []
        
        sources = []
        for association in self.page_sources[page_id]:
            source_id = association["source_id"]
            if source_id in self.sources:
                source_info = self.sources[source_id].copy()
                source_info.update(association)
                sources.append(source_info)
        
        return sources
    
    def get_source_info(self, source_id):
        """获取来源信息
        
        Args:
            source_id: 来源ID
            
        Returns:
            来源信息
        """
        if source_id in self.sources:
            return self.sources[source_id]
        return None
    
    def get_sources_by_type(self, source_type):
        """按类型获取来源
        
        Args:
            source_type: 来源类型
            
        Returns:
            来源列表
        """
        sources = []
        for source_id, source_info in self.sources.items():
            if source_info["source_type"] == source_type:
                sources.append(source_info)
        return sources
    
    def get_reliability_score(self, source_id):
        """获取来源可靠性分数
        
        Args:
            source_id: 来源ID
            
        Returns:
            可靠性分数
        """
        if source_id in self.sources:
            return self.sources[source_id].get("reliability_score", 0.5)
        return 0.5
    
    def update_reliability_score(self, source_id, new_score):
        """更新来源可靠性分数
        
        Args:
            source_id: 来源ID
            new_score: 新的可靠性分数
            
        Returns:
            更新结果
        """
        if source_id in self.sources:
            self.sources[source_id]["reliability_score"] = min(1.0, max(0.1, new_score))
            self._save_data()
            return {
                "status": "success",
                "message": "可靠性分数更新成功"
            }
        return {
            "status": "error",
            "message": "来源不存在"
        }
    
    def remove_source_association(self, page_id, source_id):
        """移除页面与来源的关联
        
        Args:
            page_id: 页面ID
            source_id: 来源ID
            
        Returns:
            移除结果
        """
        if page_id in self.page_sources:
            for i, association in enumerate(self.page_sources[page_id]):
                if association["source_id"] == source_id:
                    self.page_sources[page_id].pop(i)
                    # 如果页面没有来源了，移除页面记录
                    if not self.page_sources[page_id]:
                        del self.page_sources[page_id]
                    self._save_data()
                    return {
                        "status": "success",
                        "message": "关联已移除"
                    }
        return {
            "status": "error",
            "message": "关联不存在"
        }
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        total_sources = len(self.sources)
        total_associations = 0
        type_counts = {}
        total_reliability = 0
        
        for source_info in self.sources.values():
            source_type = source_info["source_type"]
            type_counts[source_type] = type_counts.get(source_type, 0) + 1
            total_reliability += source_info.get("reliability_score", 0.5)
        
        for associations in self.page_sources.values():
            total_associations += len(associations)
        
        average_reliability = total_reliability / total_sources if total_sources > 0 else 0
        
        return {
            "total_sources": total_sources,
            "total_associations": total_associations,
            "type_counts": type_counts,
            "average_reliability": round(average_reliability, 2)
        }

class SourceTrackingManager:
    """来源追踪管理器"""
    
    def __init__(self):
        """初始化来源追踪管理器"""
        self.source_tracker = SourceTracker()
    
    def register_source(self, source_id, source_type, file_path=None, metadata=None):
        """注册来源
        
        Args:
            source_id: 来源ID
            source_type: 来源类型
            file_path: 文件路径
            metadata: 元数据
            
        Returns:
            注册结果
        """
        return self.source_tracker.register_source(source_id, source_type, file_path, metadata)
    
    def associate_source(self, page_id, source_id, confidence=0.8, extracted_date=None):
        """关联来源到页面
        
        Args:
            page_id: 页面ID
            source_id: 来源ID
            confidence: 置信度
            extracted_date: 提取日期
            
        Returns:
            关联结果
        """
        return self.source_tracker.associate_source(page_id, source_id, confidence, extracted_date)
    
    def get_page_sources(self, page_id):
        """获取页面的来源
        
        Args:
            page_id: 页面ID
            
        Returns:
            来源列表
        """
        return self.source_tracker.get_page_sources(page_id)
    
    def get_source_info(self, source_id):
        """获取来源信息
        
        Args:
            source_id: 来源ID
            
        Returns:
            来源信息
        """
        return self.source_tracker.get_source_info(source_id)
    
    def get_sources_by_type(self, source_type):
        """按类型获取来源
        
        Args:
            source_type: 来源类型
            
        Returns:
            来源列表
        """
        return self.source_tracker.get_sources_by_type(source_type)
    
    def get_reliability_score(self, source_id):
        """获取来源可靠性分数
        
        Args:
            source_id: 来源ID
            
        Returns:
            可靠性分数
        """
        return self.source_tracker.get_reliability_score(source_id)
    
    def update_reliability_score(self, source_id, new_score):
        """更新来源可靠性分数
        
        Args:
            source_id: 来源ID
            new_score: 新的可靠性分数
            
        Returns:
            更新结果
        """
        return self.source_tracker.update_reliability_score(source_id, new_score)
    
    def remove_source_association(self, page_id, source_id):
        """移除页面与来源的关联
        
        Args:
            page_id: 页面ID
            source_id: 来源ID
            
        Returns:
            移除结果
        """
        return self.source_tracker.remove_source_association(page_id, source_id)
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        return self.source_tracker.get_statistics()
