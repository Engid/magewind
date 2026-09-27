# How coding harnesses find and read code

Checked 2026-09-26. Every claim links to the page it came from. Where a vendor's own page was the
only source, that is the extent of the evidence.

## Short answer

- **No harness I checked reads every file.** They search first (grep/ripgrep, glob), then read the
  files or line ranges the search pointed to. Read tools return a whole file up to a cap and page
  through larger ones with `offset`/`limit`.
- **Indexes exist, but most harnesses don't build one.** Claude Code, Codex and pi use plain search
  tools. Aider builds a tree-sitter symbol map. Cursor built an embedding index in 2025 and its
  current docs describe a local regex index and no embeddings.
- **Tree-sitter parses; it does not link.** It gives you syntax trees and tags for definitions and
  references by name. Joining references to definitions is your code (Aider does this). Precise
  resolution needs a language server.

## Harness by harness

**Claude Code: no index.** Tools are Glob, Grep (ripgrep), and Read, which "returns the file from the
start" and pages with `offset`/`limit` when a file exceeds the token limit. An LSP tool (definitions,
references, type errors) exists but is absent by default and needs a code-intelligence plugin
([tools reference](https://code.claude.com/docs/en/tools-reference)). Boris Cherny: "Early versions of
Claude Code used RAG + a local vector db, but we found pretty quickly that agentic search generally
works better. It is also simpler and doesn't have the same issues around security, privacy,
staleness, and reliability" ([X post](https://x.com/bcherny/status/2017824286489383315)).

**OpenAI Codex: no index.** The prompting guide says to "prefer using `rg` or `rg --files`", to read
multiple files in parallel, and to edit with the `apply_patch` format the model was trained on
([Codex prompting guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)).

**pi: no index.** Four tools: read, write, edit, bash. Read "Defaults to first 2000 lines. Use
offset/limit for large files" ([Mario Zechner's post](https://mariozechner.at/posts/2025-11-30-pi-coding-agent/)).
Session storage is covered in its own section below.

**Aider: tree-sitter repo map.** Aider parses the repo with tree-sitter to find "where functions,
classes, variables, types and other definitions occur" and "where else in the code these things are
used or referenced". It builds a graph where files are nodes and edges are dependencies, ranks it,
and sends only the top-ranked definitions and signatures that fit a token budget (`--map-tokens`,
default 1k, grown when no files are in the chat)
([repo map docs](https://aider.chat/docs/repomap.html), [2023 post](https://aider.chat/2023/10/22/repomap.html)).
This is the closest existing thing to "functions and their references".

**Cursor: embeddings, then a local regex index.**
- Nov 2025: semantic search trained on agent traces, "on average 12.5% higher accuracy in answering
  questions (6.5%–23.5% depending on the model)", used together with grep
  ([blog](https://cursor.com/blog/semsearch)).
- Jan 2026: how the index worked. A Merkle tree of file hashes finds what changed; changed files are
  "split into syntactic chunks" and embedded; embeddings are cached by content; teammates' indexes are
  reused ([blog](https://cursor.com/blog/secure-codebase-indexing)). That is what "index your
  codebase" did.
- Mar 2026: Instant Grep, a sparse n-gram index built and queried on the user's machine, because "the
  agents just love to use grep" ([blog](https://cursor.com/blog/fast-regex-search)).
- The current search docs list Instant Grep and an Explore subagent, and state Cursor "does not store
  embeddings of your codebase for search" ([docs](https://cursor.com/docs/agent/tools/search)). I found
  no post explaining the change away from embeddings.

**Sourcegraph Cody: dropped embeddings in Feb 2024** for its own code search engine with BM25. Reasons
given: code had to go to a third party, keeping embeddings fresh was operational work, and vector
search got hard past 100,000 repos ([blog](https://sourcegraph.com/blog/how-cody-understands-your-codebase)).

**Cognition SWE-grep (Oct 2025): a trained search subagent.** An RL-trained model that makes up to 8
parallel grep/read/glob calls per turn over at most 4 turns. They rejected embeddings because results
"can be inaccurate, especially for complex queries that require to jump across the codebase multiple
times" ([blog](https://cognition.com/blog/swe-grep)).

**Serena: language servers as agent tools.** An MCP server that exposes symbol-level operations
(find symbol, find references, insert after symbol, rename) backed by language servers
([repo](https://github.com/oraios/serena)).

## Tree-sitter specifically

- "A parser generator tool and an incremental parsing library. It can build a concrete syntax tree
  for a source file and efficiently update the syntax tree as the source file is edited." The runtime
  is C11 with official bindings for Rust, Python and others ([site](https://tree-sitter.github.io/tree-sitter/)).
  The Rust crate is a binding to that runtime.
- **Tags queries** (`tags.scm`) label `@definition.function`, `@definition.class`, `@reference.call`
  and so on, with an `@name` capture. GitHub calls this "search-based code navigation": matches are by
  name, not resolved ([code navigation](https://tree-sitter.github.io/tree-sitter/4-code-navigation.html)).
  Two functions named `load` in different modules look the same.
- **Precise resolution** needs more. GitHub's stack-graphs did it on top of tree-sitter and was
  archived on Sep 9, 2025 ([repo](https://github.com/github/stack-graphs)). Language servers are the
  practical option (Claude Code's LSP tool, Serena).
- Python: `tree-sitter-language-pack` ships prebuilt grammars for 371 languages (v1.20.0, Sep 14 2026)
  ([PyPI](https://pypi.org/project/tree-sitter-language-pack/)). Structural search: ast-grep (Rust,
  tree-sitter) ([site](https://ast-grep.github.io/)).

## pi and session storage

The pi-mono repo now redirects to **github.com/earendil-works/pi**.

- The coding agent CLI stores each session as a JSONL file under `~/.pi/agent/sessions/`, grouped by
  working directory. Entries form a tree through `id`/`parentId`, so branching happens in place
  ([session format](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/session-format.md),
  [sessions](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sessions.md)).
- **Compaction does not delete history.** A compaction entry stores a summary and `firstKeptEntryId`;
  rebuilding context swaps the older entries for the summary.
- **`context_edit` entries** are append-only edits that change what the model sees next without
  changing the raw history. `replacement: null` drops an entry from context.
- **Tool loadout is logged.** System messages record `toolsAdded` / `toolsRemoved`, and replaying
  them yields the current prompt and tools. magewind's per-turn toolset would log the same way.
- **pi also has a SQLite backend**: `@earendil-works/pi-session-backend-sqlite-node` (0.87.1,
  2026-09-22) creates one `.sqlite` file per session by default. Its README says the host "guarantees
  one writable owner per Session"; the backend itself has no cross-process lock
  ([package](https://github.com/earendil-works/pi/tree/main/packages/session-backends/sqlite-node)).
  This is close to the one-database-per-session, harness-only-writes idea and worth reading before
  building magewind's store.

## What this suggests for magewind

- Phase 1 needs no index. `grep` + `glob` + `read(path, offset, limit)` is what Claude Code, Codex and
  pi ship.
- A code index fits the SQLite context idea well. The harness runs tree-sitter tags over the repo and
  writes `symbol(name, kind, path, line)` and `ref(name, kind, path, line)` rows into the same store.
  The agent then asks structural questions with the SQL tool it already has, e.g. every call site of a
  function. This is Aider's input without Aider's ranking step, and it inherits the name-only caveat.
- Keep embeddings out until there is a measured need. Claude Code and Cody both tried them and moved
  to search; Cursor measured a gain from them in 2025, yet its current docs say it no longer stores
  them. The evidence is mixed, and the cost (freshness, privacy, infrastructure) is certain.
