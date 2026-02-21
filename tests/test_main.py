from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from src.main import get_joke


def test_get_joke_returns_string():
    """Test that get_joke() returns the LLM's response as a string.

    We pass in a mock LLM rather than patching internals — this is the cleanest
    way to test provider-agnostic code. The mock satisfies the same interface
    (a LangChain chat model with an .invoke() method) without making real API calls.
    """
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Why don't scientists trust atoms? Because they make up everything!")

    result = get_joke(llm=mock_llm)

    assert isinstance(result, str)
    assert len(result) > 0
    assert "atoms" in result
