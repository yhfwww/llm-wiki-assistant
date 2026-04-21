# src/intelligent_ingest.py
"""智能导入系统"""

from pathlib import Path
import os
from datetime import datetime
from src.architecture import Architecture
from src.schema import SchemaManager
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import json

class IntelligentIngest:
    """智能导入系统"""
    
    def __init__(self):
        """初始化智能导入系统"""
        self.architecture = Architecture()
        self.schema_manager = SchemaManager()
        self._initialize_agent()
    
    def _initialize_agent(self):
        """初始化导入代理"""
        llm_model = os.getenv("LLM_MODEL_ID", "Qwen/Qwen3.5-4B")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1")
        
        self.agent = Agent(
            name="Intelligent Ingest Agent",
            model=OpenAIChat(id=llm_model, base_url=openai_base_url),
            description="你是一个智能导入助手，负责分析源文件并生成结构化的维基内容。",
            instructions=[
                "分析源文件内容，识别实体、概念和事件",
                "生成详细的摘要，包括核心内容和关键观点",
                "识别实体之间的关系",
                "按照Schema要求的格式生成内容",
                "保持内容准确、客观、全面"
            ],
            markdown=True
        )
    
    def ingest_source(self, file_path, source_type="document"):
        """智能导入源文件
        
        Args:
            file_path: 源文件路径
            source_type: 源文件类型
            
        Returns:
            导入结果
        """
        # 1. 添加源文件到原始资料层
        source_id = self.architecture.add_source(file_path, source_type)
        if not source_id:
            return {"status": "error", "message": "无法添加源文件"}
        
        # 2. 读取源文件内容
        source_path = self.architecture.raw_source_layer.get_source(source_id)
        if not source_path:
            return {"status": "error", "message": "无法读取源文件"}
        
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 3. 分析内容并生成摘要
        analysis_result = self._analyze_content(content, source_id)
        if analysis_result["status"] == "error":
            return analysis_result
        
        # 4. 生成维基页面
        pages_created = []
        
        # 生成摘要页面
        summary_page = self._create_summary_page(analysis_result, source_id)
        if summary_page:
            pages_created.append(summary_page)
        
        # 生成实体页面
        entity_pages = self._create_entity_pages(analysis_result, source_id)
        pages_created.extend(entity_pages)
        
        # 生成概念页面
        concept_pages = self._create_concept_pages(analysis_result, source_id)
        pages_created.extend(concept_pages)
        
        # 生成事件页面
        event_pages = self._create_event_pages(analysis_result, source_id)
        pages_created.extend(event_pages)
        
        return {
            "status": "success",
            "source_id": source_id,
            "pages_created": pages_created,
            "message": f"成功导入源文件，创建了 {len(pages_created)} 个维基页面"
        }
    
    def _analyze_content(self, content, source_id):
        """分析内容
        
        Args:
            content: 源文件内容
            source_id: 源文件ID
            
        Returns:
            分析结果
        """
        prompt = f"""
请分析以下内容，识别其中的：
1. 主要实体（人物、组织、概念、事件）
2. 实体之间的关系
3. 核心内容和关键观点
4. 时间线信息

内容：
{content[:4000]}...

请以JSON格式返回分析结果，包含以下字段：
- summary: 详细摘要
- entities: 实体列表，每个实体包含 type, name, properties, relationships
- concepts: 概念列表，每个概念包含 name, definition, examples, applications
- events: 事件列表，每个事件包含 name, date, location, description, participants
- key_points: 关键观点列表
- relationships: 关系网络
        """
        
        try:
            response = self.agent.run(prompt)
            # 提取JSON部分
            import re
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group(1))
            else:
                # 尝试直接解析响应
                analysis_data = json.loads(response)
            
            return {
                "status": "success",
                "data": analysis_data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"分析内容失败: {str(e)}"
            }
    
    def _create_summary_page(self, analysis_result, source_id):
        """创建摘要页面
        
        Args:
            analysis_result: 分析结果
            source_id: 源文件ID
            
        Returns:
            页面路径
        """
        data = analysis_result["data"]
        summary = data.get("summary", "")
        key_points = data.get("key_points", [])
        
        content = f"""## 概述
{summary}

## 主要内容
{"\n".join([f"- {point}" for point in key_points])}

## 关键观点
{"\n".join([f"- {point}" for point in key_points])}

## 参考资料
- 源文件: {source_id}
- 提取日期: {datetime.now().isoformat()}
"""
        
        try:
            page_path = self.architecture.create_wiki_page(
                "summaries",
                f"summary_{source_id[:10]}",
                content,
                [source_id]
            )
            return page_path
        except Exception as e:
            print(f"创建摘要页面失败: {str(e)}")
            return None
    
    def _create_entity_pages(self, analysis_result, source_id):
        """创建实体页面
        
        Args:
            analysis_result: 分析结果
            source_id: 源文件ID
            
        Returns:
            页面路径列表
        """
        pages = []
        data = analysis_result["data"]
        entities = data.get("entities", [])
        
        for entity in entities:
            entity_type = entity.get("type", "Person")
            entity_name = entity.get("name", "")
            if not entity_name:
                continue
            
            properties = entity.get("properties", {})
            relationships = entity.get("relationships", [])
            
            # 构建页面内容
            content = f"""## 概述
{properties.get('description', entity_name)}

## 详细信息
"""
            
            for key, value in properties.items():
                if key != 'description':
                    content += f"- **{key}**: {value}\n"
            
            content += "\n## 关系网络\n"
            for rel in relationships:
                content += f"- **{rel.get('type', '')}**: {rel.get('target', '')}\n"
            
            content += f"\n## 参考资料\n- 源文件: {source_id}\n- 提取日期: {datetime.now().isoformat()}\n"
            
            try:
                page_path = self.architecture.create_wiki_page(
                    "entities",
                    entity_name.replace(" ", "_"),
                    content,
                    [source_id]
                )
                pages.append(page_path)
            except Exception as e:
                print(f"创建实体页面失败 ({entity_name}): {str(e)}")
        
        return pages
    
    def _create_concept_pages(self, analysis_result, source_id):
        """创建概念页面
        
        Args:
            analysis_result: 分析结果
            source_id: 源文件ID
            
        Returns:
            页面路径列表
        """
        pages = []
        data = analysis_result["data"]
        concepts = data.get("concepts", [])
        
        for concept in concepts:
            concept_name = concept.get("name", "")
            if not concept_name:
                continue
            
            definition = concept.get("definition", "")
            examples = concept.get("examples", [])
            applications = concept.get("applications", [])
            related_concepts = concept.get("related_concepts", [])
            
            content = f"""## 概述
{concept_name}

## 定义
{definition}

## 应用
{"\n".join([f"- {app}" for app in applications])}

## 相关概念
{"\n".join([f"- {rel}" for rel in related_concepts])}

## 参考资料
- 源文件: {source_id}
- 提取日期: {datetime.now().isoformat()}
"""
            
            try:
                page_path = self.architecture.create_wiki_page(
                    "concepts",
                    concept_name.replace(" ", "_"),
                    content,
                    [source_id]
                )
                pages.append(page_path)
            except Exception as e:
                print(f"创建概念页面失败 ({concept_name}): {str(e)}")
        
        return pages
    
    def _create_event_pages(self, analysis_result, source_id):
        """创建事件页面
        
        Args:
            analysis_result: 分析结果
            source_id: 源文件ID
            
        Returns:
            页面路径列表
        """
        pages = []
        data = analysis_result["data"]
        events = data.get("events", [])
        
        for event in events:
            event_name = event.get("name", "")
            if not event_name:
                continue
            
            date = event.get("date", "")
            location = event.get("location", "")
            description = event.get("description", "")
            participants = event.get("participants", [])
            outcome = event.get("outcome", "")
            
            content = f"""## 概述
{event_name}

## 详细信息
- **日期**: {date}
- **地点**: {location}
- **描述**: {description}

## 参与方
{"\n".join([f"- {p}" for p in participants])}

## 影响
{outcome}

## 参考资料
- 源文件: {source_id}
- 提取日期: {datetime.now().isoformat()}
"""
            
            try:
                page_path = self.architecture.create_wiki_page(
                    "events",
                    event_name.replace(" ", "_"),
                    content,
                    [source_id]
                )
                pages.append(page_path)
            except Exception as e:
                print(f"创建事件页面失败 ({event_name}): {str(e)}")
        
        return pages
    
    def update_existing_pages(self, source_id, analysis_result):
        """更新现有页面
        
        Args:
            source_id: 源文件ID
            analysis_result: 分析结果
            
        Returns:
            更新结果
        """
        # 这里可以实现更新现有页面的逻辑
        # 例如，检查是否已有相关页面，然后更新内容
        pass

class IngestManager:
    """导入管理器"""
    
    def __init__(self):
        """初始化导入管理器"""
        self.intelligent_ingest = IntelligentIngest()
    
    def ingest(self, file_path, source_type="document"):
        """导入文件
        
        Args:
            file_path: 文件路径
            source_type: 源文件类型
            
        Returns:
            导入结果
        """
        return self.intelligent_ingest.ingest_source(file_path, source_type)
    
    def batch_ingest(self, file_paths, source_type="document"):
        """批量导入文件
        
        Args:
            file_paths: 文件路径列表
            source_type: 源文件类型
            
        Returns:
            批量导入结果
        """
        results = []
        for file_path in file_paths:
            result = self.ingest(file_path, source_type)
            results.append(result)
        
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count
        
        return {
            "status": "completed",
            "total": len(results),
            "success": success_count,
            "error": error_count,
            "results": results
        }
