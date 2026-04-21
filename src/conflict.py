# src/conflict.py
"""矛盾解决机制"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import os
from src.schema import SchemaManager
from src.confidence import ConfidenceManager

class ConflictResolver:
    """矛盾解决器"""
    
    def __init__(self):
        """初始化矛盾解决器"""
        self.schema_manager = SchemaManager()
        self.confidence_manager = ConfidenceManager()
        self.conflict_path = Path(os.getenv("CONFLICT_PATH", "conflicts"))
        self.conflict_path.mkdir(parents=True, exist_ok=True)
        self.conflict_file = self.conflict_path / "conflicts.json"
        self._load_conflicts()
    
    def _load_conflicts(self):
        """加载冲突记录"""
        if self.conflict_file.exists():
            with open(self.conflict_file, "r", encoding="utf-8") as f:
                self.conflicts = json.load(f)
        else:
            self.conflicts = {
                "active": [],
                "resolved": []
            }
    
    def _save_conflicts(self):
        """保存冲突记录"""
        with open(self.conflict_file, "w", encoding="utf-8") as f:
            json.dump(self.conflicts, f, ensure_ascii=False, indent=2)
    
    def detect_conflict(self, page_id, old_content, new_content):
        """检测冲突
        
        Args:
            page_id: 页面ID
            old_content: 旧内容
            new_content: 新内容
            
        Returns:
            冲突检测结果
        """
        conflicts = []
        
        # 提取关键信息进行比较
        old_info = self._extract_info(old_content)
        new_info = self._extract_info(new_content)
        
        # 检测事实性冲突
        factual_conflicts = self._detect_factual_conflicts(old_info, new_info)
        if factual_conflicts:
            conflicts.extend(factual_conflicts)
        
        # 检测时间性冲突
        temporal_conflicts = self._detect_temporal_conflicts(old_info, new_info)
        if temporal_conflicts:
            conflicts.extend(temporal_conflicts)
        
        # 检测解释性冲突
        interpretive_conflicts = self._detect_interpretive_conflicts(old_info, new_info)
        if interpretive_conflicts:
            conflicts.extend(interpretive_conflicts)
        
        return conflicts
    
    def _extract_info(self, content):
        """从内容中提取关键信息
        
        Args:
            content: 页面内容
            
        Returns:
            提取的信息
        """
        import re
        info = {
            "facts": [],
            "dates": [],
            "numbers": [],
            "interpretations": []
        }
        
        # 提取事实陈述
        fact_patterns = [
            r'\b(是|为|有|在|位于)\b.*?[。！？]',
            r'\b(成立于|创建于|发明于)\b.*?[。！？]',
            r'\b(主要|核心|重要)\b.*?[。！？]'
        ]
        
        for pattern in fact_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            info["facts"].extend(matches)
        
        # 提取日期
        date_patterns = [
            r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?',
            r'\d{4}年\d{1,2}月',
            r'\d{4}年'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            info["dates"].extend(matches)
        
        # 提取数字
        number_patterns = [
            r'\b\d+\b',
            r'\b\d+\.\d+\b'
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, content)
            info["numbers"].extend(matches)
        
        # 提取解释性内容
        interpretive_patterns = [
            r'\b(认为|认为是|觉得|看来|似乎)\b.*?[。！？]',
            r'\b(可能|或许|大概|应该)\b.*?[。！？]',
            r'\b(意义|影响|作用|价值)\b.*?[。！？]'
        ]
        
        for pattern in interpretive_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            info["interpretations"].extend(matches)
        
        return info
    
    def _detect_factual_conflicts(self, old_info, new_info):
        """检测事实性冲突
        
        Args:
            old_info: 旧信息
            new_info: 新信息
            
        Returns:
            事实性冲突列表
        """
        conflicts = []
        
        # 简单的事实冲突检测
        for old_fact in old_info["facts"]:
            for new_fact in new_info["facts"]:
                if self._is_conflicting(old_fact, new_fact):
                    conflicts.append({
                        "type": "factual",
                        "old_value": old_fact,
                        "new_value": new_fact,
                        "severity": "high"
                    })
        
        return conflicts
    
    def _detect_temporal_conflicts(self, old_info, new_info):
        """检测时间性冲突
        
        Args:
            old_info: 旧信息
            new_info: 新信息
            
        Returns:
            时间性冲突列表
        """
        conflicts = []
        
        # 检测日期冲突
        for old_date in old_info["dates"]:
            for new_date in new_info["dates"]:
                if old_date != new_date:
                    conflicts.append({
                        "type": "temporal",
                        "old_value": old_date,
                        "new_value": new_date,
                        "severity": "medium"
                    })
        
        return conflicts
    
    def _detect_interpretive_conflicts(self, old_info, new_info):
        """检测解释性冲突
        
        Args:
            old_info: 旧信息
            new_info: 新信息
            
        Returns:
            解释性冲突列表
        """
        conflicts = []
        
        # 检测解释性冲突
        for old_interpretation in old_info["interpretations"]:
            for new_interpretation in new_info["interpretations"]:
                if self._is_conflicting(old_interpretation, new_interpretation):
                    conflicts.append({
                        "type": "interpretive",
                        "old_value": old_interpretation,
                        "new_value": new_interpretation,
                        "severity": "low"
                    })
        
        return conflicts
    
    def _is_conflicting(self, old_value, new_value):
        """判断两个值是否冲突
        
        Args:
            old_value: 旧值
            new_value: 新值
            
        Returns:
            是否冲突
        """
        # 简单的冲突检测逻辑
        # 实际应用中可能需要更复杂的自然语言处理
        old_value = old_value.lower()
        new_value = new_value.lower()
        
        # 检查是否有明显的矛盾词汇
        conflict_pairs = [
            ("是", "不是"),
            ("有", "没有"),
            ("成立于", "创建于"),  # 这些可能不是冲突，需要更复杂的逻辑
            ("增加", "减少"),
            ("上升", "下降")
        ]
        
        for pair in conflict_pairs:
            if pair[0] in old_value and pair[1] in new_value:
                return True
            if pair[1] in old_value and pair[0] in new_value:
                return True
        
        return False
    
    def resolve_conflict(self, page_id, conflicts, confidence):
        """解决冲突
        
        Args:
            page_id: 页面ID
            conflicts: 冲突列表
            confidence: 新信息的置信度
            
        Returns:
            解决结果
        """
        resolved_conflicts = []
        unresolved_conflicts = []
        
        for conflict in conflicts:
            # 使用Schema中定义的冲突解决策略
            resolved_value = self.schema_manager.resolve_conflict(
                conflict["type"],
                conflict["old_value"],
                conflict["new_value"],
                confidence
            )
            
            if isinstance(resolved_value, dict) and "_conflict" in resolved_value:
                # 需要人工审核的冲突
                unresolved_conflicts.append({
                    "conflict": conflict,
                    "resolved_value": resolved_value
                })
            else:
                # 自动解决的冲突
                resolved_conflicts.append({
                    "conflict": conflict,
                    "resolved_value": resolved_value,
                    "strategy": "auto"
                })
        
        # 记录冲突
        if unresolved_conflicts:
            self._record_conflicts(page_id, unresolved_conflicts)
        
        return {
            "resolved": resolved_conflicts,
            "unresolved": unresolved_conflicts,
            "total_conflicts": len(conflicts),
            "resolved_count": len(resolved_conflicts),
            "unresolved_count": len(unresolved_conflicts)
        }
    
    def _record_conflicts(self, page_id, conflicts):
        """记录冲突
        
        Args:
            page_id: 页面ID
            conflicts: 冲突列表
        """
        for conflict_info in conflicts:
            conflict = conflict_info["conflict"]
            self.conflicts["active"].append({
                "conflict_id": f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{page_id}",
                "page_id": page_id,
                "conflict": conflict,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            })
        
        self._save_conflicts()
    
    def resolve_manually(self, conflict_id, resolution):
        """手动解决冲突
        
        Args:
            conflict_id: 冲突ID
            resolution: 解决方案
            
        Returns:
            解决结果
        """
        for i, conflict in enumerate(self.conflicts["active"]):
            if conflict["conflict_id"] == conflict_id:
                # 标记为已解决
                conflict["status"] = "resolved"
                conflict["resolved_at"] = datetime.now().isoformat()
                conflict["resolution"] = resolution
                
                # 移到已解决列表
                resolved_conflict = self.conflicts["active"].pop(i)
                self.conflicts["resolved"].append(resolved_conflict)
                
                self._save_conflicts()
                return {
                    "status": "success",
                    "message": "冲突已解决"
                }
        
        return {
            "status": "error",
            "message": "冲突不存在"
        }
    
    def get_active_conflicts(self):
        """获取未解决的冲突
        
        Returns:
            未解决的冲突列表
        """
        return self.conflicts["active"]
    
    def get_resolved_conflicts(self):
        """获取已解决的冲突
        
        Returns:
            已解决的冲突列表
        """
        return self.conflicts["resolved"]
    
    def get_conflicts_by_page(self, page_id):
        """获取指定页面的冲突
        
        Args:
            page_id: 页面ID
            
        Returns:
            冲突列表
        """
        page_conflicts = []
        
        for conflict in self.conflicts["active"]:
            if conflict["page_id"] == page_id:
                page_conflicts.append(conflict)
        
        for conflict in self.conflicts["resolved"]:
            if conflict["page_id"] == page_id:
                page_conflicts.append(conflict)
        
        return page_conflicts
    
    def clean_old_conflicts(self, days=30):
        """清理旧冲突
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        # 清理已解决的旧冲突
        resolved_conflicts = []
        for conflict in self.conflicts["resolved"]:
            resolved_at = datetime.fromisoformat(conflict["resolved_at"])
            if resolved_at > cutoff_date:
                resolved_conflicts.append(conflict)
            else:
                cleaned_count += 1
        
        self.conflicts["resolved"] = resolved_conflicts
        self._save_conflicts()
        
        return {
            "status": "completed",
            "cleaned_count": cleaned_count
        }

class ConflictManager:
    """冲突管理器"""
    
    def __init__(self):
        """初始化冲突管理器"""
        self.conflict_resolver = ConflictResolver()
    
    def detect_conflict(self, page_id, old_content, new_content):
        """检测冲突
        
        Args:
            page_id: 页面ID
            old_content: 旧内容
            new_content: 新内容
            
        Returns:
            冲突检测结果
        """
        return self.conflict_resolver.detect_conflict(page_id, old_content, new_content)
    
    def resolve_conflict(self, page_id, conflicts, confidence):
        """解决冲突
        
        Args:
            page_id: 页面ID
            conflicts: 冲突列表
            confidence: 新信息的置信度
            
        Returns:
            解决结果
        """
        return self.conflict_resolver.resolve_conflict(page_id, conflicts, confidence)
    
    def resolve_manually(self, conflict_id, resolution):
        """手动解决冲突
        
        Args:
            conflict_id: 冲突ID
            resolution: 解决方案
            
        Returns:
            解决结果
        """
        return self.conflict_resolver.resolve_manually(conflict_id, resolution)
    
    def get_active_conflicts(self):
        """获取未解决的冲突
        
        Returns:
            未解决的冲突列表
        """
        return self.conflict_resolver.get_active_conflicts()
    
    def get_resolved_conflicts(self):
        """获取已解决的冲突
        
        Returns:
            已解决的冲突列表
        """
        return self.conflict_resolver.get_resolved_conflicts()
    
    def get_conflicts_by_page(self, page_id):
        """获取指定页面的冲突
        
        Args:
            page_id: 页面ID
            
        Returns:
            冲突列表
        """
        return self.conflict_resolver.get_conflicts_by_page(page_id)
    
    def clean_old_conflicts(self, days=30):
        """清理旧冲突
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        return self.conflict_resolver.clean_old_conflicts(days)
