"""聊天 API——支持文件上传上下文."""
import base64
from pathlib import Path
from pydantic import BaseModel

from aitutor.backend.agents.router import RouterAgent

router_agent = RouterAgent()


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None
    file_content: str | None = None   # 上传文件抽取的文本
    file_name: str | None = None       # 文件名（给 LLM 参考）


class ChatResponse(BaseModel):
    agent_used: str
    agent_display: str
    router_analysis: dict
    reply: str
    sub_replies: list[dict]


def 处理文件(文件字节: bytes, 文件名: str) -> str:
    """从上传文件中提取文本内容."""
    suffix = Path(文件名).suffix.lower()

    # 纯文本类
    if suffix in (".txt", ".md", ".py", ".json", ".yaml", ".yml", ".csv",
                  ".c", ".cpp", ".h", ".java", ".js", ".ts", ".html", ".css",
                  ".xml", ".sh", ".sql", ".r", ".tex"):
        try:
            return 文件字节.decode("utf-8")
        except UnicodeDecodeError:
            return 文件字节.decode("latin-1", errors="replace")

    # PDF
    if suffix == ".pdf":
        try:
            from io import BytesIO
            import pypdf
            reader = pypdf.PdfReader(BytesIO(文件字节))
            parts = []
            for page in reader.pages[:10]:  # 最多读 10 页
                t = page.extract_text()
                if t:
                    parts.append(t)
            return "\n\n".join(parts)
        except ImportError:
            return "[PDF 解析需要安装 pypdf：pip install pypdf]"

    # 其他
    return f"[无法解析的文件类型：{suffix}]"


async def handle_chat(request: ChatRequest) -> ChatResponse:
    """处理聊天消息，支持文件上下文."""
    message = request.message

    # 如果有文件内容，拼接到消息前面
    if request.file_content and request.file_name:
        prefix = (
            f"【用户上传了文件：{request.file_name}】\n"
            f"以下是文件内容，请基于此内容回答用户问题：\n\n"
            f"```\n{request.file_content[:8000]}\n```\n\n"
            f"用户问题："
        )
        message = prefix + message

    result = await router_agent.route(
        message=message,
        history=request.history,
    )
    return ChatResponse(**result)
