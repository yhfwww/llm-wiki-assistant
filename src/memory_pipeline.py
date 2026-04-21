# src/memory_pipeline.py
"""四层记忆流水线"""

from datetime import datetime, timedelta
import json
from pathlib import Path
import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat

class MemoryPipeline:
    """四层记忆流水线"""
    
    def __init__(self):
        """初始化记忆流水线"""
        self.pipeline_path = Path(os.getenv("MEMORY_PIPELINE_PATH", "memory_pipeline"))
        self.pipeline_path.mkdir(parents=True, exist_ok=True)
        self.observations_file = self.pipeline_path / "observations.json"
        self.summaries_file = self.pipeline_path / "summaries.json"
        self.facts_file = self.pipeline_path / "facts.json"
        self.workflows_file = self.pipeline_path / "workflows.json"
        self._load_data()
        self._initialize_agent()
    
    def _load_data(self):
        """加载数据"""
        # 加载短期观察
        if self.observations_file.exists():
            with open(self.observations_file, "r", encoding="utf-8") as f:
                self.observations = json.load(f)
        else:
            self.observations = []
        
        # 加载会话摘要
        if self.summaries_file.exists():
            with open(self.summaries_file, "r", encoding="utf-8") as f:
                self.summaries = json.load(f)
        else:
            self.summaries = []
        
        # 加载事实
        if self.facts_file.exists():
            with open(self.facts_file, "r", encoding="utf-8") as f:
                self.facts = json.load(f)
        else:
            self.facts = []
        
        # 加载工作流程
        if self.workflows_file.exists():
            with open(self.workflows_file, "r", encoding="utf-8") as f:
                self.workflows = json.load(f)
        else:
            self.workflows = []
    
    def _save_data(self):
        """保存数据"""
        # 保存短期观察
        with open(self.observations_file, "w", encoding="utf-8") as f:
            json.dump(self.observations, f, ensure_ascii=False, indent=2)
        
        # 保存会话摘要
        with open(self.summaries_file, "w", encoding="utf-8") as f:
            json.dump(self.summaries, f, ensure_ascii=False, indent=2)
        
        # 保存事实
        with open(self.facts_file, "w", encoding="utf-8") as f:
            json.dump(self.facts, f, ensure_ascii=False, indent=2)
        
        # 保存工作流程
        with open(self.workflows_file, "w", encoding="utf-8") as f:
            json.dump(self.workflows, f, ensure_ascii=False, indent=2)
    
    def _initialize_agent(self):
        """初始化处理代理"""
        llm_model = os.getenv("LLM_MODEL_ID", "Qwen/Qwen3.5-4B")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
        
        self.agent = Agent(
            name="Memory Pipeline Agent",
            model=OpenAIChat(id=llm_model, base_url=openai_base_url),
            description="你是一个记忆处理助手，负责处理和转换不同层次的记忆。",
            instructions=[
                "将短期观察总结为会话摘要",
                "从会话摘要中提取事实",
                "从事实中识别工作流程和模式",
                "保持内容准确、简洁、结构化"
            ],
            markdown=True
        )
    
    def add_observation(self, content, context=None):
        """添加短期观察
        
        Args:
            content: 观察内容
            context: 上下文信息
            
        Returns:
            添加结果
        """
        observation = {
            "observation_id": f"obs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "content": content,
            "context": context or {},
            "created_at": datetime.now().isoformat(),
            "status": "raw"
        }
        
        self.observations.append(observation)
        self._save_data()
        
        # 自动处理观察
        self.process_observations()
        
        return {
            "status": "success",
            "message": "观察添加成功",
            "observation_id": observation["observation_id"]
        }
    
    def process_observations(self):
        """处理短期观察，生成会话摘要"""
        # 处理未处理的观察
        unprocessed_observations = [obs for obs in self.observations if obs["status"] == "raw"]
        
        for observation in unprocessed_observations:
            # 生成会话摘要
            summary = self._generate_summary(observation)
            if summary:
                # 标记观察为已处理
                observation["status"] = "processed"
                observation["summary_id"] = summary["summary_id"]
        
        self._save_data()
    
    def _generate_summary(self, observation):
        """生成会话摘要
        
        Args:
            observation: 观察信息
            
        Returns:
            摘要信息
        """
        prompt = f"""
请根据以下观察内容生成一个简洁的会话摘要：

观察内容：
{observation['content']}

上下文：
{json.dumps(observation['context'], ensure_ascii=False)}

摘要应包括：
1. 主要事件
2. 关键信息
3. 相关实体
4. 时间和地点（如果适用）

请以JSON格式返回摘要，包含以下字段：
- summary: 摘要内容
- key_points: 关键点列表
- entities: 相关实体列表
- timestamp: 时间戳
        """
        
        try:
            response = self.agent.run(prompt)
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                summary_data = json.loads(json_match.group(1))
            else:
                summary_data = json.loads(response)
            
            summary = {
                "summary_id": f"sum_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "observation_id": observation["observation_id"],
                "content": summary_data.get("summary", ""),
                "key_points": summary_data.get("key_points", []),
                "entities": summary_data.get("entities", []),
                "created_at": datetime.now().isoformat(),
                "status": "generated"
            }
            
            self.summaries.append(summary)
            
            # 自动提取事实
            self.extract_facts(summary)
            
            return summary
        except Exception as e:
            print(f"生成摘要失败: {str(e)}")
            return None
    
    def extract_facts(self, summary):
        """从会话摘要中提取事实
        
        Args:
            summary: 会话摘要
        """
        prompt = f"""
请从以下会话摘要中提取具体事实：

摘要内容：
{summary['content']}

关键点：
{"\n".join([f"- {point}" for point in summary['key_points']])}

实体：
{"\n".join([f"- {entity}" for entity in summary['entities']])}

请提取的事实应满足：
1. 具体明确
2. 可验证
3. 包含必要的上下文
4. 按主题组织

请以JSON格式返回提取的事实，包含以下字段：
- facts: 事实列表，每个事实包含 fact_id, content, category, entities, confidence
- categories: 事实类别列表
        """
        
        try:
            response = self.agent.run(prompt)
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                facts_data = json.loads(json_match.group(1))
            else:
                facts_data = json.loads(response)
            
            for fact_data in facts_data.get("facts", []):
                fact = {
                    "fact_id": f"fact_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.facts)}",
                    "summary_id": summary["summary_id"],
                    "content": fact_data.get("content", ""),
                    "category": fact_data.get("category", "general"),
                    "entities": fact_data.get("entities", []),
                    "confidence": fact_data.get("confidence", 0.8),
                    "created_at": datetime.now().isoformat(),
                    "status": "extracted"
                }
                self.facts.append(fact)
            
            # 自动识别工作流程
            self.identify_workflows(facts_data.get("facts", []))
        except Exception as e:
            print(f"提取事实失败: {str(e)}")
    
    def identify_workflows(self, facts):
        """从事实中识别工作流程
        
        Args:
            facts: 事实列表
        """
        if not facts:
            return
        
        prompt = f"""
请从以下事实中识别工作流程和模式：

事实：
{"\n".join([f"- {fact.get('content', '')}" for fact in facts])}

请识别：
1. 工作流程步骤
2. 模式和规律
3. 因果关系
4. 最佳实践

请以JSON格式返回识别结果，包含以下字段：
- workflow: 工作流程描述
- steps: 步骤列表
- patterns: 识别的模式
- dependencies: 依赖关系
        """
        
        try:
            response = self.agent.run(prompt)
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                workflow_data = json.loads(json_match.group(1))
            else:
                workflow_data = json.loads(response)
            
            workflow = {
                "workflow_id": f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "content": workflow_data.get("workflow", ""),
                "steps": workflow_data.get("steps", []),
                "patterns": workflow_data.get("patterns", []),
                "dependencies": workflow_data.get("dependencies", []),
                "created_at": datetime.now().isoformat(),
                "status": "identified"
            }
            
            self.workflows.append(workflow)
        except Exception as e:
            print(f"识别工作流程失败: {str(e)}")
    
    def get_observations(self, limit=10):
        """获取短期观察
        
        Args:
            limit: 返回数量限制
            
        Returns:
            观察列表
        """
        return self.observations[-limit:]
    
    def get_summaries(self, limit=10):
        """获取会话摘要
        
        Args:
            limit: 返回数量限制
            
        Returns:
            摘要列表
        """
        return self.summaries[-limit:]
    
    def get_facts(self, category=None, limit=10):
        """获取事实
        
        Args:
            category: 事实类别
            limit: 返回数量限制
            
        Returns:
            事实列表
        """
        if category:
            filtered_facts = [fact for fact in self.facts if fact.get("category") == category]
            return filtered_facts[-limit:]
        return self.facts[-limit:]
    
    def get_workflows(self, limit=10):
        """获取工作流程
        
        Args:
            limit: 返回数量限制
            
        Returns:
            工作流程列表
        """
        return self.workflows[-limit:]
    
    def clean_old_memory(self, days=30):
        """清理旧记忆
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        # 清理旧观察
        new_observations = []
        for obs in self.observations:
            created_at = datetime.fromisoformat(obs["created_at"])
            if created_at > cutoff_date:
                new_observations.append(obs)
            else:
                cleaned_count += 1
        
        self.observations = new_observations
        self._save_data()
        
        return {
            "status": "completed",
            "cleaned_count": cleaned_count
        }
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        total_observations = len(self.observations)
        total_summaries = len(self.summaries)
        total_facts = len(self.facts)
        total_workflows = len(self.workflows)
        
        # 计算处理率
        processed_observations = sum(1 for obs in self.observations if obs["status"] == "processed")
        processing_rate = processed_observations / total_observations if total_observations > 0 else 0
        
        return {
            "total_observations": total_observations,
            "total_summaries": total_summaries,
            "total_facts": total_facts,
            "total_workflows": total_workflows,
            "processing_rate": round(processing_rate, 2)
        }

class MemoryPipelineManager:
    """记忆流水线管理器"""
    
    def __init__(self):
        """初始化记忆流水线管理器"""
        self.memory_pipeline = MemoryPipeline()
    
    def add_observation(self, content, context=None):
        """添加短期观察
        
        Args:
            content: 观察内容
            context: 上下文信息
            
        Returns:
            添加结果
        """
        return self.memory_pipeline.add_observation(content, context)
    
    def process_observations(self):
        """处理短期观察"""
        self.memory_pipeline.process_observations()
    
    def get_observations(self, limit=10):
        """获取短期观察
        
        Args:
            limit: 返回数量限制
            
        Returns:
            观察列表
        """
        return self.memory_pipeline.get_observations(limit)
    
    def get_summaries(self, limit=10):
        """获取会话摘要
        
        Args:
            limit: 返回数量限制
            
        Returns:
            摘要列表
        """
        return self.memory_pipeline.get_summaries(limit)
    
    def get_facts(self, category=None, limit=10):
        """获取事实
        
        Args:
            category: 事实类别
            limit: 返回数量限制
            
        Returns:
            事实列表
        """
        return self.memory_pipeline.get_facts(category, limit)
    
    def get_workflows(self, limit=10):
        """获取工作流程
        
        Args:
            limit: 返回数量限制
            
        Returns:
            工作流程列表
        """
        return self.memory_pipeline.get_workflows(limit)
    
    def clean_old_memory(self, days=30):
        """清理旧记忆
        
        Args:
            days: 天数阈值
            
        Returns:
            清理结果
        """
        return self.memory_pipeline.clean_old_memory(days)
    
    def get_statistics(self):
        """获取统计信息
        
        Returns:
            统计信息
        """
        return self.memory_pipeline.get_statistics()
