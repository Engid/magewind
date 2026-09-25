# magewind

An agent harness around the jev system-one model.

The Python version is the prototype. Once the structure is solid, it will be ported to Rust.

## Layout

```
magewind/
├── spec/                # language-neutral, shared by every implementation
│   ├── fixtures/        # test cases as JSON: input -> expected output
│   └── prompts/         # system prompts / instructions as plain text
├── python/              # Python prototype (uv project), see python/README.md
└── rust/                # Rust port (not started yet)
```

## Working in each language

| Language | Folder    | Test command                      |
| -------- | --------- | --------------------------------- |
| Python   | `python/` | `cd python && uv run pytest`      |
| Rust     | `rust/`   | `cd rust && cargo test` (planned) |

Each language folder has its own tooling, dependencies, and README. The root only holds shared files.

## Porting notes

- **Shared fixtures:** put test cases in `spec/fixtures/` and have both implementations' tests load them. When the Rust tests pass on the same fixtures, the port matches the prototype.
- **Shared prompts:** keep prompts in `spec/prompts/` as text files rather than inline strings, so both versions use the same text.
- **Keep the agent loop and `ModelClient` interface your own.** They port cleanly to a Rust trait. Keep library-specific code (e.g. Pydantic AI) inside the Python `ModelClient`.
- **Keep data as plain models.** Pydantic `BaseModel`s map closely to Rust structs with `serde`.
