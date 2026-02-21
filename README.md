# agent-sandbox

A sandbox project for experimenting with LLM-powered agents in Python.

Built with a provider-agnostic design — the application code is decoupled from
any specific LLM provider, making it easy to switch between Anthropic, OpenAI,
Azure, or any other backend by changing a single file and your `.env`.

---

## Project Structure

```
agent-sandbox/
├── src/
│   ├── llm.py        # Provider-specific wrapper (only file that knows about your LLM)
│   └── main.py       # Application logic — imports only generic LangChain interfaces
├── tests/
│   └── test_main.py  # Unit tests with mocked LLM (no real API calls needed)
├── conftest.py       # Tells pytest where the project root is
├── requirements.txt  # Pinned dependencies
├── .env.example      # Template showing required environment variables
└── python-project-setup-guide.md  # Full setup guide for future reference
```

---

## Setup

**1. Create and activate a virtual environment:**
```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
```

**2. Install dependencies:**
```
pip install -r requirements.txt
```

**3. Configure environment variables:**
```
copy .env.example .env       # Windows
cp .env.example .env         # macOS / Linux
```
Then open `.env` and add your API key.

> **API key:** Get one from [console.anthropic.com](https://console.anthropic.com).
> This is separate from a Claude Pro subscription — API access requires billing
> to be enabled on your console account.

---

## Running

```
python -m src.main
```

---

## Running Tests

Tests use a mocked LLM and do not require a real API key or credits:
```
pytest tests/ -v
```

---

## Switching LLM Providers

Only `src/llm.py` knows about the current provider (Anthropic). To switch:
1. Rewrite `src/llm.py` to wrap your new provider's SDK
2. Update `.env` with the new API key
3. `src/main.py` and all tests stay unchanged
