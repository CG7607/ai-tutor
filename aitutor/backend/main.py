"""FastAPI entry point for AITutor."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aitutor.backend.api.chat import ChatRequest, ChatResponse, handle_chat
from aitutor.backend.api.kg import (
    KGSearchRequest,
    KGSearchResponse,
    KGNodeRequest,
    KGNeighborhoodResponse,
    KGFullGraphResponse,
    search_kg,
    get_neighborhood,
    get_full_graph,
)

app = FastAPI(
    title="AITutor API",
    description="基于多智能体协作的《人工智能导论》课程助教",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "aitutor"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """多智能体协作问答接口。

    学生提问后，Router 自动分类并调度合适的专家 Agent 回答。
    """
    return await handle_chat(request)


@app.post("/api/kg/search", response_model=KGSearchResponse)
async def kg_search(request: KGSearchRequest):
    """搜索知识图谱中的概念。"""
    return await search_kg(request)


@app.post("/api/kg/neighborhood", response_model=KGNeighborhoodResponse)
async def kg_neighborhood(request: KGNodeRequest):
    """查询节点的 1-hop 邻居。"""
    return await get_neighborhood(request)


@app.get("/api/kg/full", response_model=KGFullGraphResponse)
async def kg_full():
    """获取完整知识图谱数据（用于可视化）。"""
    return await get_full_graph()
