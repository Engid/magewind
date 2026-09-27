# Publishing magewind

Nothing is published yet. Each language folder is a real `magewind` package at version 0.1.0, with a
guard that makes the registry or the publish tool refuse it. To release a package, work through the
checklist, remove that package's guard, and run its commands below.

Checked 2026-09-27 with uv 0.12.13, cargo 1.95.0, npm 10.9 and bun 1.3.13.

## Packages

| Registry  | Package    | Folder        | Guard                                         | Enforced by                   |
| --------- | ---------- | ------------- | --------------------------------------------- | ----------------------------- |
| PyPI      | `magewind` | `python/`     | `"Private :: Do Not Upload"` in `classifiers` | PyPI, when the upload arrives |
| crates.io | `magewind` | `rust/`       | `publish = false` in `Cargo.toml`             | `cargo publish`, locally      |
| npm       | `magewind` | `typescript/` | `"private": true` in `package.json`           | `npm publish` / `bun publish` |

What each guard does and doesn't catch:

- **PyPI** rejects the upload on the server: "PyPI will always reject packages with classifiers
  beginning with `Private ::`" ([classifiers](https://pypi.org/classifiers/)). Nothing local checks
  it: `uv build` and `twine check` both pass with the guard in place.
- **Cargo** checks locally, including in a dry run: `cargo publish --dry-run` stops with "`magewind`
  cannot be published" ([manifest: publish](https://doc.rust-lang.org/cargo/reference/manifest.html#the-publish-field)).
- **npm** checks locally, but **not in a dry run**. With the guard in place, `npm publish --dry-run`
  reported a successful dry run. A real `npm publish` stops with "This package has been marked as
  private" ([package.json: private](https://docs.npmjs.com/cli/v11/configuring-npm/package-json#private)),
  and `bun publish` stops with "attempted to publish a private package". Both were tested here, not
  just read from docs.

## One-time account setup

### PyPI

1. Create an account at <https://pypi.org>. PyPI requires 2FA before you can upload
   ([PyPI blog](https://blog.pypi.org/posts/2024-01-01-2fa-enforced/)).
2. Create an API token. The first upload creates the project, so that token must have scope
   **Entire account** ([packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)).
   After the first release, replace it with a token scoped to `magewind` and delete the
   account-wide one.
3. uv reads the token from `--token` or the `UV_PUBLISH_TOKEN` environment variable
   (`uv publish --help`).
4. Optional: a separate account at <https://test.pypi.org> for a rehearsal upload.

PyPI also supports [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) from CI, which
avoids storing a token (`uv publish --trusted-publishing`). Worth setting up if releases move to
GitHub Actions.

### crates.io

1. Log in at <https://crates.io> with GitHub.
2. Add and verify an email address under Account Settings. Publishing requires it.
3. Create an API token, run `cargo login` and paste it. Cargo stores it in
   `~/.cargo/credentials.toml` ([Cargo book](https://doc.rust-lang.org/cargo/reference/publishing.html)).

### npm

1. Create an account at <https://www.npmjs.com>. Publishing requires 2FA, or a granular access token
   with "bypass 2FA" enabled ([npm docs](https://docs.npmjs.com/requiring-2fa-for-package-publishing-and-settings-modification)).
2. Run `npm login`. `bun publish` reads the same `.npmrc`, so one login covers both
   ([bun publish](https://bun.com/docs/cli/publish)).

## Release checklist

Do this per package. Each registry's version moves on its own.

- [ ] It works for someone who isn't you: install it in a clean environment and follow the README.
- [ ] The package README (`python/README.md`, `rust/README.md` or `typescript/README.md`) is written
      for users: what it does, how to install it, and which API keys it needs (TypeSafe, plus the
      model provider). The registry shows this file, so use full `https://github.com/Engid/magewind/...`
      links rather than relative ones like `../README.md`.
- [ ] The version in the manifest is new. Every registry allows a version only once, even after
      deleting it (see [Versions are permanent](#versions-are-permanent)).
- [ ] Tests pass.
- [ ] The guard is removed from this package only, the change is committed, and the tree is clean.
- [ ] The commit is tagged with a per-package prefix, e.g. `py-v0.1.0`, `rs-v0.1.0`, `ts-v0.1.0`,
      and the tag is pushed.
- [ ] Published with the commands below, then installed from the registry in a clean environment.

After the first release the guard has done its job. Leave it off, or put it back if you want every
release to start by removing it on purpose.

## Python → PyPI

From `python/`:

```sh
rm -rf dist                      # uv publish uploads everything in dist/ by default
uv build
tar tzf dist/magewind-*.tar.gz   # check what ships
unzip -l dist/magewind-*.whl
uvx twine check dist/*
```

Optional rehearsal on TestPyPI:

```sh
uv publish --publish-url https://test.pypi.org/legacy/ --token "$TESTPYPI_TOKEN"
```

Release and smoke test:

```sh
uv publish --token "$PYPI_TOKEN"       # or export UV_PUBLISH_TOKEN
uvx --from magewind==0.1.0 magewind    # runs the published entry point
```

As configured today, the wheel holds only `src/magewind`. The sdist also carries `tests/`, `uv.lock`
and `.python-version`.

## Rust → crates.io

From `rust/`:

```sh
cargo package --list      # check what ships
cargo publish --dry-run   # builds the packaged crate, stops before uploading
cargo publish
```

`include` in `Cargo.toml` limits the crate to `src/`, `README.md` and `LICENSE`, so `todo.md` stays
out. Right now the crate is a library (`src/lib.rs`). If the port becomes a CLI, add `src/main.rs`
before the first release.

## TypeScript → npm

From `typescript/`:

```sh
npm pack --dry-run   # check what ships (does not test the guard)
npm publish          # or: bun publish
```

### If the prototype runs on Bun

Decide how people will run it before the first release:

- **Bun-only npm package.** Point `bin` at a file that starts with `#!/usr/bin/env bun`. Users need
  Bun installed. npm's docs tell you to start `bin` files with `#!/usr/bin/env node`
  ([package.json: bin](https://docs.npmjs.com/cli/v11/configuring-npm/package-json#bin)), and
  Bun-only APIs such as `bun:sqlite` don't exist in Node, so Node users can't run it.
- **Standalone binary.** `bun build --compile` bundles the app "along with a copy of the Bun runtime"
  into one executable, `bun:sqlite` included, and cross-compiles with `--target` (for example
  `bun-darwin-arm64`, `bun-linux-x64`, `bun-windows-x64`)
  ([Bun executables](https://bun.com/docs/bundler/executables)). Ship these as GitHub Release assets.
- **Node-compatible package.** Compile to JavaScript with type declarations and avoid Bun-only APIs.
  The most work, and the widest reach.

TypeSafe publishes an official TypeScript SDK, [`@typesafe-ai/sdk`](https://www.npmjs.com/package/@typesafe-ai/sdk)
(0.6.0 as of this writing, `engines: node >=20`).

## Versions are permanent

- **PyPI:** "PyPI does not allow for a filename to be reused, even once a project has been deleted
  and recreated" ([PyPI help](https://pypi.org/help/#file-name-reuse)).
- **crates.io:** "The version can never be overwritten, and the code cannot be deleted." A bad release
  can only be yanked ([Cargo book](https://doc.rust-lang.org/cargo/reference/publishing.html)).
- **npm:** unpublishing is allowed within 72 hours if nothing depends on the package, and after that
  only under narrow conditions. Either way, "Once `package@version` has been used, you can never use
  it again" ([unpublish policy](https://docs.npmjs.com/policies/unpublish)).

## Why nothing was published to hold the name

All three registries prohibit publishing a package just to reserve its name:

- PyPI treats a project as invalid when it "is name squatting (package has no functionality or is
  empty)" ([PEP 541](https://peps.python.org/pep-0541/)).
- npm: "Package names are considered squatted if the package has no genuine function"
  ([disputes policy](https://docs.npmjs.com/policies/disputes)).
- crates.io prohibits a crate that exists only to reserve a name "without having any genuine
  functionality, purpose, or significant development activity on the corresponding repository"
  ([RFC 3463](https://rust-lang.github.io/rfcs/3463-crates-io-policy-update.html)).

As of 2026-09-26 the name was free on all three. Check again before the first release:

```sh
curl -s -o /dev/null -w "%{http_code}\n" https://pypi.org/pypi/magewind/json          # 404 = free
curl -s -o /dev/null -w "%{http_code}\n" https://registry.npmjs.org/magewind           # 404 = free
curl -s -o /dev/null -w "%{http_code}\n" -A "magewind-check" https://crates.io/api/v1/crates/magewind  # 404 = free
```
