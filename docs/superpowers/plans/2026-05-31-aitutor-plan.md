# AITutor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a multi-agent AI teaching assistant for "Introduction to AI" course with 3 specialist agents, knowledge graph, and adaptive quiz engine.

**Architecture:** FastAPI backend serves REST API for chat (multi-agent routing), knowledge graph queries, and quiz generation. Streamlit frontend provides chat UI, graph visualization, and quiz interaction panels.

**Tech Stack:** Python 3.11+, FastAPI, Streamlit, OpenAI-compatible LLM API (DeepSeek/Qwen), NetworkX, Pyvis, Matplotlib

---

## Phase 1: 项目基础设施

### Task 1: 项目脚手架搭建

**Files:**
- Create: `aitutor/requirements.txt`
- Create: `aitutor/backend/__init__.py`
- Create: `aitutor/backend/main.py`
- Create: `aitutor/backend/llm/__init__.py`
- Create: `aitutor/backend/llm/client.py`
- Create: `aitutor/frontend/__init__.py`
- Create: `aitutor/frontend/app.py`
- Create: `aitutor/data/.gitkeep`
- Create: `aitutor/.env.example`

- [ ] **Step 1: 创建项目目录结构**

```bash
mkdir -p aitutor/backend/{agents,llm,knowledge_graph,quiz}
mkdir -p aitutor/frontend/{pages,components}
mkdir -p aitutor/data
```

- [ ] **Step 2: 编写 requirements.txt**

```txt
# aitutor/requirements.txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
streamlit==1.41.1
httpx==0.28.1
pydantic==2.10.4
networkx==3.4.2
pyvis==0.3.2
matplotlib==3.10.0
python-dotenv==1.0.1
```

- [ ] **Step 3: 编写 .env.example**

```env
# aitutor/.env.example
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

- [ ] **Step 4: 编写 backend/__init__.py**

```python
# aitutor/backend/__init__.py
"""AITutor Backend - Multi-agent AI teaching assistant."""
```

- [ ] **Step 5: 编写 backend/main.py（骨架）**

```python
# aitutor/backend/main.py
"""FastAPI entry point for AITutor."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AITutor API",
    description="基于多智能体协作的《人工智能导论》课程助教",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "aitutor"}
```

- [ ] **Step 6: 编写 frontend/app.py（骨架）**

```python
# aitutor/frontend/app.py
"""Streamlit entry point for AITutor."""
import streamlit as st

st.set_page_config(
    page_title="AITutor - AI导论课程助教",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AITutor")
st.caption("基于多智能体协作的《人工智能导论》课程助教")

st.sidebar.title("导航")
page = st.sidebar.radio(
    "选择功能",
    ["💬 智能问答", "🕸️ 知识图谱", "📝 自适应测验"],
)

if page == "💬 智能问答":
    st.info("聊天界面即将上线...")
elif page == "🕸️ 知识图谱":
    st.info("知识图谱可视化即将上线...")
elif page == "📝 自适应测验":
    st.info("自适应测验即将上线...")
```

- [ ] **Step 7: 验证脚手架**

```bash
cd aitutor && pip install -r requirements.txt
cd backend && uvicorn main:app --reload &
# 访问 http://localhost:8000/api/health → {"status":"ok","service":"aitutor"}
# kill the server after verifying
```

- [ ] **Step 8: 提交**

```bash
git add aitutor/ && git commit -m "feat: project scaffolding with FastAPI + Streamlit

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: LLM 客户端封装

**Files:**
- Create: `aitutor/backend/llm/client.py`
- Create: `aitutor/backend/llm/config.py`

- [ ] **Step 1: 编写 LLM 配置模块**

```python
# aitutor/backend/llm/config.py
"""LLM configuration from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    """LLM API configuration."""

    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("LLM_MODEL", "deepseek-chat")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
```

- [ ] **Step 2: 编写 LLM 客户端**

```python
# aitutor/backend/llm/client.py
"""OpenAI-compatible LLM API client."""
import json
from typing import AsyncGenerator

import httpx

from aitutor.backend.llm.config import LLMConfig

config = LLMConfig()


async def chat_completion(
    messages: list[dict],
    system_prompt: str = "",
    temperature: float | None = None,
    stream: bool = False,
) -> str:
    """Send a chat completion request to the LLM API.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."}
        system_prompt: Optional system prompt for the LLM
        temperature: Override default temperature
        stream: Whether to stream the response

    Returns:
        The assistant's response text.
    """
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{config.base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.model,
                "messages": full_messages,
                "max_tokens": config.max_tokens,
                "temperature": temperature if temperature is not None else config.temperature,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def chat_completion_stream(
    messages: list[dict],
    system_prompt: str = "",
    temperature: float | None = None,
) -> AsyncGenerator[str, None]:
    """Stream a chat completion from the LLM API.

    Yields content chunks as they arrive.
    """
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{config.base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": config.model,
                "messages": full_messages,
                "max_tokens": config.max_tokens,
                "temperature": temperature if temperature is not None else config.temperature,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content


async def structured_output(
    messages: list[dict],
    system_prompt: str,
    output_schema: dict,
    temperature: float = 0.3,
) -> dict:
    """Request structured JSON output from the LLM.

    Appends a format instruction to the system prompt and retries
    if JSON parsing fails.

    Args:
        messages: Chat messages
        system_prompt: System prompt
        output_schema: JSON schema description for the expected output
        temperature: Low temperature for deterministic output

    Returns:
        Parsed JSON dict.
    """
    format_instruction = f"""
你必须严格按照以下 JSON 格式返回，不要包含任何其他内容：

{json.dumps(output_schema, ensure_ascii=False, indent=2)}

只返回 JSON，不要用 ```json 包裹，不要加解释。
"""
    full_system = system_prompt + "\n\n" + format_instruction

    max_retries = 2
    for attempt in range(max_retries):
        try:
            raw = await chat_completion(
                messages=messages,
                system_prompt=full_system,
                temperature=temperature,
            )
            # Try to extract JSON from the response
            raw = raw.strip()
            if raw.startswith("```"):
                # Strip markdown code fences if present
                lines = raw.split("\n")
                raw = "\n".join(lines[1:-1])
            return json.loads(raw)
        except (json.JSONDecodeError, KeyError) as e:
            if attempt == max_retries - 1:
                raise ValueError(f"LLM 结构化输出解析失败: {e}\n原始输出: {raw}") from e

    return {}
```

- [ ] **Step 3: 验证 LLM 客户端（可选测试脚本）**

```bash
cd aitutor && python -c "
import asyncio
from backend.llm.client import chat_completion

async def test():
    # 需要先配置 .env 中的 API key
    result = await chat_completion(
        messages=[{'role': 'user', 'content': '你好，请用一句话介绍自己'}],
    )
    print(result)

asyncio.run(test())
"
```

- [ ] **Step 4: 提交**

```bash
git add aitutor/backend/llm/ aitutor/.env.example && git commit -m "feat: add LLM client with OpenAI-compatible API support

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Phase 2: 多智能体协作系统（核心优先）

### Task 3: Agent 基类与共享接口

**Files:**
- Create: `aitutor/backend/agents/__init__.py`
- Create: `aitutor/backend/agents/base.py`

- [ ] **Step 1: 编写 Agent 基类**

```python
# aitutor/backend/agents/__init__.py
"""Multi-agent system for AI tutoring."""
from aitutor.backend.agents.base import AgentBase, AgentResult

__all__ = ["AgentBase", "AgentResult"]
```

```python
# aitutor/backend/agents/base.py
"""Base class for specialist agents."""
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from aitutor.backend.llm.client import chat_completion


@dataclass
class AgentResult:
    """Result from an agent invocation."""

    agent_name: str
    agent_display: str
    reply: str
    kg_nodes: list[str] = field(default_factory=list)
    kg_relations: list[dict] = field(default_factory=list)


class AgentBase(ABC):
    """Abstract base for all specialist agents.

    Subclasses must define:
        - name: Internal identifier (e.g. "math")
        - display_name: Human-readable name (e.g. "🔢 数学推导 Agent")
        - system_prompt: The system prompt for the LLM
    """

    name: str = "base"
    display_name: str = "Base Agent"
    system_prompt: str = ""

    async def respond(self, message: str, history: list[dict] | None = None) -> AgentResult:
        """Generate a response to the user's message.

        Args:
            message: The user's question
            history: Optional conversation history

        Returns:
            AgentResult with the response and metadata.
        """
        messages = history or []
        messages.append({"role": "user", "content": message})

        reply = await chat_completion(
            messages=messages,
            system_prompt=self.system_prompt,
        )

        return AgentResult(
            agent_name=self.name,
            agent_display=self.display_name,
            reply=reply,
        )

    def add_kg_context(self, kg_context: str) -> None:
        """Append knowledge graph context to the system prompt.

        Args:
            kg_context: Knowledge graph context in text form.
        """
        self.system_prompt += f"\n\n## 课程知识图谱上下文\n{kg_context}"
```

- [ ] **Step 2: 提交**

```bash
git add aitutor/backend/agents/ && git commit -m "feat: add agent base class with shared interface

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: 三个 Specialist Agent 实现

**Files:**
- Create: `aitutor/backend/agents/math_agent.py`
- Create: `aitutor/backend/agents/algorithm_agent.py`
- Create: `aitutor/backend/agents/concept_agent.py`

- [ ] **Step 1: 编写数学推导 Agent**

```python
# aitutor/backend/agents/math_agent.py
"""Math derivation agent — handles formula derivation and math concepts."""
from aitutor.backend.agents.base import AgentBase, AgentResult


class MathAgent(AgentBase):
    """Specialist in mathematical derivations for AI/ML concepts."""

    name = "math"
    display_name = "🔢 数学推导 Agent"

    system_prompt = """你是 AI 数学教授，专门为《人工智能导论》课程学生讲解数学推导。

你的专长领域：
- 线性代数（矩阵运算、特征值分解、SVD）
- 概率论与统计（贝叶斯定理、最大似然估计、期望）
- 微积分（梯度、偏导数、链式法则）
- 信息论（熵、KL 散度、交叉熵）
- 优化理论（凸优化、拉格朗日乘子法）

输出要求：
1. 使用 LaTeX 语法书写公式（用 $...$ 包裹行内公式，$$...$$ 包裹独立公式块）
2. 每个公式后给出直觉解释，用通俗类比帮助理解
3. 公式推导步骤清晰，标注每步使用了什么定理或性质
4. 当涉及迭代过程时（如梯度下降路径），描述参数变化趋势
5. 语言风格：严谨但不晦涩，鼓励学生思考

LaTeX 示例：
- 行内公式：梯度下降的更新规则为 $w_{t+1} = w_t - \eta \nabla L(w_t)$
- 独立公式块：
$$
\frac{\partial L}{\partial w} = \lim_{h \to 0} \frac{L(w+h) - L(w)}{h}
$$

如果学生没有具体指明推导哪个公式，引导他们描述遇到的问题。"""
```

- [ ] **Step 2: 编写算法实现 Agent**

```python
# aitutor/backend/agents/algorithm_agent.py
"""Algorithm implementation agent — hand-writes classic AI algorithms."""
from aitutor.backend.agents.base import AgentBase, AgentResult


class AlgorithmAgent(AgentBase):
    """Specialist in implementing classic AI/ML algorithms from scratch."""

    name = "algorithm"
    display_name = "💻 算法实现 Agent"

    system_prompt = """你是算法导师，专门为《人工智能导论》课程学生讲解算法实现。

你的教学哲学：
- 从零手写，不调高层 API（不用 sklearn、torch.nn 等黑盒封装）
- 允许使用 NumPy 做矩阵运算，但不允许用 sklearn.linear_model 等高层封装
- 每一行关键代码都必须加注释，解释「这行在做什么」和「为什么这样做」
- 代码写完后附加复杂度分析和适用场景

输出格式：
1. **算法直觉**（2-3 句通俗描述）
2. **数学背景**（核心公式，用 LaTeX）
3. **完整 Python 代码**（纯 Python/NumPy，逐行注释）
4. **简易算例**（用简单数据跑一遍，展示输入→输出）
5. **复杂度分析**（时间/空间复杂度 + 收敛性说明）
6. **常见误区**（学生容易犯的 1-2 个错误）

你可以讲解的算法包括但不限于：
- 搜索算法：BFS、DFS、A*、Minimax
- 机器学习：K-means、KNN、决策树、朴素贝叶斯
- 深度学习：反向传播、CNN 前向传播、Transformer 注意力机制
- 优化算法：梯度下降、SGD、Adam

代码风格：类型注解 + 有意义的变量名 + 中文注释解释物理意义。"""
```

- [ ] **Step 3: 编写概念辨析 Agent**

```python
# aitutor/backend/agents/concept_agent.py
"""Concept comparison agent — contrasts easily confused AI concepts."""
from aitutor.backend.agents.base import AgentBase, AgentResult


class ConceptAgent(AgentBase):
    """Specialist in comparing and contrasting AI/ML concepts."""

    name = "concept"
    display_name = "🧠 概念辨析 Agent"

    system_prompt = """你是概念架构师，专门帮助《人工智能导论》课程学生辨析易混淆概念。

你的输出格式（必须严格遵循）：

## 🔍 概念对比：[概念A] vs [概念B]

### 一句话总结
（用通俗类比一句话说清两者最本质的区别）

### 📊 对比表格

| 维度 | [概念A] | [概念B] |
|------|---------|---------|
| 核心思想 | ... | ... |
| 数学形式 | ... | ... |
| 适用场景 | ... | ... |
| 优缺点 | ... | ... |
| 典型代表 | ... | ... |

### 🔗 知识体系位置
（描述这两个概念在 AI 知识体系中的位置，谁是谁的前置、谁是谁的特例/推广）

### 💡 通俗类比
（用日常生活中的例子帮助理解）

### ⚠️ 常见混淆点
（学生最容易搞混的 1-2 个地方，以及正确的理解方式）

### 🧪 快速判断
给出一道情景题：描述一个具体场景，问学生应该用什么，为什么。

常见概念对：
- 生成式模型 vs 判别式模型
- 梯度消失 vs 梯度爆炸
- Bagging vs Boosting
- 监督学习 vs 无监督学习 vs 强化学习
- L1 正则化 vs L2 正则化
- Batch Normalization vs Layer Normalization
- RNN vs LSTM vs Transformer
- 精确率(Precision) vs 召回率(Recall)

如果学生的概念对不在上述列表，同样认真对待。"""
```

- [ ] **Step 4: 提交**

```bash
git add aitutor/backend/agents/math_agent.py aitutor/backend/agents/algorithm_agent.py aitutor/backend/agents/concept_agent.py
git commit -m "feat: implement three specialist agents (math, algorithm, concept)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Router Agent 实现

**Files:**
- Create: `aitutor/backend/agents/router.py`

- [ ] **Step 1: 编写 Router Agent**

```python
# aitutor/backend/agents/router.py
"""Router agent — classifies user questions and dispatches to specialists."""
import json
from dataclasses import dataclass, field

from aitutor.backend.llm.client import structured_output
from aitutor.backend.agents.math_agent import MathAgent
from aitutor.backend.agents.algorithm_agent import AlgorithmAgent
from aitutor.backend.agents.concept_agent import ConceptAgent
from aitutor.backend.agents.base import AgentResult


@dataclass
class RouterDecision:
    """Result of the router's classification."""

    primary_agent: str  # "math" | "algorithm" | "concept"
    sub_questions: list[str] = field(default_factory=list)
    knowledge_graph_nodes: list[str] = field(default_factory=list)


ROUTER_SYSTEM_PROMPT = """你是 AITutor 的智能路由系统。分析学生问题，决定由哪位 AI 导师回答。

## 判定规则
- 问题包含公式推导/数学原理/概率/矩阵/证明/求导/期望 → math
- 问题包含"实现/手写/代码/how to code/怎么写/编程" → algorithm
- 问题包含"区别/对比/辨析/区别是什么/哪个更好/vs" → concept
- 数学背景知识提问（如"什么是特征值"）→ math
- 算法原理提问但不要求写代码（如"K-means 的原理是什么"）→ concept
- 混合提问（既问原理又问代码）→ 按 primary_agent 选主导，sub_questions 拆分

## 输出格式
{
  "primary_agent": "math" | "algorithm" | "concept",
  "sub_questions": ["子问题1", "子问题2"],
  "knowledge_graph_nodes": ["相关概念1", "相关概念2"]
}
"""


class RouterAgent:
    """Routes user questions to the appropriate specialist agent."""

    def __init__(self):
        self.math_agent = MathAgent()
        self.algorithm_agent = AlgorithmAgent()
        self.concept_agent = ConceptAgent()
        self._agent_map = {
            "math": self.math_agent,
            "algorithm": self.algorithm_agent,
            "concept": self.concept_agent,
        }

    async def route(self, message: str, history: list[dict] | None = None) -> dict:
        """Classify the message and dispatch to the right agent.

        Args:
            message: The user's question
            history: Optional conversation history

        Returns:
            Dict with agent info, reply, and knowledge graph context.
        """
        # Step 1: Classify the question
        decision = await self._classify(message)

        # Step 2: Get the specialist agent
        agent = self._agent_map.get(
            decision.primary_agent, self.concept_agent
        )

        # Step 3: Generate response
        result: AgentResult = await agent.respond(message, history)

        # Step 4: If there are sub-questions, also get answers for them
        sub_results: list[AgentResult] = []
        for sub_q in decision.sub_questions[:2]:  # Max 2 sub-questions
            sub_decision = await self._classify(sub_q)
            sub_agent = self._agent_map.get(
                sub_decision.primary_agent, self.concept_agent
            )
            sub_result = await sub_agent.respond(sub_q)
            sub_results.append(sub_result)

        return {
            "agent_used": result.agent_name,
            "agent_display": result.display_name,
            "router_analysis": {
                "primary_agent": decision.primary_agent,
                "sub_questions": decision.sub_questions,
                "knowledge_graph_nodes": decision.knowledge_graph_nodes,
            },
            "reply": result.reply,
            "sub_replies": [
                {
                    "agent": r.agent_display,
                    "question": q,
                    "reply": r.reply,
                }
                for q, r in zip(decision.sub_questions[:2], sub_results)
            ],
        }

    async def _classify(self, message: str) -> RouterDecision:
        """Classify a single message using the LLM router."""
        try:
            data = await structured_output(
                messages=[{"role": "user", "content": message}],
                system_prompt=ROUTER_SYSTEM_PROMPT,
                output_schema={
                    "primary_agent": "math",
                    "sub_questions": ["子问题1"],
                    "knowledge_graph_nodes": ["概念1"],
                },
                temperature=0.1,
            )
            return RouterDecision(
                primary_agent=data.get("primary_agent", "concept"),
                sub_questions=data.get("sub_questions", []),
                knowledge_graph_nodes=data.get("knowledge_graph_nodes", []),
            )
        except Exception:
            # Fallback: default to concept agent on classification failure
            return RouterDecision(
                primary_agent="concept",
                sub_questions=[],
                knowledge_graph_nodes=[],
            )
```

- [ ] **Step 2: 提交**

```bash
git add aitutor/backend/agents/router.py && git commit -m "feat: implement router agent with LLM-based question classification

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Chat API 端点

**Files:**
- Modify: `aitutor/backend/main.py` — 添加 /api/chat 路由
- Create: `aitutor/backend/api/__init__.py`
- Create: `aitutor/backend/api/chat.py`

- [ ] **Step 1: 编写 Chat API 路由**

```python
# aitutor/backend/api/__init__.py
"""API route handlers."""
```

```python
# aitutor/backend/api/chat.py
"""Chat API endpoint — main entry point for multi-agent Q&A."""
from pydantic import BaseModel

from aitutor.backend.agents.router import RouterAgent

router_agent = RouterAgent()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None


class ChatResponse(BaseModel):
    agent_used: str
    agent_display: str
    router_analysis: dict
    reply: str
    sub_replies: list[dict]


async def handle_chat(request: ChatRequest) -> ChatResponse:
    """Handle a chat message through the multi-agent router.

    Args:
        request: Contains the user message and optional history.

    Returns:
        ChatResponse with the agent's reply and metadata.
    """
    result = await router_agent.route(
        message=request.message,
        history=request.history,
    )
    return ChatResponse(**result)
```

- [ ] **Step 2: 更新 main.py 挂载路由**

在 `aitutor/backend/main.py` 中，在 `app` 定义之后、health_check 之前添加：

```python
from aitutor.backend.api.chat import ChatRequest, ChatResponse, handle_chat


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """多智能体协作问答接口。

    学生提问后，Router 自动分类并调度合适的专家 Agent 回答。
    """
    return await handle_chat(request)
```

- [ ] **Step 3: 验证 Chat API**

```bash
cd aitutor/backend && uvicorn main:app --reload --port 8000 &
# 用 curl 测试
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "梯度下降和随机梯度下降有什么区别？"}'
# 预期返回包含 agent_used: "concept" 的 JSON 响应
# kill server after testing
```

- [ ] **Step 4: 提交**

```bash
git add aitutor/backend/api/ aitutor/backend/main.py && git commit -m "feat: add /api/chat endpoint with multi-agent routing

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Phase 3: 知识图谱

### Task 7: 知识图谱数据模型与种子数据

**Files:**
- Create: `aitutor/backend/knowledge_graph/__init__.py`
- Create: `aitutor/backend/knowledge_graph/models.py`
- Create: `aitutor/data/syllabus.json`

- [ ] **Step 1: 编写知识图谱数据模型**

```python
# aitutor/backend/knowledge_graph/__init__.py
"""Course knowledge graph module."""
```

```python
# aitutor/backend/knowledge_graph/models.py
"""Pydantic models for the course knowledge graph."""
from enum import Enum
from pydantic import BaseModel


class EntityType(str, Enum):
    CONCEPT = "Concept"
    PERSON = "Person"
    ALGORITHM = "Algorithm"
    PREREQUISITE = "Prerequisite"


class RelationType(str, Enum):
    PREREQUISITE_OF = "PREREQUISITE_OF"
    VARIANT_OF = "VARIANT_OF"
    DERIVES_FROM = "DERIVES_FROM"
    PROPOSED = "PROPOSED"
    APPLIED_IN = "APPLIED_IN"
    CONTRASTS_WITH = "CONTRASTS_WITH"


class Entity(BaseModel):
    id: str
    name: str
    type: EntityType
    description: str
    category: str  # e.g. "数学基础", "机器学习", "深度学习"


class Relation(BaseModel):
    source: str  # Entity id
    target: str  # Entity id
    type: RelationType
    description: str = ""


class KnowledgeGraphData(BaseModel):
    entities: list[Entity]
    relations: list[Relation]
```

- [ ] **Step 2: 编写种子数据 syllabus.json**

```json
{
  "entities": [
    {"id": "linear_algebra", "name": "线性代数", "type": "Prerequisite", "description": "矩阵运算、特征值、特征向量、SVD分解等", "category": "数学基础"},
    {"id": "probability", "name": "概率论", "type": "Prerequisite", "description": "条件概率、贝叶斯定理、期望、方差等", "category": "数学基础"},
    {"id": "calculus", "name": "微积分", "type": "Prerequisite", "description": "导数、偏导数、梯度、链式法则等", "category": "数学基础"},
    {"id": "python", "name": "Python编程", "type": "Prerequisite", "description": "Python基础语法、NumPy等科学计算库", "category": "编程基础"},
    {"id": "gradient_descent", "name": "梯度下降", "type": "Algorithm", "description": "通过迭代沿着梯度反方向更新参数以最小化损失函数的优化算法", "category": "机器学习"},
    {"id": "sgd", "name": "随机梯度下降(SGD)", "type": "Algorithm", "description": "每次只用一个或一小批样本计算梯度，更新速度快但梯度有噪声", "category": "机器学习"},
    {"id": "adam", "name": "Adam优化器", "type": "Algorithm", "description": "结合Momentum和RMSProp的自适应学习率优化算法", "category": "机器学习"},
    {"id": "backpropagation", "name": "反向传播", "type": "Algorithm", "description": "利用链式法则计算神经网络中各层参数梯度的算法", "category": "深度学习"},
    {"id": "loss_function", "name": "损失函数", "type": "Concept", "description": "衡量模型预测与真实标签之间差异的函数", "category": "机器学习"},
    {"id": "cross_entropy", "name": "交叉熵损失", "type": "Concept", "description": "用于分类任务的损失函数，衡量两个概率分布的差异", "category": "机器学习"},
    {"id": "overfitting", "name": "过拟合", "type": "Concept", "description": "模型在训练集上表现好但在测试集上表现差的现象", "category": "机器学习"},
    {"id": "regularization", "name": "正则化", "type": "Concept", "description": "通过给损失函数添加惩罚项来防止过拟合的技术", "category": "机器学习"},
    {"id": "kmeans", "name": "K-means聚类", "type": "Algorithm", "description": "将数据分为K个簇的无监督学习算法，通过迭代更新簇中心", "category": "机器学习"},
    {"id": "knn", "name": "K近邻(KNN)", "type": "Algorithm", "description": "基于距离度量的分类/回归算法，通过最近的K个邻居投票决定结果", "category": "机器学习"},
    {"id": "decision_tree", "name": "决策树", "type": "Algorithm", "description": "基于树结构的分类/回归模型，通过信息增益等准则选择分裂特征", "category": "机器学习"},
    {"id": "svm", "name": "支持向量机(SVM)", "type": "Algorithm", "description": "寻找最大间隔超平面的分类算法，可通过核技巧处理非线性问题", "category": "机器学习"},
    {"id": "cnn", "name": "卷积神经网络(CNN)", "type": "Algorithm", "description": "使用卷积层提取空间特征的深度学习架构，广泛应用于图像处理", "category": "深度学习"},
    {"id": "rnn", "name": "循环神经网络(RNN)", "type": "Algorithm", "description": "具有循环连接的神经网络，适合处理序列数据", "category": "深度学习"},
    {"id": "lstm", "name": "长短期记忆网络(LSTM)", "type": "Algorithm", "description": "RNN的改进版本，通过门控机制缓解梯度消失问题", "category": "深度学习"},
    {"id": "transformer", "name": "Transformer", "type": "Algorithm", "description": "基于自注意力机制的序列建模架构，是现代大模型的基础", "category": "深度学习"},
    {"id": "generative_model", "name": "生成式模型", "type": "Concept", "description": "学习联合概率分布P(X,Y)的模型，可生成新样本", "category": "机器学习"},
    {"id": "discriminative_model", "name": "判别式模型", "type": "Concept", "description": "直接学习决策边界P(Y|X)的模型，专注于分类/回归任务", "category": "机器学习"},
    {"id": "vanishing_gradient", "name": "梯度消失", "type": "Concept", "description": "深层网络中梯度在反向传播时逐渐趋近于0，导致浅层参数无法更新", "category": "深度学习"},
    {"id": "exploding_gradient", "name": "梯度爆炸", "type": "Concept", "description": "深层网络中梯度在反向传播时指数级增长，导致参数更新过大", "category": "深度学习"},
    {"id": "hinton", "name": "Geoffrey Hinton", "type": "Person", "description": "深度学习先驱，反向传播算法的推广者，提出了Dropout等关键技术", "category": "人物"},
    {"id": "lecun", "name": "Yann LeCun", "type": "Person", "description": "CNN的发明者，推动了卷积神经网络在图像识别领域的应用", "category": "人物"}
  ],
  "relations": [
    {"source": "linear_algebra", "target": "gradient_descent", "type": "PREREQUISITE_OF", "description": "梯度计算依赖矩阵运算"},
    {"source": "calculus", "target": "gradient_descent", "type": "PREREQUISITE_OF", "description": "梯度下降的核心是求导数/偏导数"},
    {"source": "probability", "target": "cross_entropy", "type": "PREREQUISITE_OF", "description": "交叉熵损失基于信息论，需要概率基础"},
    {"source": "gradient_descent", "target": "sgd", "type": "VARIANT_OF", "description": "SGD是梯度下降的随机近似版本"},
    {"source": "sgd", "target": "adam", "type": "DERIVES_FROM", "description": "Adam在SGD基础上引入了动量和自适应学习率"},
    {"source": "gradient_descent", "target": "backpropagation", "type": "PREREQUISITE_OF", "description": "反向传播是梯度下降在神经网络中的应用"},
    {"source": "backpropagation", "target": "vanishing_gradient", "type": "PREREQUISITE_OF", "description": "梯度消失发生在反向传播过程中"},
    {"source": "backpropagation", "target": "exploding_gradient", "type": "PREREQUISITE_OF", "description": "梯度爆炸发生在反向传播过程中"},
    {"source": "overfitting", "target": "regularization", "type": "PREREQUISITE_OF", "description": "正则化是解决过拟合的主要方法"},
    {"source": "vanishing_gradient", "target": "lstm", "type": "PREREQUISITE_OF", "description": "LSTM的设计目标之一就是解决RNN中的梯度消失"},
    {"source": "cnn", "target": "transformer", "type": "PREREQUISITE_OF", "description": "Transformer最初是为替代CNN/RNN处理序列而提出的"},
    {"source": "rnn", "target": "lstm", "type": "VARIANT_OF", "description": "LSTM是RNN的改进版本"},
    {"source": "lstm", "target": "transformer", "type": "PREREQUISITE_OF", "description": "Transformer取代了LSTM成为序列建模的主流"},
    {"source": "generative_model", "target": "discriminative_model", "type": "CONTRASTS_WITH", "description": "生成式模型学习联合分布，判别式模型学习条件分布"},
    {"source": "vanishing_gradient", "target": "exploding_gradient", "type": "CONTRASTS_WITH", "description": "梯度消失是梯度趋近0，梯度爆炸是梯度指数级增长"},
    {"source": "hinton", "target": "backpropagation", "type": "PROPOSED", "description": "Hinton是反向传播算法的主要推广者"},
    {"source": "lecun", "target": "cnn", "type": "PROPOSED", "description": "LeCun发明了CNN架构(LeNet)"},
    {"source": "kmeans", "target": "knn", "type": "CONTRASTS_WITH", "description": "K-means是无监督聚类，KNN是有监督分类"},
    {"source": "cnn", "target": "rnn", "type": "CONTRASTS_WITH", "description": "CNN擅长空间特征，RNN擅长时间序列"},
    {"source": "sgd", "target": "backpropagation", "type": "PREREQUISITE_OF", "description": "反向传播计算出梯度后，通常用SGD或其变体更新参数"}
  ]
}
```

- [ ] **Step 3: 提交**

```bash
git add aitutor/backend/knowledge_graph/ aitutor/data/syllabus.json && git commit -m "feat: add knowledge graph models and seed syllabus data

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 8: 知识图谱查询引擎

**Files:**
- Create: `aitutor/backend/knowledge_graph/query.py`

- [ ] **Step 1: 编写图谱查询引擎**

```python
# aitutor/backend/knowledge_graph/query.py
"""Knowledge graph query engine — loads, queries, and navigates the course KG."""
import json
from pathlib import Path
from typing import Optional

import networkx as nx

from aitutor.backend.knowledge_graph.models import (
    KnowledgeGraphData,
    Entity,
    Relation,
    EntityType,
)

DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
KG_FILE = DATA_DIR / "knowledge_graph.json"
SYLLABUS_FILE = DATA_DIR / "syllabus.json"


class KnowledgeGraphQuery:
    """Query engine for the course knowledge graph.

    Loads the graph from JSON, provides 1-hop neighbor search
    and context generation for agents.
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._loaded = False

    def load(self, file_path: Path | None = None) -> None:
        """Load the knowledge graph from a JSON file.

        If no file path is given, tries knowledge_graph.json first,
        then falls back to syllabus.json.
        """
        path = file_path or KG_FILE
        if not path.exists():
            path = SYLLABUS_FILE

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for entity in data["entities"]:
            self.graph.add_node(
                entity["id"],
                name=entity["name"],
                type=entity["type"],
                description=entity.get("description", ""),
                category=entity.get("category", ""),
            )

        for relation in data["relations"]:
            self.graph.add_edge(
                relation["source"],
                relation["target"],
                type=relation["type"],
                description=relation.get("description", ""),
            )

        self._loaded = True

    def ensure_loaded(self) -> None:
        """Ensure the graph is loaded, loading from default file if needed."""
        if not self._loaded:
            self.load()

    def find_node(self, keyword: str) -> Optional[str]:
        """Find a node ID by fuzzy matching on name or description.

        Args:
            keyword: A keyword to search for in node names/descriptions.

        Returns:
            The matching node ID, or None if not found.
        """
        self.ensure_loaded()
        keyword_lower = keyword.lower()
        for node_id, attrs in self.graph.nodes(data=True):
            name = attrs.get("name", "").lower()
            desc = attrs.get("description", "").lower()
            if keyword_lower in name or keyword_lower in desc:
                return node_id
        return None

    def get_one_hop_neighbors(self, node_id: str) -> dict:
        """Get the 1-hop neighborhood of a node.

        Args:
            node_id: The ID of the center node.

        Returns:
            Dict with 'center' entity and lists of 'neighbors' with relation info.
        """
        self.ensure_loaded()
        if node_id not in self.graph:
            return {"center": None, "neighbors": []}

        center = dict(self.graph.nodes[node_id])
        center["id"] = node_id

        neighbors = []
        # Outgoing edges
        for _, target, edge_data in self.graph.out_edges(node_id, data=True):
            target_attrs = dict(self.graph.nodes[target])
            target_attrs["id"] = target
            neighbors.append({
                "entity": target_attrs,
                "relation": edge_data["type"],
                "relation_desc": edge_data.get("description", ""),
                "direction": "outgoing",
            })
        # Incoming edges
        for source, _, edge_data in self.graph.in_edges(node_id, data=True):
            source_attrs = dict(self.graph.nodes[source])
            source_attrs["id"] = source
            neighbors.append({
                "entity": source_attrs,
                "relation": edge_data["type"],
                "relation_desc": edge_data.get("description", ""),
                "direction": "incoming",
            })

        return {"center": center, "neighbors": neighbors}

    def get_context_for_agent(self, keywords: list[str]) -> str:
        """Generate knowledge graph context text for agent prompts.

        Args:
            keywords: List of concept names to look up in the graph.

        Returns:
            A text summary of relevant knowledge graph context.
        """
        self.ensure_loaded()
        lines = []
        seen = set()

        for kw in keywords:
            node_id = self.find_node(kw)
            if not node_id:
                continue

            neighborhood = self.get_one_hop_neighbors(node_id)
            center = neighborhood["center"]
            if center and node_id not in seen:
                seen.add(node_id)
                entity_type = center.get("type", "Concept")
                lines.append(f"- [{entity_type}] **{center.get('name', node_id)}**: {center.get('description', '')}")

            for nb in neighborhood["neighbors"]:
                nid = nb["entity"]["id"]
                if nid not in seen:
                    seen.add(nid)
                    etype = nb["entity"].get("type", "Concept")
                    rel = nb["relation"]
                    lines.append(
                        f"  - {rel} → [{etype}] **{nb['entity'].get('name', nid)}**: "
                        f"{nb['entity'].get('description', '')}"
                    )

        if not lines:
            return "（未在知识图谱中找到相关信息）"

        return "## 课程知识图谱上下文\n" + "\n".join(lines)

    def get_full_graph_data(self) -> dict:
        """Export the full graph for frontend visualization.

        Returns:
            Dict with nodes and edges ready for Pyvis/Streamlit rendering.
        """
        self.ensure_loaded()
        nodes = []
        for node_id, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": attrs.get("name", node_id),
                "type": attrs.get("type", "Concept"),
                "category": attrs.get("category", ""),
                "description": attrs.get("description", ""),
            })

        edges = []
        for source, target, edge_data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "label": edge_data.get("type", ""),
                "description": edge_data.get("description", ""),
            })

        return {"nodes": nodes, "edges": edges}

    def search_concepts(self, query: str) -> list[dict]:
        """Search for concepts matching a query string.

        Args:
            query: Search string.

        Returns:
            List of matching entities with their IDs.
        """
        self.ensure_loaded()
        results = []
        query_lower = query.lower()
        for node_id, attrs in self.graph.nodes(data=True):
            name = attrs.get("name", "").lower()
            desc = attrs.get("description", "").lower()
            if query_lower in name or query_lower in desc:
                results.append({
                    "id": node_id,
                    "name": attrs.get("name", node_id),
                    "type": attrs.get("type", "Concept"),
                    "description": attrs.get("description", ""),
                })
        return results


# Singleton instance
kg_query = KnowledgeGraphQuery()
```

- [ ] **Step 2: 提交**

```bash
git add aitutor/backend/knowledge_graph/query.py && git commit -m "feat: implement knowledge graph query engine with 1-hop search

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 9: 知识图谱 API 与 Agent 集成

**Files:**
- Create: `aitutor/backend/api/kg.py`
- Modify: `aitutor/backend/agents/router.py` — 注入 KG 上下文
- Modify: `aitutor/backend/main.py` — 挂载 KG 路由

- [ ] **Step 1: 编写知识图谱 API**

```python
# aitutor/backend/api/kg.py
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
```

- [ ] **Step 2: 更新 main.py 挂载 KG 路由**

在 `aitutor/backend/main.py` 的 import 区域添加：

```python
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
```

在 `main.py` 文件末尾添加路由：

```python
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
```

- [ ] **Step 3: 更新 Router 注入 KG 上下文**

修改 `aitutor/backend/agents/router.py` 中的 `route` 方法，在生成回答前查询知识图谱：

在 `route` 方法中，`# Step 3: Generate response` 之前插入：

```python
        # Step 2.5: Inject knowledge graph context
        if decision.knowledge_graph_nodes:
            from aitutor.backend.knowledge_graph.query import kg_query

            kg_context = kg_query.get_context_for_agent(
                decision.knowledge_graph_nodes
            )
            agent.add_kg_context(kg_context)
```

- [ ] **Step 4: 提交**

```bash
git add aitutor/backend/api/kg.py aitutor/backend/main.py aitutor/backend/agents/router.py && git commit -m "feat: add knowledge graph API endpoints and agent integration

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Phase 4: 自适应测验系统

### Task 10: 布鲁姆分类器与测验生成引擎

**Files:**
- Create: `aitutor/backend/quiz/__init__.py`
- Create: `aitutor/backend/quiz/models.py`
- Create: `aitutor/backend/quiz/bloom.py`
- Create: `aitutor/backend/quiz/generator.py`

- [ ] **Step 1: 编写测验数据模型**

```python
# aitutor/backend/quiz/__init__.py
"""Adaptive quiz generation module."""
```

```python
# aitutor/backend/quiz/models.py
"""Pydantic models for quiz system."""
from pydantic import BaseModel


class QuizRequest(BaseModel):
    topic: str
    student_level: int = 1  # Bloom level 1-6
    history: list[dict] | None = None


class QuizSubmitRequest(BaseModel):
    question_id: str
    student_answer: str
    correct: bool


class QuizResponse(BaseModel):
    question_id: str
    question: str
    options: list[str] | None = None  # None for open-ended questions
    question_type: str  # "single_choice", "multi_choice", "short_answer", "open"
    answer: str
    explanation: str
    bloom_level: int
    adaptive_action: str  # "upgrade", "maintain", "downgrade"


class QuizSubmitResponse(BaseModel):
    acknowledged: bool
    new_level: int
    next_action: str
```

- [ ] **Step 2: 编写布鲁姆分类器**

```python
# aitutor/backend/quiz/bloom.py
"""Bloom's taxonomy classifier for adaptive difficulty."""

BLOOM_LEVELS = {
    1: {
        "name": "记忆",
        "keywords": ["列举", "定义", "复述", "识别", "描述"],
        "question_types": ["single_choice", "fill_blank"],
        "prompt_hint": "考查学生对基本概念、术语的记忆。题目应直接，不需要推理。",
    },
    2: {
        "name": "理解",
        "keywords": ["解释", "总结", "举例", "归纳", "用自己的话"],
        "question_types": ["single_choice", "multi_choice", "short_answer"],
        "prompt_hint": "考查学生是否真正理解了概念的含义，能否用自己的话解释。",
    },
    3: {
        "name": "应用",
        "keywords": ["计算", "实现", "求解", "使用", "应用"],
        "question_types": ["single_choice", "short_answer"],
        "prompt_hint": "考查学生能否将理论知识应用到具体问题中，进行实际计算或简单实现。",
    },
    4: {
        "name": "分析",
        "keywords": ["对比", "区分", "解构", "分析原因", "找出差异"],
        "question_types": ["multi_choice", "short_answer"],
        "prompt_hint": "考查学生能否分析问题的组成部分，识别因果关系和隐含假设。",
    },
    5: {
        "name": "评价",
        "keywords": ["评判", "论证", "推荐", "优缺点", "适用场景"],
        "question_types": ["short_answer", "open"],
        "prompt_hint": "考查学生能否对方法/模型做出有据可依的判断和评价。",
    },
    6: {
        "name": "创造",
        "keywords": ["设计", "构建", "综合", "改进", "提出新方法"],
        "question_types": ["open"],
        "prompt_hint": "考查学生能否综合所学知识，创造性地设计新方案或改进已有方法。",
    },
}


def calculate_adaptive_action(
    current_level: int,
    recent_accuracy: float,
    recent_count: int = 5,
) -> tuple[int, str]:
    """Determine whether to upgrade, maintain, or downgrade the student's level.

    Args:
        current_level: Current Bloom level (1-6)
        recent_accuracy: Accuracy rate over recent questions (0.0-1.0)
        recent_count: Number of recent questions to consider

    Returns:
        Tuple of (new_level, action_string).
    """
    if recent_count < 3:
        # Not enough data — maintain current level
        return current_level, "maintain"

    if recent_accuracy > 0.8:
        new_level = min(6, current_level + 1)
        return new_level, "upgrade"
    elif recent_accuracy < 0.5:
        new_level = max(1, current_level - 1)
        return new_level, "downgrade"
    else:
        return current_level, "maintain"


def get_question_types_for_level(level: int) -> list[str]:
    """Get appropriate question types for a Bloom level."""
    return BLOOM_LEVELS.get(level, BLOOM_LEVELS[1])["question_types"]


def get_prompt_hint_for_level(level: int) -> str:
    """Get the prompt hint for a Bloom level."""
    return BLOOM_LEVELS.get(level, BLOOM_LEVELS[1])["prompt_hint"]
```

- [ ] **Step 3: 编写测验生成引擎**

```python
# aitutor/backend/quiz/generator.py
"""Quiz generation pipeline with adversarial verification."""
import json
import uuid

from aitutor.backend.llm.client import chat_completion, structured_output
from aitutor.backend.quiz.bloom import (
    BLOOM_LEVELS,
    get_question_types_for_level,
    get_prompt_hint_for_level,
    calculate_adaptive_action,
)
from aitutor.backend.quiz.models import QuizResponse

QUIZ_GENERATION_PROMPT = """你是《人工智能导论》课程的出题专家。根据以下参数生成一道测试题。

## 题目参数
- 知识点：{topic}
- 布鲁姆认知层次：L{level} ({level_name})
- 层次说明：{level_hint}
- 题目类型要求：从 {question_types} 中选择最合适的

## 输出要求
1. 题目语言：中文
2. 选择题必须提供 4 个选项
3. 答案必须准确无误
4. 解析必须详细，解释为什么正确答案是对的、错误选项错在哪里
5. 难度匹配指定的布鲁姆层次

## 输出格式（JSON）
{{
  "question": "题面文本",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "question_type": "single_choice",
  "answer": "B",
  "explanation": "详细解析..."
}}
"""

VERIFICATION_PROMPT = """你是《人工智能导论》课程的审题专家。请检查以下题目是否存在问题。

## 待审题目
知识点：{topic}
布鲁姆层次：L{level} ({level_name})
题目：{question}
选项：{options}
答案：{answer}
解析：{explanation}

## 检查清单
1. 答案是否正确？（如果错误，给出正确答案）
2. 题面是否有歧义？（如果有，指出歧义在哪）
3. 难度是否匹配指定的布鲁姆层次？（如果不匹配，说明为什么不匹配）
4. 选项是否合理？（错误选项是否明显离谱）

## 输出格式（JSON）
{{
  "is_valid": true/false,
  "issues": ["问题1", "问题2"],
  "corrected_answer": "如答案有误，给出正确答案"
}}
"""


async def generate_quiz(
    topic: str,
    student_level: int,
    history: list[dict] | None = None,
) -> QuizResponse:
    """Generate a quiz question with adversarial verification.

    Args:
        topic: The knowledge topic to test
        student_level: Current Bloom level (1-6)
        history: Past quiz attempts for this student

    Returns:
        A verified QuizResponse.
    """
    level_info = BLOOM_LEVELS.get(student_level, BLOOM_LEVELS[1])
    question_types = get_question_types_for_level(student_level)
    level_hint = get_prompt_hint_for_level(student_level)

    generation_prompt = QUIZ_GENERATION_PROMPT.format(
        topic=topic,
        level=student_level,
        level_name=level_info["name"],
        level_hint=level_hint,
        question_types=", ".join(question_types),
    )

    # Step 1: Generate the question
    raw = await structured_output(
        messages=[{"role": "user", "content": f"知识点：{topic}"}],
        system_prompt=generation_prompt,
        output_schema={
            "question": "题面文本",
            "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
            "question_type": "single_choice",
            "answer": "B",
            "explanation": "详细解析...",
        },
        temperature=0.7,
    )

    # Step 2: Adversarial verification
    verification_result = await _verify_question(
        topic=topic,
        level=student_level,
        level_name=level_info["name"],
        question=raw["question"],
        options=raw.get("options", []),
        answer=raw["answer"],
        explanation=raw["explanation"],
    )

    # Step 3: If invalid, use corrected answer
    if not verification_result.get("is_valid", True):
        if "corrected_answer" in verification_result:
            raw["answer"] = verification_result["corrected_answer"]
            raw["explanation"] += "\n\n（经审题系统校正）"

    # Step 4: Calculate adaptive action
    accuracy = _calculate_recent_accuracy(history)
    new_level, action = calculate_adaptive_action(
        student_level, accuracy, len(history or [])
    )

    return QuizResponse(
        question_id=f"q_{uuid.uuid4().hex[:8]}",
        question=raw["question"],
        options=raw.get("options"),
        question_type=raw.get("question_type", "single_choice"),
        answer=raw["answer"],
        explanation=raw["explanation"],
        bloom_level=student_level,
        adaptive_action=action,
    )


async def _verify_question(
    topic: str,
    level: int,
    level_name: str,
    question: str,
    options: list[str],
    answer: str,
    explanation: str,
) -> dict:
    """Run adversarial verification on a generated question."""
    try:
        result = await structured_output(
            messages=[{
                "role": "user",
                "content": VERIFICATION_PROMPT.format(
                    topic=topic,
                    level=level,
                    level_name=level_name,
                    question=question,
                    options=json.dumps(options, ensure_ascii=False),
                    answer=answer,
                    explanation=explanation,
                ),
            }],
            system_prompt="你是严格的审题专家。只输出 JSON，不要加任何其他内容。",
            output_schema={
                "is_valid": True,
                "issues": ["问题描述"],
                "corrected_answer": "如答案有误，给出正确答案",
            },
            temperature=0.1,
        )
        return result
    except Exception:
        # Verification failed — assume question is valid
        return {"is_valid": True, "issues": [], "corrected_answer": ""}


def _calculate_recent_accuracy(history: list[dict] | None, n: int = 5) -> float:
    """Calculate accuracy over the most recent n questions."""
    if not history:
        return 0.5  # Default for new students
    recent = history[-n:]
    if not recent:
        return 0.5
    correct = sum(1 for h in recent if h.get("correct", False))
    return correct / len(recent)
```

- [ ] **Step 4: 提交**

```bash
git add aitutor/backend/quiz/ && git commit -m "feat: implement quiz generation engine with Bloom taxonomy

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 11: 测验 API 端点

**Files:**
- Create: `aitutor/backend/api/quiz.py`
- Modify: `aitutor/backend/main.py` — 挂载 Quiz 路由

- [ ] **Step 1: 编写测验 API**

```python
# aitutor/backend/api/quiz.py
"""Quiz API endpoints."""
from aitutor.backend.quiz.models import (
    QuizRequest,
    QuizSubmitRequest,
    QuizResponse,
    QuizSubmitResponse,
)
from aitutor.backend.quiz.generator import generate_quiz
from aitutor.backend.quiz.bloom import calculate_adaptive_action


async def generate_quiz_endpoint(request: QuizRequest) -> QuizResponse:
    """Generate a new quiz question."""
    return await generate_quiz(
        topic=request.topic,
        student_level=request.student_level,
        history=request.history,
    )


async def submit_quiz_endpoint(request: QuizSubmitRequest) -> QuizSubmitResponse:
    """Submit a quiz answer and get adaptive feedback."""
    # Simple: maintain current level, let the next generate call handle adaptation
    # In production, this would update a persistent student profile
    return QuizSubmitResponse(
        acknowledged=True,
        new_level=0,  # Will be calculated on next generate
        next_action="pending",
    )
```

- [ ] **Step 2: 更新 main.py 挂载 Quiz 路由**

在 `aitutor/backend/main.py` 中添加：

```python
from aitutor.backend.api.quiz import (
    QuizRequest,
    QuizSubmitRequest,
    QuizResponse,
    QuizSubmitResponse,
    generate_quiz_endpoint,
    submit_quiz_endpoint,
)

# ... 在文件末尾添加：

@app.post("/api/quiz/generate", response_model=QuizResponse)
async def quiz_generate(request: QuizRequest):
    """生成自适应测验题目。"""
    return await generate_quiz_endpoint(request)


@app.post("/api/quiz/submit", response_model=QuizSubmitResponse)
async def quiz_submit(request: QuizSubmitRequest):
    """提交测验答案。"""
    return await submit_quiz_endpoint(request)
```

- [ ] **Step 3: 提交**

```bash
git add aitutor/backend/api/quiz.py aitutor/backend/main.py && git commit -m "feat: add quiz generation and submission API endpoints

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Phase 5: Streamlit 前端

### Task 12: Streamlit 聊天界面

**Files:**
- Create: `aitutor/frontend/pages/__init__.py`
- Create: `aitutor/frontend/pages/chat.py`
- Create: `aitutor/frontend/components/__init__.py`
- Create: `aitutor/frontend/components/agent_badge.py`
- Modify: `aitutor/frontend/app.py` — 集成聊天页面

- [ ] **Step 1: 编写 Agent 徽章组件**

```python
# aitutor/frontend/components/__init__.py
"""Streamlit UI components."""
```

```python
# aitutor/frontend/components/agent_badge.py
"""Agent identity badge component for Streamlit."""
import streamlit as st

AGENT_CONFIG = {
    "math": {"icon": "🔢", "label": "数学推导 Agent", "color": "#4CAF50"},
    "algorithm": {"icon": "💻", "label": "算法实现 Agent", "color": "#2196F3"},
    "concept": {"icon": "🧠", "label": "概念辨析 Agent", "color": "#FF9800"},
}


def render_agent_badge(agent_name: str) -> None:
    """Render a colored badge showing which agent is responding."""
    config = AGENT_CONFIG.get(agent_name, AGENT_CONFIG["concept"])
    st.markdown(
        f"""<span style="
            background-color: {config['color']};
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 500;
        ">{config['icon']} {config['label']}</span>""",
        unsafe_allow_html=True,
    )
```

- [ ] **Step 2: 编写聊天页面**

```python
# aitutor/frontend/pages/__init__.py
"""Streamlit page modules."""
```

```python
# aitutor/frontend/pages/chat.py
"""Chat interface page — main Q&A interaction with multi-agent system."""
import streamlit as st
import requests
import json

BACKEND_URL = "http://localhost:8000"

AGENT_AVATARS = {
    "math": "🔢",
    "algorithm": "💻",
    "concept": "🧠",
}


def render_chat_page():
    """Render the main chat interface."""
    from aitutor.frontend.components.agent_badge import render_agent_badge

    st.title("💬 智能问答")
    st.caption("向 AITutor 提问，AI 导师组将为你解答《人工智能导论》相关问题")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar")):
            if msg["role"] == "assistant" and "agent_name" in msg:
                render_agent_badge(msg["agent_name"])
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("输入你的问题，比如「梯度下降和SGD有什么区别？」"):
        # Display user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call backend
        with st.chat_message("assistant"):
            with st.spinner("AI 导师思考中..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/chat",
                        json={
                            "message": prompt,
                            "history": [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages[-6:]  # Last 6 messages
                            ],
                        },
                        timeout=60,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        agent_name = data.get("agent_used", "concept")
                        render_agent_badge(agent_name)
                        st.markdown(data["reply"])

                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": data["reply"],
                            "agent_name": agent_name,
                            "avatar": AGENT_AVATARS.get(agent_name, "🤖"),
                        })

                        # Show sub-replies if any
                        if data.get("sub_replies"):
                            with st.expander("📋 相关子问题解答"):
                                for sub in data["sub_replies"]:
                                    st.caption(f"**{sub['agent']}**")
                                    st.markdown(sub["reply"])
                    else:
                        st.error(f"后端错误: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ 无法连接到后端服务。请确保 FastAPI 服务已启动（`uvicorn backend.main:app --reload`）")
                except requests.exceptions.Timeout:
                    st.error("⏰ 请求超时，请重试。")

    # Sidebar tips
    with st.sidebar:
        st.subheader("💡 试试这些问题")
        st.markdown("""
        **数学推导：**
        - 推导反向传播中链式法则的具体计算过程
        - 为什么交叉熵损失对分类问题比 MSE 更好？

        **算法实现：**
        - 用 NumPy 从零实现 K-means 聚类
        - 手写一个简单的 CNN 前向传播

        **概念辨析：**
        - 生成式模型和判别式模型的本质区别是什么？
        - L1 正则化和 L2 正则化在实际效果上有什么不同？

        **混合提问：**
        - 解释 Adam 优化器的原理并用代码实现
        """)
```

- [ ] **Step 3: 更新 Streamlit 入口**

修改 `aitutor/frontend/app.py`，替换骨架代码：

```python
# aitutor/frontend/app.py
"""Streamlit entry point for AITutor."""
import streamlit as st

st.set_page_config(
    page_title="AITutor - AI导论课程助教",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AITutor")
st.caption("基于多智能体协作的《人工智能导论》课程助教")

st.sidebar.title("导航")
page = st.sidebar.radio(
    "选择功能",
    ["💬 智能问答", "🕸️ 知识图谱", "📝 自适应测验"],
)

if page == "💬 智能问答":
    from aitutor.frontend.pages.chat import render_chat_page
    render_chat_page()
elif page == "🕸️ 知识图谱":
    st.info("🕸️ 知识图谱可视化即将上线...")
elif page == "📝 自适应测验":
    st.info("📝 自适应测验即将上线...")
```

- [ ] **Step 4: 提交**

```bash
git add aitutor/frontend/ && git commit -m "feat: implement Streamlit chat interface with multi-agent display

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 13: 知识图谱可视化页面

**Files:**
- Create: `aitutor/frontend/components/kg_renderer.py`
- Create: `aitutor/frontend/pages/knowledge_graph.py`
- Modify: `aitutor/frontend/app.py` — 集成 KG 页面

- [ ] **Step 1: 编写 KG 渲染组件**

```python
# aitutor/frontend/components/kg_renderer.py
"""Knowledge graph visualization component using Pyvis."""
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import requests

BACKEND_URL = "http://localhost:8000"

ENTITY_COLORS = {
    "Concept": "#4CAF50",
    "Person": "#9C27B0",
    "Algorithm": "#2196F3",
    "Prerequisite": "#FF9800",
}


def render_knowledge_graph_html(nodes: list[dict], edges: list[dict]) -> str:
    """Generate an interactive Pyvis network HTML string.

    Args:
        nodes: List of node dicts with id, label, type, category
        edges: List of edge dicts with source, target, label

    Returns:
        HTML string for embedding in Streamlit.
    """
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333")
    net.set_options("""
    var options = {
      "nodes": {
        "font": {"size": 14, "face": "sans-serif"},
        "borderWidth": 2,
        "borderWidthSelected": 4
      },
      "edges": {
        "color": {"inherit": false, "color": "#999999", "highlight": "#2196F3"},
        "smooth": {"type": "continuous"},
        "font": {"size": 10, "color": "#666666"}
      },
      "physics": {
        "barnesHut": {"gravitationalConstant": -5000, "springLength": 200},
        "stabilization": {"iterations": 100}
      }
    }
    """)

    for node in nodes:
        color = ENTITY_COLORS.get(node.get("type", "Concept"), "#999999")
        net.add_node(
            node["id"],
            label=node.get("label", node["id"]),
            title=node.get("description", ""),
            color=color,
            shape="dot",
            size=25,
        )

    for edge in edges:
        net.add_edge(
            edge["source"],
            edge["target"],
            title=edge.get("label", ""),
            label=edge.get("label", ""),
            arrows="to",
        )

    return net.generate_html()


def render_kg_page():
    """Render the knowledge graph exploration page."""
    st.title("🕸️ 课程知识图谱")
    st.caption("探索《人工智能导论》课程的知识体系结构")

    col1, col2 = st.columns([2, 3])

    with col1:
        st.subheader("🔍 概念搜索")
        query = st.text_input("输入概念名称", placeholder="例如：梯度下降")

        if query:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/kg/search",
                    json={"query": query},
                    timeout=10,
                )
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if results:
                        for r in results:
                            entity_type = r.get("type", "Concept")
                            color = ENTITY_COLORS.get(entity_type, "#999999")
                            st.markdown(
                                f"**{r['name']}** "
                                f"<span style='color:{color}'>[{entity_type}]</span>",
                                unsafe_allow_html=True,
                            )
                            st.caption(r.get("description", ""))

                            # Show neighborhood
                            if st.button(f"查看关联 →", key=f"explore_{r['id']}"):
                                st.session_state.selected_node = r["id"]
                                st.rerun()
                    else:
                        st.info("未找到匹配概念")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ 无法连接到后端")

        # Show selected node neighborhood
        if "selected_node" in st.session_state:
            node_id = st.session_state.selected_node
            st.divider()
            st.subheader("📌 关联概念")
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/kg/neighborhood",
                    json={"node_id": node_id},
                    timeout=10,
                )
                if response.status_code == 200:
                    data = response.json()
                    center = data.get("center", {})
                    if center:
                        st.markdown(f"**中心概念：{center.get('name', node_id)}**")
                        st.caption(center.get("description", ""))
                    for nb in data.get("neighbors", []):
                        entity = nb["entity"]
                        rel = nb["relation"]
                        direction = "→" if nb["direction"] == "outgoing" else "←"
                        etype = entity.get("type", "Concept")
                        st.markdown(f"- {direction} **{rel}** → [{etype}] **{entity.get('name', '')}**")
                        st.caption(entity.get("description", ""))
            except requests.exceptions.ConnectionError:
                st.error("⚠️ 无法连接到后端")

    with col2:
        st.subheader("🗺️ 知识体系全览")
        try:
            response = requests.get(f"{BACKEND_URL}/api/kg/full", timeout=10)
            if response.status_code == 200:
                data = response.json()
                html = render_knowledge_graph_html(
                    data.get("nodes", []),
                    data.get("edges", []),
                )
                components.html(html, height=650, scrolling=True)

                # Legend
                st.caption("图例：")
                cols = st.columns(4)
                for i, (etype, color) in enumerate(ENTITY_COLORS.items()):
                    cols[i].markdown(
                        f"<span style='color:{color};font-weight:bold'>●</span> {etype}",
                        unsafe_allow_html=True,
                    )
        except requests.exceptions.ConnectionError:
            st.error("⚠️ 无法连接到后端")
```

- [ ] **Step 2: 更新 app.py 集成 KG 页面**

修改 `aitutor/frontend/app.py`，将 KG 部分替换为：

```python
elif page == "🕸️ 知识图谱":
    from aitutor.frontend.pages.knowledge_graph import render_kg_page
    render_kg_page()
```

- [ ] **Step 3: 提交**

```bash
git add aitutor/frontend/ && git commit -m "feat: add knowledge graph visualization page with Pyvis

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 14: 自适应测验页面

**Files:**
- Create: `aitutor/frontend/pages/quiz.py`
- Create: `aitutor/frontend/components/quiz_card.py`
- Modify: `aitutor/frontend/app.py` — 集成 Quiz 页面

- [ ] **Step 1: 编写测验卡片组件**

```python
# aitutor/frontend/components/quiz_card.py
"""Quiz question card component."""
import streamlit as st

BLOOM_LABELS = {
    1: ("📋", "记忆"),
    2: ("💡", "理解"),
    3: ("🔧", "应用"),
    4: ("🔍", "分析"),
    5: ("⚖️", "评价"),
    6: ("🚀", "创造"),
}


def render_quiz_card(
    question: str,
    options: list[str] | None,
    question_type: str,
    bloom_level: int,
    question_id: str,
) -> str | None:
    """Render a quiz question card and return the student's answer.

    Args:
        question: The question text
        options: List of answer options (None for open-ended)
        question_type: Type of question
        bloom_level: Bloom taxonomy level
        question_id: Unique question ID for session state

    Returns:
        The student's answer string, or None if not yet answered.
    """
    icon, label = BLOOM_LABELS.get(bloom_level, ("📋", "未知"))

    st.markdown(f"### {icon} {label}层次")
    st.markdown(question)

    answer_key = f"answer_{question_id}"
    submitted_key = f"submitted_{question_id}"

    if options:
        answer = st.radio(
            "请选择你的答案：",
            options,
            key=answer_key,
            index=None,
            format_func=lambda x: x,
        )
        if st.button("提交答案", key=submitted_key, disabled=answer is None):
            return answer
    else:
        answer = st.text_area("请输入你的答案：", key=answer_key, height=100)
        if st.button("提交答案", key=submitted_key, disabled=not answer.strip()):
            return answer.strip()

    return None


def render_feedback(correct: bool, correct_answer: str, explanation: str) -> None:
    """Render answer feedback."""
    if correct:
        st.success("✅ 回答正确！")
    else:
        st.error(f"❌ 回答错误。正确答案是：**{correct_answer}**")

    with st.expander("📖 查看解析"):
        st.markdown(explanation)
```

- [ ] **Step 2: 编写测验页面**

```python
# aitutor/frontend/pages/quiz.py
"""Adaptive quiz page."""
import streamlit as st
import requests
import uuid

from aitutor.frontend.components.quiz_card import render_quiz_card, render_feedback

BACKEND_URL = "http://localhost:8000"

TOPICS = [
    "梯度下降", "反向传播", "CNN", "RNN/LSTM", "Transformer",
    "过拟合与正则化", "损失函数", "优化算法", "生成式模型",
    "K-means聚类", "SVM", "决策树",
]


def render_quiz_page():
    """Render the adaptive quiz page."""
    st.title("📝 自适应测验")
    st.caption("基于布鲁姆认知目标分类的动态测验系统")

    # Initialize session state
    if "quiz_history" not in st.session_state:
        st.session_state.quiz_history = []
    if "student_level" not in st.session_state:
        st.session_state.student_level = 1
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "show_feedback" not in st.session_state:
        st.session_state.show_feedback = False

    # Sidebar: student progress
    with st.sidebar:
        st.subheader("📊 学习进度")

        level = st.session_state.student_level
        st.metric("当前布鲁姆层次", f"L{level}")

        history = st.session_state.quiz_history
        if history:
            correct_count = sum(1 for h in history if h.get("correct"))
            accuracy = correct_count / len(history) * 100
            st.metric("准确率", f"{accuracy:.0f}%")
            st.metric("已答题数", len(history))

            if accuracy >= 80:
                st.success("🎉 准备升级！")
            elif accuracy < 50:
                st.warning("📚 需要巩固基础")
            else:
                st.info("👍 继续加油")
        else:
            st.caption("尚未答题")

        st.divider()
        if st.button("🔄 重置进度"):
            st.session_state.quiz_history = []
            st.session_state.student_level = 1
            st.session_state.current_question = None
            st.session_state.show_feedback = False
            st.rerun()

    # Main area: topic selection
    st.subheader("🎯 选择知识点")
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.selectbox("", TOPICS, label_visibility="collapsed")
    with col2:
        if st.button("🎲 生成题目", type="primary", use_container_width=True):
            with st.spinner("生成题目中..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/quiz/generate",
                        json={
                            "topic": topic,
                            "student_level": st.session_state.student_level,
                            "history": st.session_state.quiz_history,
                        },
                        timeout=60,
                    )
                    if response.status_code == 200:
                        st.session_state.current_question = response.json()
                        st.session_state.show_feedback = False
                        st.rerun()
                    else:
                        st.error(f"生成失败: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ 无法连接到后端")
                except requests.exceptions.Timeout:
                    st.error("⏰ 生成超时，请重试")

    # Display current question
    q = st.session_state.current_question
    if q:
        st.divider()

        # Show adaptive action
        action = q.get("adaptive_action", "maintain")
        if action == "upgrade":
            st.info("📈 你在当前层次表现优异，难度已提升！")
        elif action == "downgrade":
            st.warning("📉 返回上一层次巩固基础")

        answer = render_quiz_card(
            question=q["question"],
            options=q.get("options"),
            question_type=q.get("question_type", "single_choice"),
            bloom_level=q.get("bloom_level", 1),
            question_id=q.get("question_id", "unknown"),
        )

        # Handle answer submission
        if answer is not None and not st.session_state.show_feedback:
            correct = answer == q["answer"]
            st.session_state.show_feedback = True

            # Record in history
            st.session_state.quiz_history.append({
                "question_id": q["question_id"],
                "topic": topic,
                "correct": correct,
                "bloom_level": q["bloom_level"],
            })

            # Update level based on adaptive action
            if action == "upgrade":
                st.session_state.student_level = min(6, st.session_state.student_level + 1)
            elif action == "downgrade":
                st.session_state.student_level = max(1, st.session_state.student_level - 1)

            render_feedback(correct, q["answer"], q["explanation"])
            st.rerun()

        elif st.session_state.show_feedback and q:
            render_feedback(True, q["answer"], q["explanation"])
```

- [ ] **Step 3: 更新 app.py 集成 Quiz 页面**

修改 `aitutor/frontend/app.py`，将 Quiz 部分替换为：

```python
elif page == "📝 自适应测验":
    from aitutor.frontend.pages.quiz import render_quiz_page
    render_quiz_page()
```

- [ ] **Step 4: 提交**

```bash
git add aitutor/frontend/ && git commit -m "feat: implement adaptive quiz page with Bloom taxonomy

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Phase 6: 集成测试与完善

### Task 15: 端到端验证

**Files:**
- Create: `aitutor/run.sh`

- [ ] **Step 1: 编写一键启动脚本**

```bash
#!/bin/bash
# aitutor/run.sh
# 一键启动 AITutor 前后端服务

echo "🚀 启动 AITutor..."
echo ""

# Start FastAPI backend
echo "📡 启动 FastAPI 后端 (端口 8000)..."
cd "$(dirname "$0")/backend"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start Streamlit frontend
echo "🎨 启动 Streamlit 前端 (端口 8501)..."
cd "$(dirname "$0")/frontend"
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "✅ AITutor 已启动！"
echo "   后端: http://localhost:8000"
echo "   前端: http://localhost:8501"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# Trap SIGINT to cleanup
trap "echo '🛑 停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT

wait
```

```bash
chmod +x aitutor/run.sh
```

- [ ] **Step 2: 编写后端验证脚本**

```bash
# 验证后端 API
cd aitutor/backend && uvicorn main:app --port 8000 &
sleep 2

# Test health
curl http://localhost:8000/api/health

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是梯度下降？"}'

# Test KG search
curl -X POST http://localhost:8000/api/kg/search \
  -H "Content-Type: application/json" \
  -d '{"query": "梯度下降"}'

# Test KG full graph
curl http://localhost:8000/api/kg/full

# Test quiz generate
curl -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "梯度下降", "student_level": 2}'

# Cleanup
kill %1
```

- [ ] **Step 3: 提交**

```bash
git add aitutor/run.sh && git commit -m "feat: add one-click startup script and integration tests

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## 验证清单

- [ ] FastAPI 服务正常启动，`/api/health` 返回 200
- [ ] `/api/chat` 能正确路由到不同 Agent（用包含"区别"、"代码实现"等不同关键词测试）
- [ ] `/api/kg/search` 能搜索知识图谱
- [ ] `/api/kg/full` 返回完整图谱数据
- [ ] `/api/kg/neighborhood` 返回 1-hop 邻居
- [ ] `/api/quiz/generate` 返回符合布鲁姆层次的题目
- [ ] Streamlit 前端三个页面均能正常加载
- [ ] 前端调用后端 API 正常返回数据
- [ ] Agent 徽章正确显示
- [ ] 知识图谱可视化正常渲染
