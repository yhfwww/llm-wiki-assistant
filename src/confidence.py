# src/confidence.py
"""信心评分系统"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import os

class ConfidenceScore:
    """信心评分管理"""
    
    def __init__(self):
        """初始化信心评分系统"""
        self.confidence_path = Path(os.getenv("CONFIDENCE_PATH", "confidence"))
        self.confidence_path.mkdir(parents=True, exist_ok=True)
        self.score_file = self.confidence_path / "scores.json"
        self._load_scores()
    
    def _load_scores(self):
        """加载信心评分"""
        if self.score_file.exists():
            with open(self.score_file, "r", encoding="utf-8") as f:
                self.scores = json.load(f)
        else:
            self.scores = {}
    
    def _save_scores(self):
        """保存信心评分"""
        with open(self.score_file, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)
    
    def get_score(self, page_id):
        """获取页面的信心评分
        
        Args:
            page_id: 页面ID
            
        Returns:
            信心评分 (0-1)
        """
        if page_id in self.scores:
            score_data = self.scores[page_id]
            # 计算时间衰减
            current_score = self._calculate_decayed_score(score_data)
            return current_score
        return 0.5  # 默认中等信心
    
    def set_score(self, page_id, score, source_quality=0.8, consistency=1.0):
        """设置页面的信心评分
        
        Args:
            page_id: 页面ID
            score: 信心评分 (0-1)
            source_quality: 源质量 (0-1)
            consistency: 一致性 (0-1)
        """
        self.scores[page_id] = {
            "score": min(1.0, max(0.0, score)),
            "source_quality": source_quality,
            "consistency": consistency,
            "last_updated": datetime.now().isoformat(),
            "usage_count": self.scores.get(page_id, {}).get("usage_count", 0)
        }
        self._save_scores()
    
    def update_score(self, page_id, delta=0.1, reason="update"):
        """更新页面的信心评分
        
        Args:
            page_id: 页面ID
            delta: 评分变化值
            reason: 更新原因
        """
        current_score = self.get_score(page_id)
        new_score = min(1.0, max(0.0, current_score + delta))
        
        if page_id in self.scores:
            self.scores[page_id].update({
                "score": new_score,
                "last_updated": datetime.now().isoformat()
            })
        else:
            self.scores[page_id] = {
                "score": new_score,
                "source_quality": 0.8,
                "consistency": 1.0,
                "last_updated": datetime.now().isoformat(),
                "usage_count": 0
            }
        
        # 记录更新原因
        if "update_history" not in self.scores[page_id]:
            self.scores[page_id]["update_history"] = []
        
        self.scores[page_id]["update_history"].append({
            "timestamp": datetime.now().isoformat(),
            "delta": delta,
            "reason": reason,
            "new_score": new_score
        })
        
        self._save_scores()
        return new_score
    
    def _calculate_decayed_score(self, score_data):
        """计算时间衰减后的评分
        
        Args:
            score_data: 评分数据
            
        Returns:
            衰减后的评分
        """
        last_updated = datetime.fromisoformat(score_data["last_updated"])
        days_since_update = (datetime.now() - last_updated).days
        
        # 基础衰减率：每天0.01
        decay_rate = 0.01
        # 源质量影响衰减率
        source_quality = score_data.get("source_quality", 0.8)
        adjusted_decay_rate = decay_rate * (1 - source_quality * 0.5)
        
        # 计算衰减
        decay_amount = days_since_update * adjusted_decay_rate
        current_score = max(0.1, score_data["score"] - decay_amount)
        
        # 如果评分发生了显著变化，更新存储
        if abs(current_score - score_data["score"]) > 0.05:
            score_data["score"] = current_score
            score_data["last_updated"] = datetime.now().isoformat()
            self._save_scores()
        
        return current_score
    
    def record_usage(self, page_id):
        """记录页面使用，增强信心
        
        Args:
            page_id: 页面ID
        """
        if page_id in self.scores:
            self.scores[page_id]["usage_count"] = self.scores[page_id].get("usage_count", 0) + 1
            # 每使用5次，增加0.05的信心
            if self.scores[page_id]["usage_count"] % 5 == 0:
                self.update_score(page_id, 0.05, "usage_increase")
            self._save_scores()
        else:
            # 首次使用，设置初始评分
            self.set_score(page_id, 0.6, 0.8, 1.0)
    
    def calculate_initial_score(self, source_type, content_length, source_quality):
        """计算初始信心评分
        
        Args:
            source_type: 源类型
            content_length: 内容长度
            source_quality: 源质量
            
        Returns:
            初始评分
        """
        # 基础评分
        base_score = 0.5
        
        # 源类型加成
        source_boost = {
            "paper": 0.3,
            "document": 0.2,
            "website": 0.1,
            "interview": 0.15,
            "social_media": -0.1
        }
        base_score += source_boost.get(source_type, 0)
        
        # 内容长度加成（适中长度最佳）
        if 500 <= content_length <= 2000:
            base_score += 0.1
        elif content_length > 2000:
            base_score += 0.05
        
        # 源质量加成
        base_score += source_quality * 0.2
        
        return min(1.0, max(0.1, base_score))
    
    def batch_update(self):
        """批量更新所有页面的信心评分
        
        Returns:
            更新结果
        """
        updated_count = 0
        for page_id in list(self.scores.keys()):
            # 触发衰减计算
            self.get_score(page_id)
            updated_count += 1
        
        return {
            "status": "completed",
            "updated_count": updated_count
        }
    
    def get_low_confidence_pages(self, threshold=0.3):
        """获取低信心页面
        
        Args:
            threshold: 信心阈值
            
        Returns:
            低信心页面列表
        """
        low_confidence_pages = []
        for page_id, score_data in self.scores.items():
            current_score = self.get_score(page_id)
            if current_score < threshold:
                low_confidence_pages.append({
                    "page_id": page_id,
                    "score": current_score,
                    "last_updated": score_data.get("last_updated"),
                    "usage_count": score_data.get("usage_count", 0)
                })
        
        return low_confidence_pages
    
    def get_confidence_stats(self):
        """获取信心评分统计
        
        Returns:
            统计信息
        """
        scores = []
        for page_id in self.scores:
            scores.append(self.get_score(page_id))
        
        if not scores:
            return {
                "total_pages": 0,
                "average_score": 0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0
            }
        
        average_score = sum(scores) / len(scores)
        high_confidence = sum(1 for s in scores if s >= 0.7)
        medium_confidence = sum(1 for s in scores if 0.4 <= s < 0.7)
        low_confidence = sum(1 for s in scores if s < 0.4)
        
        return {
            "total_pages": len(scores),
            "average_score": round(average_score, 2),
            "high_confidence_count": high_confidence,
            "medium_confidence_count": medium_confidence,
            "low_confidence_count": low_confidence
        }

class ConfidenceManager:
    """信心评分管理器"""
    
    def __init__(self):
        """初始化信心评分管理器"""
        self.confidence_score = ConfidenceScore()
    
    def get_score(self, page_id):
        """获取页面信心评分
        
        Args:
            page_id: 页面ID
            
        Returns:
            信心评分
        """
        return self.confidence_score.get_score(page_id)
    
    def set_score(self, page_id, score, source_quality=0.8, consistency=1.0):
        """设置页面信心评分
        
        Args:
            page_id: 页面ID
            score: 信心评分
            source_quality: 源质量
            consistency: 一致性
        """
        self.confidence_score.set_score(page_id, score, source_quality, consistency)
    
    def update_score(self, page_id, delta=0.1, reason="update"):
        """更新页面信心评分
        
        Args:
            page_id: 页面ID
            delta: 评分变化值
            reason: 更新原因
            
        Returns:
            新的评分
        """
        return self.confidence_score.update_score(page_id, delta, reason)
    
    def record_usage(self, page_id):
        """记录页面使用
        
        Args:
            page_id: 页面ID
        """
        self.confidence_score.record_usage(page_id)
    
    def calculate_initial_score(self, source_type, content_length, source_quality):
        """计算初始信心评分
        
        Args:
            source_type: 源类型
            content_length: 内容长度
            source_quality: 源质量
            
        Returns:
            初始评分
        """
        return self.confidence_score.calculate_initial_score(source_type, content_length, source_quality)
    
    def batch_update(self):
        """批量更新所有页面的信心评分
        
        Returns:
            更新结果
        """
        return self.confidence_score.batch_update()
    
    def get_low_confidence_pages(self, threshold=0.3):
        """获取低信心页面
        
        Args:
            threshold: 信心阈值
            
        Returns:
            低信心页面列表
        """
        return self.confidence_score.get_low_confidence_pages(threshold)
    
    def get_confidence_stats(self):
        """获取信心评分统计
        
        Returns:
            统计信息
        """
        return self.confidence_score.get_confidence_stats()
