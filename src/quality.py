# src/quality.py
"""自动质量检查和修复系统"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import os
from src.schema import SchemaManager
from src.confidence import ConfidenceManager

class QualityChecker:
    """质量检查器"""
    
    def __init__(self):
        """初始化质量检查器"""
        self.schema_manager = SchemaManager()
        self.confidence_manager = ConfidenceManager()
        self.quality_path = Path(os.getenv("QUALITY_PATH", "quality"))
        self.quality_path.mkdir(parents=True, exist_ok=True)
        self.issues_file = self.quality_path / "issues.json"
        self._load_issues()
    
    def _load_issues(self):
        """加载质量问题"""
        if self.issues_file.exists():
            with open(self.issues_file, "r", encoding="utf-8") as f:
                self.issues = json.load(f)
        else:
            self.issues = {
                "active": [],
                "fixed": [],
                "ignored": []
            }
    
    def _save_issues(self):
        """保存质量问题"""
        with open(self.issues_file, "w", encoding="utf-8") as f:
            json.dump(self.issues, f, ensure_ascii=False, indent=2)
    
    def check_page_quality(self, page_id, page_content, page_type):
        """检查页面质量
        
        Args:
            page_id: 页面ID
            page_content: 页面内容
            page_type: 页面类型
            
        Returns:
            质量检查结果
        """
        issues = []
        
        # 1. 检查Schema验证
        schema_valid, schema_message = self.schema_manager.validate_page(page_type, page_content)
        if not schema_valid:
            issues.append({
                "issue_id": f"schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{page_id}",
                "page_id": page_id,
                "type": "schema_validation",
                "severity": "high",
                "description": schema_message,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            })
        
        # 2. 检查内容完整性
        content_issues = self._check_content_integrity(page_content, page_type)
        issues.extend(content_issues)
        
        # 3. 检查格式问题
        format_issues = self._check_formatting(page_content)
        issues.extend(format_issues)
        
        # 4. 检查信心评分
        confidence_score = self.confidence_manager.get_score(page_id)
        if confidence_score < 0.5:
            issues.append({
                "issue_id": f"confidence_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{page_id}",
                "page_id": page_id,
                "type": "low_confidence",
                "severity": "medium",
                "description": f"页面信心评分过低: {confidence_score}",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            })
        
        # 记录问题
        for issue in issues:
            self.issues["active"].append(issue)
        
        self._save_issues()
        
        return {
            "status": "completed",
            "total_issues": len(issues),
            "issues": issues
        }
    
    def _check_content_integrity(self, content, page_type):
        """检查内容完整性
        
        Args:
            content: 页面内容
            page_type: 页面类型
            
        Returns:
            内容完整性问题列表
        """
        issues = []
        
        # 检查内容长度
        if len(content) < 100:
            issues.append({
                "issue_id": f"content_length_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "content_length",
                "severity": "medium",
                "description": "内容长度不足",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            })
        
        # 检查必需章节
        required_sections = self.schema_manager.get_schema().get("quality_standards", {}).get("required_sections", {}).get(page_type, [])
        for section in required_sections:
            if f"## {section}" not in content:
                issues.append({
                    "issue_id": f"missing_section_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{section}",
                    "type": "missing_section",
                    "severity": "high",
                    "description": f"缺少必需章节: {section}",
                    "created_at": datetime.now().isoformat(),
                    "status": "active"
                })
        
        # 检查参考资料
        if "参考资料" not in content:
            issues.append({
                "issue_id": f"missing_references_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "missing_references",
                "severity": "medium",
                "description": "缺少参考资料",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            })
        
        return issues
    
    def _check_formatting(self, content):
        """检查格式问题
        
        Args:
            content: 页面内容
            
        Returns:
            格式问题列表
        """
        issues = []
        
        # 检查标题格式
        lines = content.split('\n')
        heading_count = 0
        for line in lines:
            if line.startswith('## '):
                heading_count += 1
        
        if heading_count < 2:
            issues.append({
                "issue_id": f"format_headings_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "format_headings",
                "severity": "low",
                "description": "标题结构不足",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            })
        
        # 检查段落长度
        paragraphs = content.split('\n\n')
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 500:
                issues.append({
                    "issue_id": f"format_paragraph_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    "type": "format_paragraph",
                    "severity": "low",
                    "description": "段落过长",
                    "created_at": datetime.now().isoformat(),
                    "status": "active"
                })
        
        return issues
    
    def fix_issue(self, issue_id, fix_strategy="auto"):
        """修复质量问题
        
        Args:
            issue_id: 问题ID
            fix_strategy: 修复策略 (auto, manual)
            
        Returns:
            修复结果
        """
        for i, issue in enumerate(self.issues["active"]):
            if issue["issue_id"] == issue_id:
                # 标记为已修复
                issue["status"] = "fixed"
                issue["fixed_at"] = datetime.now().isoformat()
                issue["fix_strategy"] = fix_strategy
                
                # 移到已修复列表
                fixed_issue = self.issues["active"].pop(i)
                self.issues["fixed"].append(fixed_issue)
                
                self._save_issues()
                return {
                    "status": "success",
                    "message": "问题已修复"
                }
        
        return {
            "status": "error",
            "message": "问题不存在"
        }
    
    def ignore_issue(self, issue_id, reason="用户忽略"):
        """忽略质量问题
        
        Args:
            issue_id: 问题ID
            reason: 忽略原因
            
        Returns:
            忽略结果
        """
        for i, issue in enumerate(self.issues["active"]):
            if issue["issue_id"] == issue_id:
                # 标记为已忽略
                issue["status"] = "ignored"
                issue["ignored_at"] = datetime.now().isoformat()
                issue["ignore_reason"] = reason
                
                # 移到已忽略列表
                ignored_issue = self.issues["active"].pop(i)
                self.issues["ignored"].append(ignored_issue)
                
                self._save_issues()
                return {
                    "status": "success",
                    "message": "问题已忽略"
                }
        
        return {
            "status": "error",
            "message": "问题不存在"
        }
    
    def get_active_issues(self):
        """获取未解决的质量问题
        
        Returns:
            未解决的质量问题列表
        """
        return self.issues["active"]
    
    def get_fixed_issues(self):
        """获取已修复的质量问题
        
        Returns:
            已修复的质量问题列表
        """
        return self.issues["fixed"]
    
    def get_ignored_issues(self):
        """获取已忽略的质量问题
        
        Returns:
            已忽略的质量问题列表
        """
        return self.issues["ignored"]
    
    def get_issues_by_page(self, page_id):
        """获取指定页面的质量问题
        
        Args:
            page_id: 页面ID
            
        Returns:
            质量问题列表
        """
        page_issues = []
        
        for issue in self.issues["active"]:
            if issue.get("page_id") == page_id:
                page_issues.append(issue)
        
        for issue in self.issues["fixed"]:
            if issue.get("page_id") == page_id:
                page_issues.append(issue)
        
        for issue in self.issues["ignored"]:
            if issue.get("page_id") == page_id:
                page_issues.append(issue)
        
        return page_issues
    
    def get_issues_by_type(self, issue_type):
        """按类型获取质量问题
        
        Args:
            issue_type: 问题类型
            
        Returns:
            质量问题列表
        """
        issues = []
        
        for issue in self.issues["active"]:
            if issue.get("type") == issue_type:
                issues.append(issue)
        
        return issues
    
    def clean_old_issues(self, days=30):
        """清理旧问题
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        # 清理已修复的旧问题
        fixed_issues = []
        for issue in self.issues["fixed"]:
            fixed_at = datetime.fromisoformat(issue.get("fixed_at", datetime.now().isoformat()))
            if fixed_at > cutoff_date:
                fixed_issues.append(issue)
            else:
                cleaned_count += 1
        
        # 清理已忽略的旧问题
        ignored_issues = []
        for issue in self.issues["ignored"]:
            ignored_at = datetime.fromisoformat(issue.get("ignored_at", datetime.now().isoformat()))
            if ignored_at > cutoff_date:
                ignored_issues.append(issue)
            else:
                cleaned_count += 1
        
        self.issues["fixed"] = fixed_issues
        self.issues["ignored"] = ignored_issues
        self._save_issues()
        
        return {
            "status": "completed",
            "cleaned_count": cleaned_count
        }
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        total_issues = len(self.issues["active"]) + len(self.issues["fixed"]) + len(self.issues["ignored"])
        active_issues = len(self.issues["active"])
        fixed_issues = len(self.issues["fixed"])
        ignored_issues = len(self.issues["ignored"])
        
        issue_types = {}
        for issue in self.issues["active"]:
            issue_type = issue.get("type", "unknown")
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            "total_issues": total_issues,
            "active_issues": active_issues,
            "fixed_issues": fixed_issues,
            "ignored_issues": ignored_issues,
            "issue_types": issue_types
        }

class QualityManager:
    """质量管理器"""
    
    def __init__(self):
        """初始化质量管理器"""
        self.quality_checker = QualityChecker()
    
    def check_page_quality(self, page_id, page_content, page_type):
        """检查页面质量
        
        Args:
            page_id: 页面ID
            page_content: 页面内容
            page_type: 页面类型
            
        Returns:
            质量检查结果
        """
        return self.quality_checker.check_page_quality(page_id, page_content, page_type)
    
    def fix_issue(self, issue_id, fix_strategy="auto"):
        """修复质量问题
        
        Args:
            issue_id: 问题ID
            fix_strategy: 修复策略
            
        Returns:
            修复结果
        """
        return self.quality_checker.fix_issue(issue_id, fix_strategy)
    
    def ignore_issue(self, issue_id, reason="用户忽略"):
        """忽略质量问题
        
        Args:
            issue_id: 问题ID
            reason: 忽略原因
            
        Returns:
            忽略结果
        """
        return self.quality_checker.ignore_issue(issue_id, reason)
    
    def get_active_issues(self):
        """获取未解决的质量问题
        
        Returns:
            未解决的质量问题列表
        """
        return self.quality_checker.get_active_issues()
    
    def get_fixed_issues(self):
        """获取已修复的质量问题
        
        Returns:
            已修复的质量问题列表
        """
        return self.quality_checker.get_fixed_issues()
    
    def get_ignored_issues(self):
        """获取已忽略的质量问题
        
        Returns:
            已忽略的质量问题列表
        """
        return self.quality_checker.get_ignored_issues()
    
    def get_issues_by_page(self, page_id):
        """获取指定页面的质量问题
        
        Args:
            page_id: 页面ID
            
        Returns:
            质量问题列表
        """
        return self.quality_checker.get_issues_by_page(page_id)
    
    def get_issues_by_type(self, issue_type):
        """按类型获取质量问题
        
        Args:
            issue_type: 问题类型
            
        Returns:
            质量问题列表
        """
        return self.quality_checker.get_issues_by_type(issue_type)
    
    def clean_old_issues(self, days=30):
        """清理旧问题
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        return self.quality_checker.clean_old_issues(days)
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        return self.quality_checker.get_statistics()
