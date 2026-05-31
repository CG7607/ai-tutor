"""Base class for specialist agents."""
from dataclasses import dataclass, field
from abc import ABC

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
