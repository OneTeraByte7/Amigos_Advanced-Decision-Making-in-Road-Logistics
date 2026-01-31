"""
utils/llm_client.py
───────────────────
Thin wrapper around the Groq LLM. All agents import and use this —
never instantiate ChatGroq directly.

Why a wrapper:
  - Single place to swap models (Groq → OpenAI → local) later
  - Centralizes error handling and retry logic
  - Lets us inject system prompts per-agent cleanly
"""

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import llm_settings


def get_llm() -> ChatGroq:
    """
    Returns a configured ChatGroq instance.
    Uses the model and key from settings.
    """
    return ChatGroq(
        groq_api_key=llm_settings.api_key,
        model_name=llm_settings.model,
        temperature=0.1,             # Low temp: we want deterministic reasoning, not creativity
        max_tokens=1024,
        timeout=60,                  # 60 second timeout for complex prompts
        max_retries=2                # Retry on failure
    )


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """
    Simple invoke: takes a system prompt and user prompt,
    returns the LLM's text response.

    This is the function every agent calls when it needs to reason.
    """
    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        # Return detailed error for debugging
        error_msg = str(e)
        if "rate_limit" in error_msg.lower():
            return f"LLM Error: Rate limit exceeded. Please wait a moment and try again."
        elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return f"LLM Error: Authentication failed. Check your GROQ_API_KEY in .env file."
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            return f"LLM Error: Connection failed. Check your internet connection. Details: {error_msg}"
        else:
            return f"LLM Error: {error_msg}"