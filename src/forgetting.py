# src/forgetting.py
"""遗忘曲线系统"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import os
from src.confidence import ConfidenceManager
from src.schema import SchemaManager

class ForgettingCurve:
    """遗忘曲线管理"""
    
    def __init__(self):
        """初始化遗忘曲线系统"""
        self.confidence_manager = ConfidenceManager()
        self.schema_manager = SchemaManager()
        self.forgetting_path = Path(os.getenv("FORGETTING_PATH", "forgetting"))
        self.forgetting_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.forgetting_path / "metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """加载元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "pages": {},
                "last_cleanup": datetime.now().isoformat()
            }
    
    def _save_metadata(self):
        """保存元数据"""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def update_page_metadata(self, page_id, usage=False):
        """更新页面元数据
        
        Args:
            page_id: 页面ID
            usage: 是否为使用操作
        """
        if page_id not in self.metadata["pages"]:
            self.metadata["pages"][page_id] = {
                "created_at": datetime.now().isoformat(),
                "last_used": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "usage_count": 0,
                "importance_score": 0.5,
                "status": "active"
            }
        
        page_data = self.metadata["pages"][page_id]
        
        if usage:
            page_data["last_used"] = datetime.now().isoformat()
            page_data["usage_count"] = page_data.get("usage_count", 0) + 1
        else:
            page_data["last_updated"] = datetime.now().isoformat()
        
        # 更新重要性分数
        page_data["importance_score"] = self._calculate_importance(page_id, page_data)
        
        # 更新状态
        page_data["status"] = self._determine_status(page_data)
        
        self._save_metadata()
    
    def _calculate_importance(self, page_id, page_data):
        """计算页面重要性
        
        Args:
            page_id: 页面ID
            page_data: 页面数据
            
        Returns:
            重要性分数 (0-1)
        """
        # 使用信心评分作为基础
        confidence_score = self.confidence_manager.get_score(page_id)
        
        # 计算使用频率分数
        usage_count = page_data.get("usage_count", 0)
        usage_score = min(1.0, usage_count / 10.0)  # 最多10次使用
        
        # 计算新鲜度分数
        last_used = datetime.fromisoformat(page_data.get("last_used", datetime.now().isoformat()))
        days_since_used = (datetime.now() - last_used).days
        recency_score = max(0.0, 1 - days_since_used / 365)  # 一年后新鲜度为0
        
        # 计算更新频率分数
        last_updated = datetime.fromisoformat(page_data.get("last_updated", datetime.now().isoformat()))
        days_since_updated = (datetime.now() - last_updated).days
        update_score = max(0.0, 1 - days_since_updated / 180)  # 半年后更新分数为0
        
        # 综合计算重要性
        importance_score = (
            confidence_score * 0.4 +
            usage_score * 0.3 +
            recency_score * 0.2 +
            update_score * 0.1
        )
        
        return min(1.0, max(0.0, importance_score))
    
    def _determine_status(self, page_data):
        """确定页面状态
        
        Args:
            page_data: 页面数据
            
        Returns:
            状态 (active, dimmed, archived)
        """
        importance_score = page_data.get("importance_score", 0.5)
        
        if importance_score >= 0.6:
            return "active"
        elif importance_score >= 0.3:
            return "dimmed"
        else:
            return "archived"
    
    def get_page_status(self, page_id):
        """获取页面状态
        
        Args:
            page_id: 页面ID
            
        Returns:
            页面状态
        """
        if page_id in self.metadata["pages"]:
            return self.metadata["pages"][page_id].get("status", "active")
        return "active"
    
    def get_page_importance(self, page_id):
        """获取页面重要性
        
        Args:
            page_id: 页面ID
            
        Returns:
            重要性分数
        """
        if page_id in self.metadata["pages"]:
            return self.metadata["pages"][page_id].get("importance_score", 0.5)
        return 0.5
    
    def get_low_importance_pages(self, threshold=0.3):
        """获取低重要性页面
        
        Args:
            threshold: 重要性阈值
            
        Returns:
            低重要性页面列表
        """
        low_importance_pages = []
        
        for page_id, page_data in self.metadata["pages"].items():
            importance_score = page_data.get("importance_score", 0.5)
            if importance_score < threshold:
                low_importance_pages.append({
                    "page_id": page_id,
                    "importance_score": importance_score,
                    "status": page_data.get("status", "active"),
                    "last_used": page_data.get("last_used"),
                    "usage_count": page_data.get("usage_count", 0)
                })
        
        return low_importance_pages
    
    def get_archived_pages(self):
        """获取已归档页面
        
        Returns:
            已归档页面列表
        """
        archived_pages = []
        
        for page_id, page_data in self.metadata["pages"].items():
            if page_data.get("status") == "archived":
                archived_pages.append({
                    "page_id": page_id,
                    "importance_score": page_data.get("importance_score", 0.5),
                    "last_used": page_data.get("last_used"),
                    "archived_at": page_data.get("last_updated")
                })
        
        return archived_pages
    
    def cleanup(self, days=90):
        """清理过期内容
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        cleanup_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        archived_count = 0
        
        for page_id, page_data in list(self.metadata["pages"].items()):
            last_used = datetime.fromisoformat(page_data.get("last_used", datetime.now().isoformat()))
            
            if last_used < cleanup_date:
                # 对于长期未使用的页面，降低其重要性
                page_data["importance_score"] = max(0.0, page_data.get("importance_score", 0.5) - 0.2)
                page_data["status"] = self._determine_status(page_data)
                
                if page_data["status"] == "archived":
                    archived_count += 1
                
                cleaned_count += 1
        
        self.metadata["last_cleanup"] = datetime.now().isoformat()
        self._save_metadata()
        
        return {
            "status": "completed",
            "cleaned_count": cleaned_count,
            "archived_count": archived_count
        }
    
    def restore_page(self, page_id):
        """恢复页面
        
        Args:
            page_id: 页面ID
            
        Returns:
            恢复结果
        """
        if page_id in self.metadata["pages"]:
            page_data = self.metadata["pages"][page_id]
            page_data["status"] = "active"
            page_data["importance_score"] = 0.6  # 恢复到中等重要性
            page_data["last_used"] = datetime.now().isoformat()
            self._save_metadata()
            return {
                "status": "success",
                "message": "页面已恢复"
            }
        
        return {
            "status": "error",
            "message": "页面不存在"
        }
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        total_pages = len(self.metadata["pages"])
        active_pages = 0
        dimmed_pages = 0
        archived_pages = 0
        total_importance = 0
        
        for page_data in self.metadata["pages"].values():
            status = page_data.get("status", "active")
            if status == "active":
                active_pages += 1
            elif status == "dimmed":
                dimmed_pages += 1
            elif status == "archived":
                archived_pages += 1
            
            total_importance += page_data.get("importance_score", 0.5)
        
        average_importance = total_importance / total_pages if total_pages > 0 else 0
        
        return {
            "total_pages": total_pages,
            "active_pages": active_pages,
            "dimmed_pages": dimmed_pages,
            "archived_pages": archived_pages,
            "average_importance": round(average_importance, 2),
            "last_cleanup": self.metadata.get("last_cleanup")
        }

class ForgettingManager:
    """遗忘曲线管理器"""
    
    def __init__(self):
        """初始化遗忘曲线管理器"""
        self.forgetting_curve = ForgettingCurve()
    
    def record_usage(self, page_id):
        """记录页面使用
        
        Args:
            page_id: 页面ID
        """
        self.forgetting_curve.update_page_metadata(page_id, usage=True)
    
    def record_update(self, page_id):
        """记录页面更新
        
        Args:
            page_id: 页面ID
        """
        self.forgetting_curve.update_page_metadata(page_id, usage=False)
    
    def get_page_status(self, page_id):
        """获取页面状态
        
        Args:
            page_id: 页面ID
            
        Returns:
            页面状态
        """
        return self.forgetting_curve.get_page_status(page_id)
    
    def get_page_importance(self, page_id):
        """获取页面重要性
        
        Args:
            page_id: 页面ID
            
        Returns:
            重要性分数
        """
        return self.forgetting_curve.get_page_importance(page_id)
    
    def get_low_importance_pages(self, threshold=0.3):
        """获取低重要性页面
        
        Args:
            threshold: 重要性阈值
            
        Returns:
            低重要性页面列表
        """
        return self.forgetting_curve.get_low_importance_pages(threshold)
    
    def get_archived_pages(self):
        """获取已归档页面
        
        Returns:
            已归档页面列表
        """
        return self.forgetting_curve.get_archived_pages()
    
    def cleanup(self, days=90):
        """清理过期内容
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        return self.forgetting_curve.cleanup(days)
    
    def restore_page(self, page_id):
        """恢复页面
        
        Args:
            page_id: 页面ID
            
        Returns:
            恢复结果
        """
        return self.forgetting_curve.restore_page(page_id)
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        return self.forgetting_curve.get_statistics()
