# magewind — compiled notes

Compiled 2026-09-26 from three sources: the Jev project's memory (summaries of the harness,
framework and magewind conversations), the project doc `jev-support-bot-design.md`, and this repo
at commit `70f5648`. I did not have the conversation transcripts or Diogo's notes on a Jev-native
harness, only what was recorded from them. Anything marked *open* has not been decided.

## 1. Lineage

- Came out of an earlier "AI harness" thread. Worked through a shared state-machine framework
  (TypeScript, used for the customer-service bot) → the markdown-rubric / s1-tool idea → a Jev coding
  harness named **rein** → renamed **magewind** (Earthsea). Runner-up name: inwit.
- Repo: github.com/Engid/magewind. The local clone's `origin` still points at `Engid/rein.git`.
  GitHub redirects git operations after a rename but recommends `git remote set-url origin NEW_URL`
  ([GitHub docs](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)).
- Diogo (CEO of TypeSafe) shared notes on a Jev-native coding harness; those notes are design input.

## 2. Architecture decisions carried over from the framework work

These were settled for the support bot and apply to magewind unless revisited.

- **Orchestrator** is a deterministic state machine. Jev sits inside it as the **Evaluator** (the
  name he settled on; he rejected "judge", "controller", "sensor"). The Evaluator never has control.
- **Workers** are LLM + tools + prompt, used for generation only. The human talks only to the
  orchestrator, never directly to a worker.
- Orchestrator ↔ worker is **saga-style command/reply**. Both are stateless toward each other: the
  message carries current state plus a way to fetch more history. Chosen for testability, replay and
  a console view.
- The orchestrator **always reviews** returned work (too big, off-task, over-planning). Workers never
  self-certify.
- **Same shape at every scale**: an Evaluator + LLM pair inside each worker too.
- **Turn-based**, no clock or scheduler in the core. Pure `step(snapshot, input)` at the core, with a
  driver on top.
- **Edges are data, not code.** Node definition, state and questions travel in one JSON envelope that
  is logged, stored and replayed.
- Jev kinds (Choice / Score / Noul) do not compose; threshold each in its own kind and keep arithmetic
  in code. Use bands, not point thresholds. Every edge needs an `unsure` arm.
- Open values (paths, IDs, dates) are extracted by code as candidates, then a Choice picks one with a
  "none of these" option.
- Approach: single node first, then scale to multi-worker.

## 3. magewind-specific direction

- Jev is the **first layer of intelligence**: Choice to route between main functions, Score for
  coding-practice rubrics, routing to narrowly scoped LLM subagents.
- **Context is not an append-only list of strings.** It is a SQLite database that every subagent can
  query. (Also floated earlier: a tree.)
- **Jev hooks throughout**: filtering tools/actions, verifying tool calls, safety checks, style checks.
  Originally configured as markdown files of criteria, optionally with literal SQL or a plain-language
  query whose results are combined with Jev questions, plus an ordering file wiring them into a flow.
- **Markdown question language**: a prose-like way to "prompt" a System One model without writing
  JSON. The first use case was a basic LLM converting the markdown into Jev API calls instead of a
  hand-written parser. The name S1QL was dropped (SentinelOne uses it); new name *open*.
- Early versions scoped narrowly: read-only queries and checks against a directory of data (JSON, CSV,
  email, code) with small LLMs helping, optional reports. Full agentic coding comes later.
- Goal: a "magical", configurable agent with precise, strictly applied criteria instead of
  prompt-and-hope.

## 4. Language, tooling, extensibility

- **Python prototype, Rust port later**, with shared `spec/fixtures` and `spec/prompts` so both
  implementations run the same tests. Python chosen partly to learn Python; wants async state machine
  with dataclasses + `match`. *Open*: going all-in on Rust from the start for speed and a single binary.
- Current Python deps: `typesafe-sdk` 0.7.1, `pydantic-ai-slim[openai]` 2.48.0, `pydantic`. Keep the
  agent loop and model interface your own; keep vendor code in one module.
- Won't fork pi; likes pi's extensibility. *Open*: pi-style code extensions/hooks that magewind can
  write for itself, versus a new markdown hook syntax.
- Plans a GUI app later (similar to Claude desktop, also works with CLI tools).

## 5. Product and licensing (all *open*)

- Options considered: open-source harness with an enterprise plan; cloud version connecting to a
  customer's Azure tenant; subscription desktop tool for enterprise data.
- Torn between open source (also a portfolio piece) and going closed; notes a product is hard solo.
- License narrowed to FSL or Apache 2.0 for the core, with a CLA; wants "magewind" as a trademark.

## 6. Added in this conversation (2026-09-26)

- **Phase 1 scope**: a CLI. Each prompt runs one turn: Jev asks a set of questions about the prompt
  (intent, which tools, how hard, which model strength), code turns the answers into a toolset and
  instructions, an agent does the work, and the harness inspects the result and can run a second Jev
  check (did it do the task, did it follow preferences, is it done). The agent should say when it is
  ready to be verified.
- **Context as data, not code.** Inspired by recursive-language-model harnesses, but rather than a
  REPL where the agent writes code, the agent writes **SQL to read** context. Only the harness writes
  context; agents can read anything. Possibly **one SQLite database per session**.
- Interested in a code index (functions and their references) the agent can use instead of reading
  whole files.

See `phase-1.md` for the design sketch and `research/code-search.md` for how other harnesses read code.
