import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_llm() -> BaseChatModel:
    """
    Returns a base LLM instance based on available environment credentials.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "Missing credentials: Please set the ANTHROPIC_API_KEY environment variable."
        )

    # Use Anthropic Claude 3.5 Sonnet if the API key is available
    return ChatAnthropic(model="claude-3-5-sonnet-latest")
