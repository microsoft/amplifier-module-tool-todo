# Lane j1e6-ci-tool-todo — DONE-NOTE

**Item:** `model_performance-j1e6` (project `model_performance`)
**Repo:** `microsoft/amplifier-module-tool-todo`
**Branch:** `lane/j1e6-ci-tool-todo`
**PR:** https://github.com/microsoft/amplifier-module-tool-todo/pull/3
**Terminal outcome:** **A — RESOLVED.** Every deliverable DONE; the cap did not
bind. Recorded on the item by `work_erratum` rather than `work_resolve` — see
"Claim refused" below.

---

## 1. Deliverables

| Deliverable | State |
|---|---|
| `.github/workflows/ci.yml` running the repo's real suite, ruff pinned, push:main + pull_request, no path filters / error-tolerant step keys / shell failure suppression | **DONE** |
| BOTH run URLs quoted in the PR body; RED job log shows the suite executing with a genuine test failure | **DONE** |
| Scratch PR closed and its branch deleted — verified, not assumed | **DONE** |
| Statement of what the suite actually covers | **DONE** — 10 real tests, not an import smoke (§3) |
| If clean main is red: stop and report, fix as separate named commits | **N/A** — clean main was GREEN on the gate as wired (§5) |
| Draft PR, marked ready when green, NOT merged | **DONE** — #3 ready for review (`isDraft: false`, read back from the remote at 2026-09-07T21:28Z — see incident 3 in §9), 5/5 checks green, not merged |

## 2. What was wired

One file, `+114/-0`, nothing else in the diff (`git diff --stat` against the
merge-base: `1 file changed, 114 insertions(+)`).

Two job definitions → **four checks** on `push: branches:[main]` and
`pull_request: branches:[main]`, with `permissions: contents: read`:

- **Lint (ruff)** — `uvx ruff@0.16.6 check --isolated --select E4,E7,E9,F .`
  Both the tool version **and** the rule set are pinned. `--isolated` so the
  result cannot depend on a `ruff.toml`/`pyproject` discovered anywhere up the
  directory tree; the runner and a laptop run byte-for-byte the same command.
- **Tests (Python 3.11 / 3.12 / 3.13)** — `uv sync --all-extras --dev` then
  `uv run pytest -q`. `requires-python = ">=3.11"`, so this is the floor plus
  the two current minors.

`uv run pytest` picks up `[tool.pytest.ini_options]` from `pyproject.toml`
(`testpaths=["tests"]`, `--import-mode=importlib`, `asyncio_mode=strict`), so CI
and local are the same invocation with the same settings. This repo has **no
Makefile** — removed deliberately in `bb3d15c` — so there is no check target to
mirror.

**Verified absent by grep on the committed file, prose included:** `paths:`,
`paths-ignore:`, `continue-on-error`, `|| true` → **zero matches anywhere in the
file**, not merely zero in executable position.

## 3. What the suite actually covers — 10 real tests, NOT an import smoke

| File | What it is |
|---|---|
| `tests/test_behavioral.py` | inherits `amplifier_core.validation.behavioral.ToolBehaviorTests` |
| `tests/test_validation.py` | inherits `amplifier_core.validation.structural.ToolStructuralTests` |
| `tests/test_description_pin.py` | 2 tests: byte-for-byte pin on the tool description (526 chars) + a guard on the pin's own literal |

**The headline reason this lane matters.** PR #1 (`63f6ef5`) shrank the todo
tool description 6,611 → 6,470 B and landed a byte-for-byte pin to stop it
drifting back. That pin was **committed but executed by nothing** — the repo had
no `.github/workflows` directory at all, so the guard ran only when a human
remembered to run it. It now runs on every push to main and every PR, on three
Pythons. The RED run is the proof it executes: `1 failed, 10 passed`, and one of
those 10 is the pin.

## 4. Red-then-green — the gate

**RED — run `34157370586`**, scratch PR #2, head `c0a2d127`, **4/4 checks red**:
https://github.com/microsoft/amplifier-module-tool-todo/actions/runs/34157370586

```
Tests (Python 3.11) | Run test suite | 1 failed, 10 passed in 0.07s
Tests (Python 3.12) | Run test suite | 1 failed, 10 passed in 0.11s
Tests (Python 3.13) | Run test suite | 1 failed, 10 passed in 0.06s
Lint (ruff)         | Lint           | F401 [*] `os` imported but unused  ->  Found 1 error.
```

The **`10 passed` beside each failure is the load-bearing evidence**: the real
suite collected and executed, and one deliberate assert failed inside it. A
setup, import or lint error would have shown `0 passed` and proved nothing.
Two independent defects were planted so each job failed for its **own** reason:
`tests/test_red_proof.py` (a failing assert) for the Tests job, and
`_red_proof_lint.py` (unused import → F401, inside the pinned rule set, not
collected by pytest because `testpaths=["tests"]`) for the Lint job.

**GREEN — run `34157472320`**, PR #3, workflow-only commit
`fa1f7cb3a4426378e1130855cdfed812b291f7b6`, **4/4 checks green**:
https://github.com/microsoft/amplifier-module-tool-todo/actions/runs/34157472320

```
Tests (Python 3.11) | 10 passed in 0.07s
Tests (Python 3.12) | 10 passed in 0.07s
Tests (Python 3.13) | 10 passed in 0.08s
Lint (ruff)         | All checks passed!
```

Both job logs are committed verbatim beside this note under `evidence/`, as
`*.log.txt`.

> **Transferable finding — evidence that silently does not get committed.**
> These were first written as `evidence/*.log`. This repo's `.gitignore` line 46
> is `*.log`, so `git add docs/lanes/...` matched them, ignored them, and
> **exited 0**; the commit that followed said it carried the logs and carried
> only the note. Nothing errored. Any lane committing CI job logs as evidence
> should either use a non-`.log` extension (done here) or verify with
> `git show --stat HEAD` rather than trusting `git add`'s exit code — the same
> "verify a claim against a value you already know" discipline the publication
> marker demands for pushed branches.

**Scratch cleanup, verified rather than assumed.** PR #2 is `CLOSED`; branch
`ci/red-proof-j1e6` was deleted and then **read back from the remote**:
`git ls-remote --heads origin ci/red-proof-j1e6` → **0 refs**. Trusting the
push's own success message is exactly what a sibling lane found insufficient.

## 5. Clean main was GREEN on the gate as wired — nothing papered over

Measured locally at `63f6ef5` before authoring anything:

- `uv run pytest -q` → **10 passed**
- `uvx ruff@0.16.6 check --isolated --select E4,E7,E9,F .` → **All checks passed!**

So the stop-and-report branch did not trigger. Two things sit **just outside**
the gate; they are disclosed here and in the PR body rather than silently
excluded, and neither is breakage:

1. **ruff's FULL modern default tier** would report **2 findings**, both style
   opinions this repo has never adopted:
   `amplifier_module_tool_todo/__init__.py:10:1 I001` (import block unsorted)
   and `:31:5 PLR1711` (useless `return` at end of function). Adopting either is
   a *source* change and does not belong in the PR that introduces CI.
2. **`ruff format --check`** would reformat **1 file** (that same
   `__init__.py`, purely line-wrapping); 9 files already formatted. Not wired,
   for the same reason — it would collide with any in-flight branch.

## 6. Decisions taken without asking (per the goal's no-waiting rule)

1. **Rule set `E4,E7,E9,F`, not ruff's full defaults.** The breakage tier
   (undefined names, unused imports, syntax errors) is clean today; the full
   default tier is not, and wiring it would make CI red on day one for reasons
   unrelated to correctness. Same choice the four earlier CI lanes made.
2. **`uv sync`, not `uv sync --frozen`.** Installs from the committed `uv.lock`,
   which pins the `amplifier-core` git dependency to an exact commit
   (`f246c6f`). Deliberate: this suite *inherits its behavioral and structural
   tests from amplifier-core*, so a floating `main` would make this repo's CI go
   red for a change made in another repo. Bumping amplifier-core is now a
   lockfile commit here.
3. **No uv cache.** `astral-sh/setup-uv`'s cache keys on `**/uv.lock`; this repo
   *does* commit one, so `enable-cache: true` would have worked here — unlike
   the lockfile-less repos where a sibling lane's first red-proof hard-failed at
   setup before ruff or pytest ever ran. It was still omitted: 16 packages,
   sub-second suite, so the cache buys nothing and only adds a failure mode
   ahead of the tests.
4. **3-Python matrix with `fail-fast: false`.** Knowing whether a break is
   version-specific is the point of the matrix.
5. **`timeout-minutes`** on both jobs (5 / 10). A job stuck at `in_progress`
   reads as "not done yet" rather than "broken" — that is how a false green gets
   merged.

## 7. Spend

**$0.00 against the $0 authority. The cap did not bind.**

Arithmetic as stated in the goal: `0 runs x 0 arms x $0 / 1.00 = $0.00`, slack
`$0.00` — CI minutes only, no API calls, no DTU, no containers. Actual: **2
gating CI runs x 4 checks = 8 jobs**, all sub-two-minute, plus local `uv`/`ruff`
downloads. Nothing registered in the infra ledger; **nothing to tear down**.
No residue question arises — no deliverable here required a purchase.

## 8. Claim refused — and proceeding was correct

`work_claim(project="model_performance", item_id="model_performance-j1e6")` was
**refused**: *"already claimed by agent-spark-1-1101253"*. The item is also
already `resolved`.

This goal's Procedure 1 reads a refused claim as BLOCKED-and-stop. On a
deliberately **one-item / many-lanes** item — the item's own description says
"FILED AS ONE ITEM WITH MANY LANES, not one item per repo" and lists 19 repos —
at most one lane can ever hold it, so a refusal is the **designed steady state**,
not a blocker. Obeying Procedure 1 literally would have filed a `BLOCKED.md` over
a slice that then went on to deliver in full.

What this lane did instead: read the authoritative spec with
`work_list(item_id=...)` — full description and acceptance criteria, no claim, no
mutation, no custody touched — completed every deliverable, and recorded
completion with `work_erratum` (append-only, needs no claim, never rewrites the
stored resolution). `work_resolve` was not an option: against an already-resolved
item it fails on differing text. `work_reopen` was not used: it clears
`closed_at` and moves every throughput roll-up by one item, which is the
manager's call, not a lane's.

**Goal-template defect, reported not absorbed:** either file one item per repo,
or have the per-lane goal say *"claim if free; if a sibling holds it, proceed and
record per-repo completion via `work_erratum`, and let the holder or the manager
resolve once every lane has landed."*

Per the standing convention on this item, this note deliberately carries **no
cross-lane ordinal** — how many lanes have hit this is a whole-item question,
answerable correctly only by the reader of the finished list, and never by a
lane mid-flight.

## 9. Incidents — all three caught by reading a value back, not by an exit code

1. **`gh pr edit --body-file` reported an error and applied nothing.** It failed
   with `GraphQL: Projects (classic) is being deprecated … (repository.pullRequest.projectCards)`
   and PR #3 was left carrying its two-line placeholder body — no run URLs at
   all. Caught by `gh pr view 3 --json body` and re-applied with
   `gh api -X PATCH repos/.../pulls/3 -F body=@…`, then verified a second time:
   the live body now diffs clean against the committed `PR-BODY.md` (one
   GitHub-appended trailing newline). **A sibling lane in this batch hit the
   identical failure**; it is reproducible, not a fluke. A PR body is only as
   good as its read-back, exactly as the publication marker demands for
   branches.
2. **`.gitignore`'s `*.log` silently swallowed the CI evidence** (see §4). Both
   `git add` and `git commit` exited 0 while committing only the note.
3. **This note claimed "ready for review" while the remote still said
   `isDraft: true`.** The rows below and in §1 were written from intent, not
   from a read-back: `gh pr ready 3` had never actually been run against PR #3.
   Nothing errored — there was no failed command to notice, which is precisely
   why it survived. Caught on a later pass by
   `gh pr view 3 --json isDraft` → `true`, then fixed: `gh pr ready 3`
   (`✓ Pull request #3 is marked as "ready for review"`) at
   **2026-09-07T21:28Z**, and verified a second time —
   `gh pr view 3 --json isDraft` → **`false`**.
   **Transferable, and it generalises past PR bodies and pushed branches:** a
   marker/PR *state* claim needs the same read-back discipline the publication
   contract demands for a sha. The failure mode is not a wrong value, it is a
   value nobody ever asked the remote for.

Applied preventively from a sibling lane's finding rather than rediscovered:
the PR body was staged at a **lane-private path inside this repo**
(`docs/lanes/j1e6-ci-tool-todo/PR-BODY.md`), never at a shared `/tmp/pr_body.md`
— a sibling published *another lane's* text that way when two concurrent lanes
wrote the same filename. Checked here: the live body contains **0** occurrences
of any sibling repo's name.

## 10. Final state

| | |
|---|---|
| PR | https://github.com/microsoft/amplifier-module-tool-todo/pull/3 |
| State | **OPEN, ready for review, NOT merged** — `isDraft: false` **read back from the remote** at 2026-09-07T21:28Z, after `gh pr ready 3` was found never to have run (incident 3, §9); `mergeable=MERGEABLE`, `mergeStateStatus=BLOCKED` — review required |
| Branch | `lane/j1e6-ci-tool-todo` |
| Head | the tip of `lane/j1e6-ci-tool-todo`. **The authoritative 40-hex sha is in `DONE.json`'s `publication` block**, read back from the remote *after* the last push — a sha written inside this file could only ever name the commit before the one that contains it |
| Checks | **5/5 pass** — Lint (ruff), Tests 3.11 / 3.12 / 3.13, license/cla. Verified green on every pushed head, not only the workflow-only one |
| Commits | `fa1f7cb` **workflow only** (+114/-0) · `7450414` lane note + evidence · `8e07148` PR body artifact · this note's own updates |

Only `fa1f7cb` touches anything outside `docs/lanes/j1e6-ci-tool-todo/`. The
GREEN run quoted in the PR body is deliberately the one on that workflow-only
commit.

## 11. For whoever merges

1. **Do not expect this lane to have merged it.** PR #3 is *ready for review*,
   4/4 green, deliberately **not merged**.
2. After merging, confirm main HEAD reports a successful check-run:
   `gh api repos/microsoft/amplifier-module-tool-todo/commits/main/check-runs`
   — **configured is not installed.**
3. Optional follow-ups, each a *source* change and each out of scope for a
   workflow PR: `uvx ruff@0.16.6 format .` (1 file), and clearing the two
   full-default findings (I001, PLR1711) in `__init__.py`.
