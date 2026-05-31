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
