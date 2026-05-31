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
