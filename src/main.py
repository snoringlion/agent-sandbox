from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.llm import AnthropicChatModel

load_dotenv()


def get_joke(llm=None):
    """Ask the LLM for a joke.

    Args:
        llm: Any LangChain-compatible chat model. Defaults to AnthropicChatModel.
             Pass a different model here to switch providers without changing this code.
    """
    if llm is None:
        llm = AnthropicChatModel()

    messages = [
        SystemMessage(content="You are a witty comedian who specialises in short, clever jokes."),
        HumanMessage(content="Tell me one short, funny joke."),
    ]

    response = llm.invoke(messages)
    return response.content


if __name__ == "__main__":
    joke = get_joke()
    print("Here's a joke from Claude:")
    print(joke)
