## What

Adds the first CI to this repo. Before this PR there was **no `.github/workflows`
directory at all** — one of 19 repos in that state.

**Why it matters here specifically:** PR #1 (`63f6ef5`) shrank the todo tool
description 6,611 → 6,470 B and landed a **byte-for-byte pin** so it could not
silently drift back. That pin has been **executed by nothing** — committed, but
run only when a human remembered to. It now runs on every push to `main` and
every PR, on three Pythons.

One file, `+114/-0`. Nothing else in the workflow commit.

## The workflow

Two job definitions → **four checks** on `push: branches:[main]` and
`pull_request: branches:[main]`, with `permissions: contents: read`.

| Check | Command |
|---|---|
| **Lint (ruff)** | `uvx ruff@0.16.6 check --isolated --select E4,E7,E9,F .` |
| **Tests (Python 3.11 / 3.12 / 3.13)** | `uv sync --all-extras --dev` → `uv run pytest -q` |

- **ruff is pinned twice** — the tool version *and* the rule set. `--isolated`
  so the result cannot depend on a config discovered up the directory tree; the
  runner and a laptop run byte-for-byte the same command.
- `uv run pytest` picks up `[tool.pytest.ini_options]` from `pyproject.toml`
  (`testpaths`, `--import-mode=importlib`, `asyncio_mode=strict`), so CI and
  local are the same invocation. This repo has **no Makefile** (removed
  deliberately in `bb3d15c`), so there is no check target to mirror.
- `requires-python = ">=3.11"` → the floor plus the two current minors, with
  `fail-fast: false` so a version-specific break is visible as such.
- **No path filters, no error-tolerant step keys, no shell-level failure
  suppression.** Verified by grep on the committed file: `paths:`,
  `paths-ignore:`, `continue-on-error`, `|| true` → **zero matches anywhere in
  the file**, prose included.
- Nothing here calls an LLM. No API keys, no cost per run.

## What the suite actually covers — 10 real tests, NOT an import smoke

| File | What it is |
|---|---|
| `tests/test_behavioral.py` | inherits `amplifier_core.validation.behavioral.ToolBehaviorTests` |
| `tests/test_validation.py` | inherits `amplifier_core.validation.structural.ToolStructuralTests` |
| `tests/test_description_pin.py` | 2 tests — the byte-for-byte description pin (526 chars) + a guard on the pin's own literal |

## Red-then-green — both runs, both URLs

**RED — run [`34157370586`](https://github.com/microsoft/amplifier-module-tool-todo/actions/runs/34157370586)**
(scratch PR #2, head `c0a2d127`, **4/4 checks red**):

```
Tests (Python 3.11) | Run test suite | 1 failed, 10 passed in 0.07s
Tests (Python 3.12) | Run test suite | 1 failed, 10 passed in 0.11s
Tests (Python 3.13) | Run test suite | 1 failed, 10 passed in 0.06s
Lint (ruff)         | Lint           | F401 [*] `os` imported but unused  ->  Found 1 error.
```

The **`10 passed` beside each failure is the load-bearing part**: the real suite
collected and executed, and a deliberate assert failed *inside* it. A setup,
import or lint error would have shown `0 passed` and proved nothing. Two
independent defects were planted so each job failed for its **own** reason — a
failing assert in `tests/test_red_proof.py` for the Tests job, and an unused
import (F401, inside the pinned rule set, not collected by pytest) for Lint.

**GREEN — run [`34157472320`](https://github.com/microsoft/amplifier-module-tool-todo/actions/runs/34157472320)**
(this PR, workflow-only commit `fa1f7cb3a4426378e1130855cdfed812b291f7b6`,
**4/4 checks green**):

```
Tests (Python 3.11) | 10 passed in 0.07s
Tests (Python 3.12) | 10 passed in 0.07s
Tests (Python 3.13) | 10 passed in 0.08s
Lint (ruff)         | All checks passed!
```

Both job logs are committed verbatim under
`docs/lanes/j1e6-ci-tool-todo/evidence/`.

**Scratch cleanup, verified rather than assumed:** PR #2 is `CLOSED` and branch
`ci/red-proof-j1e6` was deleted — then **read back from the remote**
(`git ls-remote --heads origin ci/red-proof-j1e6` → **0 refs**).

## Clean `main` was green on this gate — and what sits just outside it

Measured at `63f6ef5` before authoring anything: `uv run pytest -q` → **10
passed**; the pinned ruff invocation → **All checks passed!** So there was
nothing to stop and report, and nothing was weakened to get there.

Two things are **deliberately not wired**, disclosed rather than silently
excluded. Neither is breakage; both are *source* changes that do not belong in
the PR that introduces CI:

1. **ruff's full modern default tier** reports **2** findings, both style
   opinions this repo has never adopted —
   `amplifier_module_tool_todo/__init__.py:10:1 I001` (import block unsorted)
   and `:31:5 PLR1711` (useless `return`).
2. **`ruff format --check`** would reformat **1** file (that same `__init__.py`,
   purely line-wrapping); 9 files already formatted.

Follow-ups if wanted: `uvx ruff@0.16.6 format .`, then clear I001/PLR1711 and
widen the rule set.

## Two more decisions worth seeing

- **`uv sync`, not `uv sync --frozen`** — installs from the committed `uv.lock`,
  which pins the `amplifier-core` git dependency to an exact commit. Deliberate:
  this suite *inherits its behavioral and structural tests from amplifier-core*,
  so a floating `main` would make this repo's CI go red for a change made in
  another repo. Bumping amplifier-core is now a lockfile commit here.
- **No uv cache.** `astral-sh/setup-uv`'s cache keys on `**/uv.lock`, and this
  repo does commit one, so enabling it would work — it was still omitted because
  16 packages and a sub-second suite mean the cache buys nothing while adding a
  failure mode *ahead of* the tests.

## After merge

Please confirm main HEAD reports a successful check-run —
`gh api repos/microsoft/amplifier-module-tool-todo/commits/main/check-runs`.
**Configured is not installed.**
