# magewind (Python prototype)

An agent harness around the jev system-one model. This is the Python prototype. See the [root README](../README.md) for the overall repo layout.

## Setup

This project uses [uv](https://docs.astral.sh/uv/) to manage the Python version, the virtual environment, and dependencies. Run all commands below from the `python/` folder (or from the repo root with `uv --directory python ...`).

```sh
uv sync          # create .venv and install everything from uv.lock
uv run pytest    # run the tests
uv run magewind  # run the program
```

## Common commands

| Command                  | What it does                                 |
| ------------------------ | -------------------------------------------- |
| `uv run pytest`          | Run the tests                                |
| `uv run magewind`        | Run `main()` in `src/magewind/__init__.py`   |
| `uv add <package>`       | Add a dependency                             |
| `uv add --dev <package>` | Add a dev-only dependency (e.g. test tools)  |
| `uv run python`          | Open a Python prompt with the project loaded |

## Project layout

```
python/
├── pyproject.toml        # project config and dependency list
├── uv.lock               # exact installed versions (commit this)
├── .python-version       # pins Python 3.12
├── src/magewind/
│   ├── __init__.py       # makes `magewind` a package; main() lives here
│   ├── model.py          # Message type + ModelClient (the API wrapper)
│   └── agent.py          # Agent class with a simple loop
└── tests/test_agent.py   # a test that uses a fake client
```

## How the pieces fit together

- **`Message`** (`model.py`) is a `@dataclass`, a class that just holds data (`role` and `content`).
- **`ModelClient.complete()`** (`model.py`) is the only place that should talk to the jev system-one API. The rest of the code only sees `Message` objects.
- **`Agent.step()`** (`agent.py`) adds user input to the history, asks the model for a reply, and saves the reply to the history.
- **Tests** use a fake `EchoClient` instead of the real API, so they run without network access or an API key.
- **Type hints** (`list[Message]`, `-> Message`) are optional in Python, but they let your editor catch mistakes early.

## Next steps

1. **Get an API key.** Create one at https://console.typesafe.ai/ and set `TYPESAFE_API_KEY` in your environment. The SDK (`typesafe-sdk`) is already installed. Docs: https://docs.typesafe.ai/sdk/python/
2. **Write `ModelClient`.** Wrap `TypeSafeClient.system_one(state=..., questions=...)`. Note that System One answers structured questions (`Noul`, `Choice`, `Score`) rather than chat messages, so reshape `Message` / `complete()` to fit.
3. **Handle tool calls in `Agent.step()`.** See the TODO: inspect the reply, run any tools it asks for, and loop until the model is done.
4. **Update `main()`** in `src/magewind/__init__.py` to create an `Agent` and run a simple input loop.
5. **Add the LLM side.** Set `OPENAI_API_KEY` and follow the Pydantic plan below, using a Luna model (`gpt-5.6-luna` or `gpt-6-luna`).

## Learning Pydantic, step by step

Introduce one piece at a time, and keep the agent loop in `agent.py` your own.

1. **Make `Message` a pydantic `BaseModel`** (`model.py`). Swap `@dataclass` for `class Message(BaseModel):` and keep the same fields. Pydantic checks the data when a `Message` is created and gives you `.model_dump()` and `.model_validate()` for converting to and from plain dicts. Start here: it only touches `Message`, and no API calls are involved.
2. **Call the model inside `ModelClient.complete()` with Pydantic AI.** `pydantic_ai.direct.model_request_sync` sends one request to the model and returns its reply, with no loop. Convert your `Message` list into Pydantic AI's message types (`pydantic_ai.messages`, e.g. `ModelRequest`, `ModelResponse`, `TextPart`), then turn the reply back into a `Message`. Switching models later is just a different model name. See "direct model requests" in the docs: https://ai.pydantic.dev/
3. **Structured output.** Define a `BaseModel` for the data you want back (a plan, a decision, and so on) and check the reply with `YourModel.model_validate_json(text)`. This fits well with Jev's typed answers.
4. **Later, if you want:** add tools, then consider letting Pydantic AI's `Agent` run the loop once you know what your own loop does.

## Dependencies

- `typesafe-sdk`: client for the TypeSafe System One API.
- `pydantic-ai-slim[openai]`: LLM agent framework (tools, structured output, history). The `[openai]` extra installs the `openai` SDK.
- `pydantic`: data validation. Listed directly because you'll import it in your own code.

## Reminders

- Keep your API key in an environment variable or a `.env` file, never in code. `.env` is already in `.gitignore`.
- Commit `uv.lock`. Don't commit `.venv/` (it's ignored).
- Keep vendor-specific code in `model.py` so the rest of the harness stays easy to test.
- Pydantic AI also has an `Agent` class. Import it with an alias (`from pydantic_ai import Agent as LLMAgent`) to avoid clashing with `magewind.agent.Agent`.
