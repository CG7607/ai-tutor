"""Router agent — classifies user questions and dispatches to specialists."""
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
