"""LLM configuration from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

# 从项目根目录加载 .env，不受工作目录影响
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)


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
