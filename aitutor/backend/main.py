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
    KGDetailRequest,
    KGDetailResponse,
    get_concept_detail,
)
from aitutor.backend.api.quiz import (
    QuizRequest,
    QuizSubmitRequest,
    QuizResponse,
    QuizSubmitResponse,
    generate_quiz_endpoint,
    submit_quiz_endpoint,
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


@app.post("/api/quiz/generate", response_model=QuizResponse)
async def quiz_generate(request: QuizRequest):
    """生成自适应测验题目。"""
    return await generate_quiz_endpoint(request)


@app.post("/api/kg/detail", response_model=KGDetailResponse)
async def kg_detail(request: KGDetailRequest):
    """获取概念的深度解读——LLM 生成核心思想/数学基础/历史/误区/应用."""
    return await get_concept_detail(request)


@app.post("/api/quiz/submit", response_model=QuizSubmitResponse)
async def quiz_submit(request: QuizSubmitRequest):
    """提交测验答案。"""
    return await submit_quiz_endpoint(request)
