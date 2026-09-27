> [!WARNING]
> This project is a work in progress, and the Python version is only a prototype.
> The API and structure may change significantly.

# magewind

An agent harness around the jev system-one model.

The Python version is the prototype. Once the structure is solid, it will be ported to Rust.

## Layout

```
magewind/
├── spec/                # language-neutral, shared by every implementation
│   ├── fixtures/        # test cases as JSON: input -> expected output
│   └── prompts/         # system prompts / instructions as plain text
├── docs/                # design notes, research, and how to publish
├── python/              # Python prototype (uv project), see python/README.md
├── rust/                # Rust port (not started yet)
└── typescript/          # possible Bun prototype (not started yet)
```

## Working in each language

| Language   | Folder        | Test command                                               |
| ---------- | ------------- | ---------------------------------------------------------- |
| Python     | `python/`     | `cd python && uv run pytest`                               |
| Rust       | `rust/`       | `cd rust && cargo test` (planned)                          |
| TypeScript | `typescript/` | `cd typescript && bun test` (if the Bun prototype happens) |

Each language folder has its own tooling, dependencies, and README. The root only holds shared files.

## Packages

Nothing is published yet. Each language folder is set up as a real `magewind` package at 0.1.0, with a guard that blocks publishing until a release is ready. [docs/publishing.md](docs/publishing.md) covers account setup, the release checklist, and the commands.

| Registry  | Package    | Source        | Publish guard                         |
| --------- | ---------- | ------------- | ------------------------------------- |
| PyPI      | `magewind` | `python/`     | `Private :: Do Not Upload` classifier |
| crates.io | `magewind` | `rust/`       | `publish = false` in `Cargo.toml`     |
| npm       | `magewind` | `typescript/` | `"private": true` in `package.json`   |

## License

[Apache License 2.0](LICENSE). Each package folder carries a copy of `LICENSE` so it ships inside the published package.

## Porting notes

- **Shared fixtures:** put test cases in `spec/fixtures/` and have both implementations' tests load them. When the Rust tests pass on the same fixtures, the port matches the prototype.
- **Shared prompts:** keep prompts in `spec/prompts/` as text files rather than inline strings, so both versions use the same text.
- **Keep the agent loop and `ModelClient` interface your own.** They port cleanly to a Rust trait. Keep library-specific code (e.g. Pydantic AI) inside the Python `ModelClient`.
- **Keep data as plain models.** Pydantic `BaseModel`s map closely to Rust structs with `serde`.
