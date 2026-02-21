import os
from typing import Any, List, Optional

import anthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class AnthropicChatModel(BaseChatModel):
    """
    A LangChain-compatible chat model that wraps the Anthropic SDK.

    Why this exists:
        LangChain has provider-specific packages (e.g. langchain-anthropic,
        langchain-openai). By building our own thin wrapper around BaseChatModel,
        our application code stays 100% provider-agnostic — it only ever imports
        from langchain_core. To switch providers, you write a new wrapper class
        (or use an existing langchain-<provider> package) and swap it in one place.

    To switch providers at work:
        Replace this class with one that wraps your workplace's LLM SDK.
        Your application code (main.py, etc.) does not need to change at all.
    """

    model_name: str = "claude-opus-4-6"
    max_tokens: int = 1024

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Convert LangChain messages to Anthropic format, call the API, return the result."""
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        # LangChain separates system messages from the conversation.
        # Anthropic also keeps the system prompt separate — extract it here.
        system_prompt = None
        conversation = []

        for message in messages:
            if isinstance(message, SystemMessage):
                system_prompt = message.content
            elif isinstance(message, HumanMessage):
                conversation.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                conversation.append({"role": "assistant", "content": message.content})

        request_params = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "messages": conversation,
        }
        if system_prompt:
            request_params["system"] = system_prompt

        response = client.messages.create(**request_params)
        text = response.content[0].text

        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=text))])

    @property
    def _llm_type(self) -> str:
        """Identifier used by LangChain internals for logging and tracing."""
        return "anthropic"
