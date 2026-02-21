# Python Project Setup Guide (Windows)

A step-by-step guide to setting up a professional Python project from scratch on Windows.
Written for someone familiar with enterprise Python environments who wants to understand
the underlying tooling.

---

## Prerequisites

- Python 3.x installed and accessible via `python` in your terminal
- pip (Python's package manager) installed alongside Python

Verify both with:
```
python --version
pip --version
```

---

## Concept Overview

In enterprise environments, tools like virtual environments, dependency files, and
linters are typically set up for you. Here's what each piece does:

| Tool / Concept      | What it does                                                              |
|---------------------|---------------------------------------------------------------------------|
| **Virtual env**     | Isolates project dependencies so they don't clash globally                |
| **pip**             | Installs Python packages (like npm for Node, Maven for Java)              |
| **requirements.txt**| Lists all packages your project needs (like package.json)                 |
| **.gitignore**      | Tells git which files NOT to track (e.g. your local venv)                 |
| **.env**            | Stores secrets/config locally (API keys, URLs) — never committed to git   |
| **.env.example**    | A safe template showing which variables are needed — committed to git     |
| **langchain-core**  | Provider-agnostic LLM abstractions — swap AI providers without code changes|

---

## Step 1 — Create a Project Folder

Create a folder for your project and navigate into it:
```
mkdir my-project
cd my-project
```

---

## Step 2 — Create a Virtual Environment

A **virtual environment** is an isolated Python installation just for this project.
This means packages you install here won't affect other projects or your system Python.

```
python -m venv venv
```

This creates a `venv/` folder inside your project. Think of it as a project-scoped
Python installation.

**Why this matters:** Without a venv, all packages install globally and different
projects can end up with conflicting package versions.

---

## Step 3 — Activate the Virtual Environment

You must activate the venv every time you open a new terminal for this project.

On Windows (Command Prompt / PowerShell):
```
venv\Scripts\activate
```

On macOS / Linux:
```
source venv/bin/activate
```

After activation, your terminal prompt changes to show `(venv)` at the start,
confirming you are inside the virtual environment.

To deactivate (exit the venv):
```
deactivate
```

---

## Step 4 — Install Packages

With the venv activated, install packages using pip:
```
pip install requests          # example: HTTP library
pip install flask             # example: web framework
```

Packages install only inside your venv — they are not visible to other projects.

---

## Step 5 — Freeze Dependencies to requirements.txt

After installing packages, save the full list so others (or you on another machine)
can recreate the exact same environment:

```
pip freeze > requirements.txt
```

This creates a `requirements.txt` file like:
```
requests==2.31.0
flask==3.0.0
...
```

**To recreate the environment on a new machine:**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 6 — Create a .gitignore File

You should NOT commit your `venv/` folder to git — it is large, platform-specific,
and fully reproducible from `requirements.txt`.

Create a `.gitignore` file in your project root with at minimum:
```
venv/
__pycache__/
*.pyc
*.pyo
.env
```

---

## Step 7 — Project Structure (Recommended)

A clean starting structure for any Python project:

```
my-project/
├── venv/                  # Virtual environment (never committed to git)
├── src/                   # Your source code lives here
│   ├── llm.py             # Provider-specific wrapper (only file that knows about your LLM)
│   └── main.py            # Application logic — imports only generic LangChain interfaces
├── tests/                 # Unit tests
│   └── test_main.py
├── conftest.py            # Tells pytest where the project root is (see Step 9)
├── requirements.txt       # Package dependencies
├── .env                   # Your real secrets — never committed to git
├── .env.example           # Safe template showing required variables — committed to git
├── .gitignore             # Files to exclude from git
└── README.md              # Project documentation
```

---

## Step 8 — Running the Project

With the venv activated, run your script using the `-m` flag:
```
venv\Scripts\activate
python -m src.main
```

Or without activating (calling the venv's Python directly):
```
venv\Scripts\python -m src.main
```

**Why `-m src.main` and not `python src/main.py`?**
When you run `python src/main.py`, Python sets the base path to the `src/` folder,
so `from src.llm import ...` fails — there is no `src` inside `src/`.
The `-m` flag tells Python to run the file as a module starting from the current
directory, so the project root becomes the base and all imports resolve correctly.
The same reason `conftest.py` was needed for pytest.

---

## Step 9 — Writing and Running Tests

### Install pytest
pytest is the standard Python testing tool (install it like any other package):
```
pip install pytest
pip freeze > requirements.txt    # update requirements after installing
```

### conftest.py — the project root anchor
Create an empty `conftest.py` file at the project root:
```
# conftest.py (contents can be empty)
```

**Why this file exists:** When pytest runs, it searches upward through the folder
tree for a `conftest.py`. The highest directory where it finds one becomes the
project root, and that directory is added to Python's import path. Without it,
pytest looks from inside `tests/` and cannot find your `src/` folder, causing
`ModuleNotFoundError`. The file's location is what matters — not its contents.

```
my-project/          ← conftest.py here anchors the root
├── conftest.py
├── src/
│   └── main.py      ← reachable as `from src.main import ...`
└── tests/
    └── test_main.py ← can now import from src without errors
```

### Run tests
```
venv\Scripts\activate
pytest tests/ -v
```

The `-v` flag means "verbose" — it prints each test name and whether it passed
or failed, instead of just a summary dot.

---

## Step 10 — Integrating LLMs (Provider-Agnostic Pattern)

When calling an LLM (e.g. Claude, GPT-4, Azure OpenAI), the goal is to write
application code that is not tied to any specific provider. This matters because:
- You may use Anthropic at home but OpenAI or Azure at work
- Your company may switch providers over time
- Tests should not depend on live API calls

### The pattern: abstract behind a common interface

LangChain's `langchain-core` package provides a generic `BaseChatModel` interface.
You write a thin wrapper class that implements this interface for your chosen provider.
Your application code only ever imports from `langchain_core` — never from the provider.

```
Your code (main.py)
    ↓ imports only from langchain_core
BaseChatModel interface
    ↓ implemented by
src/llm.py  ← the ONLY file that knows about your provider (e.g. Anthropic)
```

**`src/llm.py` — provider-specific wrapper (the only file that changes per provider):**
```python
import anthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

class AnthropicChatModel(BaseChatModel):
    model_name: str = "claude-opus-4-6"
    max_tokens: int = 1024

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        # convert LangChain messages → Anthropic format, call API, return result
        ...

    @property
    def _llm_type(self):
        return "anthropic"
```

**`src/main.py` — application code, zero provider knowledge:**
```python
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import AnthropicChatModel   # ← only this line changes per provider

def get_joke(llm=None):
    if llm is None:
        llm = AnthropicChatModel()
    response = llm.invoke([HumanMessage(content="Tell me a joke.")])
    return response.content
```

**To switch providers at work:** write a new wrapper in `llm.py` (or install a
`langchain-<provider>` package) and update the import in `main.py`. Nothing else changes.

---

### Setting up API keys with .env

Never hardcode API keys in your source code. Use a `.env` file loaded by `python-dotenv`.

**Install python-dotenv:**
```
pip install python-dotenv
pip freeze > requirements.txt
```

**Create `.env.example`** — a template that is safe to commit to git:
```
# Copy this file to .env and fill in your real values.
# .env is excluded from git — never commit real API keys.
ANTHROPIC_API_KEY=your_api_key_here
```

**Create `.env`** — your real secrets, never committed:
```
ANTHROPIC_API_KEY=sk-ant-...
```

**Load in your code:**
```python
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file and injects values into os.environ
api_key = os.environ["ANTHROPIC_API_KEY"]
```

**The `.env` / `.env.example` pattern:**

| File            | Contains         | Committed to git? |
|-----------------|------------------|-------------------|
| `.env`          | Real secrets     | NO — in .gitignore|
| `.env.example`  | Placeholder keys | YES — safe template|

When someone clones your project, they copy `.env.example` to `.env` and fill in their own values.

---

### Testing LLM code without real API calls

Pass the LLM as a parameter so tests can inject a mock — no patching internals needed:

```python
# tests/test_main.py
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from src.main import get_joke

def test_get_joke_returns_string():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Why don't scientists trust atoms?")

    result = get_joke(llm=mock_llm)   # inject mock — no real API call made

    assert isinstance(result, str)
    assert len(result) > 0
```

This pattern (called **dependency injection**) makes code testable and flexible —
the function accepts any object that satisfies the interface, real or mock.

---

## Step 11 — Optional But Recommended Tools

### Code formatter — Black
Automatically formats your code to a consistent style.
```
pip install black
black src/          # format all files in src/
```

### Linter — Flake8
Checks for code style issues and potential bugs.
```
pip install flake8
flake8 src/
```

### Environment variables — python-dotenv
Lets you store secrets/config in a `.env` file instead of hardcoding them.
```
pip install python-dotenv
```
Create a `.env` file:
```
DATABASE_URL=your_db_url
API_KEY=your_api_key
```
Load in your code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
```
**Important:** Always add `.env` to your `.gitignore` — never commit secrets.

---

## Quick Reference — Commands Cheat Sheet

```
# Create project and venv
mkdir my-project && cd my-project
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# Install a package
pip install <package-name>

# Save dependencies
pip freeze > requirements.txt

# Install from requirements on a new machine
pip install -r requirements.txt

# Run the project
python -m src.main

# Run tests
pytest tests/ -v

# Deactivate venv
deactivate
```

---

## Common Mistakes to Avoid

1. **Installing packages before activating venv** — they go to your global Python.
   Always see `(venv)` in your prompt before running `pip install`.

2. **Committing venv/ to git** — always have it in `.gitignore`.

3. **Forgetting to update requirements.txt** — run `pip freeze > requirements.txt`
   after every `pip install`.

4. **Hardcoding secrets in code** — use `.env` + `python-dotenv` instead.

5. **Putting real API keys in `.env.example`** — `.env.example` is committed to git
   and is public. It must only ever contain placeholder values like `your_api_key_here`.
   Real keys belong only in `.env` (which is in `.gitignore`).

6. **Committing a real key by accident** — if it happens, rotating the key immediately
   is not enough. The key is now in git history and must be treated as compromised.
   Generate a new key from your provider's console and revoke the old one.

---

*Guide generated on 2026-02-22*
