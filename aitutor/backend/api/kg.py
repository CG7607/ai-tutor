"""Knowledge graph API endpoints."""
from pydantic import BaseModel

from aitutor.backend.knowledge_graph.query import kg_query


class KGSearchRequest(BaseModel):
    query: str


class KGNodeRequest(BaseModel):
    node_id: str


class KGSearchResponse(BaseModel):
    results: list[dict]


class KGNeighborhoodResponse(BaseModel):
    center: dict | None
    neighbors: list[dict]


class KGFullGraphResponse(BaseModel):
    nodes: list[dict]
    edges: list[dict]


async def search_kg(request: KGSearchRequest) -> KGSearchResponse:
    """Search for concepts in the knowledge graph."""
    results = kg_query.search_concepts(request.query)
    return KGSearchResponse(results=results)


async def get_neighborhood(request: KGNodeRequest) -> KGNeighborhoodResponse:
    """Get 1-hop neighborhood for a specific node."""
    neighborhood = kg_query.get_one_hop_neighbors(request.node_id)
    return KGNeighborhoodResponse(
        center=neighborhood["center"],
        neighbors=neighborhood["neighbors"],
    )


async def get_full_graph() -> KGFullGraphResponse:
    """Get the full knowledge graph for visualization."""
    data = kg_query.get_full_graph_data()
    return KGFullGraphResponse(nodes=data["nodes"], edges=data["edges"])


# ============ 概念深度解读 ============

class KGDetailRequest(BaseModel):
    concept_name: str
    concept_type: str = "Concept"
    concept_desc: str = ""
    neighbor_names: list[str] = []


class KGDetailResponse(BaseModel):
    concept_name: str
    core_idea: str        # 核心思想
    math_foundation: str   # 数学基础
    history: str           # 历史背景与关键人物
    key_insights: list[str]  # 关键洞察（3-5条）
    common_mistakes: list[str]  # 常见误区（2-3条）
    applications: str      # 应用场景
    further_reading: str   # 延伸学习建议


概念解读提示词 = """你是《人工智能导论》课程的资深讲师。请为以下概念撰写一份精炼但深入的知识卡片。

## 概念信息
- 名称：{name}
- 类型：{type}
- 简介：{desc}
- 相关概念：{neighbors}

## 撰写要求
1. 每部分 2-4 句，精炼但信息密度高
2. 面向初学者，但不过度简化核心原理
3. 数学公式用 LaTeX（$...$ 或 $$...$$）
4. 提到的人物标注全名和年份

## 输出格式（JSON）
{{
  "core_idea": "核心思想——这个概念到底在解决什么问题，最本质的思路是什么",
  "math_foundation": "数学基础——核心公式或数学框架（用LaTeX），以及直觉解释",
  "history": "历史背景——谁在哪年提出，当时要解决什么问题，后来如何演变",
  "key_insights": ["洞察1", "洞察2", "洞察3"],
  "common_mistakes": ["常见误区1", "常见误区2"],
  "applications": "应用场景——在哪些实际问题中发挥作用，举1-2个具体例子",
  "further_reading": "延伸学习——建议接下来学什么相关概念，以及推荐阅读方向"
}}
"""


async def get_concept_detail(request: KGDetailRequest) -> KGDetailResponse:
    """用 LLM 生成概念的深度解读."""
    from aitutor.backend.llm.client import structured_output

    prompt = 概念解读提示词.format(
        name=request.concept_name,
        type=request.concept_type,
        desc=request.concept_desc,
        neighbors=", ".join(request.neighbor_names) if request.neighbor_names else "无",
    )

    try:
        data = await structured_output(
            messages=[{"role": "user", "content": f"请解读：{request.concept_name}"}],
            system_prompt=prompt,
            output_schema={
                "core_idea": "核心思想",
                "math_foundation": "数学基础",
                "history": "历史背景",
                "key_insights": ["洞察1", "洞察2"],
                "common_mistakes": ["误区1"],
                "applications": "应用场景",
                "further_reading": "延伸学习",
            },
            temperature=0.4,
        )
        return KGDetailResponse(
            concept_name=request.concept_name,
            core_idea=data.get("core_idea", ""),
            math_foundation=data.get("math_foundation", ""),
            history=data.get("history", ""),
            key_insights=data.get("key_insights", []),
            common_mistakes=data.get("common_mistakes", []),
            applications=data.get("applications", ""),
            further_reading=data.get("further_reading", ""),
        )
    except Exception as e:
        # LLM 不可用时返回基于图谱数据的降级版本
        return KGDetailResponse(
            concept_name=request.concept_name,
            core_idea=request.concept_desc,
            math_foundation="（需要连接 LLM 获取详细数学推导）",
            history="（需要连接 LLM 获取历史背景）",
            key_insights=[f"属于 {request.concept_type} 类型的概念"],
            common_mistakes=[],
            applications="（需要连接 LLM 获取应用场景）",
            further_reading=f"相关概念：{', '.join(request.neighbor_names[:5])}" if request.neighbor_names else "",
        )
