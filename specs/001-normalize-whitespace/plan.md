# Implementation Plan: normalize_whitespace

**Branch**: `001-normalize-whitespace` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-normalize-whitespace/spec.md`

## Summary

Add one pure function, `normalize_whitespace(value: str) -> str`, that collapses every maximal run
of the six ASCII whitespace characters into a single U+0020 space and strips ASCII whitespace from
both ends, while raising `TypeError` for any non-`str` input and preserving all non-ASCII
characters (including non-ASCII whitespace) verbatim.

The technical approach is a single precompiled `re` pattern over an explicit ASCII whitespace
character class, applied with `re.sub`, followed by `strip` over that same explicit character set.
The repository currently has no source package, so this feature also introduces the minimal
`src/`-layout package and `pytest` scaffolding it needs.

## Technical Context

**Language/Version**: Python 3.11+ (developed and verified on the installed CPython 3.14.4)

**Primary Dependencies**: None at runtime. Standard library `re` only. `pytest` for tests.

**Storage**: N/A — the function is pure and stateless.

**Testing**: `pytest` (9.0.2 installed), run as `python3 -m pytest`

**Target Platform**: Any platform with CPython 3.11+; CI runs on `ubuntu-latest`.

**Project Type**: Single Python library package.

**Performance Goals**: Linear in input length. A 1,000,000-character input normalizes in well under
one second (SC-006).

**Constraints**: No runtime third-party dependencies. No I/O, logging, global state, or network
access. Public API surface is exactly one function.

**Scale/Scope**: One source module (~20 lines), one test module, one package `__init__`, one
`pyproject.toml`, one CI workflow. Non-production, disposable canary scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The repository constitution at `.specify/memory/constitution.md` is still the unfilled upstream
template: every principle is a `[PRINCIPLE_N_NAME]` placeholder and the version and ratification
dates are unset. There are therefore no ratified project principles to gate against, and no
constitutional violation can be asserted or waived.

Ratifying a constitution is deliberately out of scope for this feature: this is a disposable
onboarding canary, and authoring binding project-wide governance from inside a one-function change
would be a far larger and less reversible decision than the feature itself. This is recorded as a
known gap rather than silently passed.

In place of ratified gates, the plan is held to the commonly assumed defaults, all of which it
satisfies:

| Default gate | Status | Evidence |
|---|---|---|
| Library-first, self-contained | PASS | One package, no runtime dependencies, no framework coupling |
| Test-first (RED before GREEN) | PASS | T004 writes failing tests before T005 implements; see TDD policy below |
| Simplicity / YAGNI | PASS | One function, no options, no configuration surface |
| Observability | N/A | A pure function with no side effects has nothing to log |
| Versioning | N/A | Not published to any index |

**Post-design re-check**: The Phase 1 design adds no new dependency, no new public symbol beyond
`normalize_whitespace`, and no configuration. The gate table above is unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/001-normalize-whitespace/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── normalize_whitespace.md   # Function contract
├── tasks.md             # Phase 2 output (/speckit-tasks)
└── github-ledger.json   # Derived GitHub work-ledger binding
```

No `data-model.md` is produced: the feature introduces no entity, schema, or persistent data.

### Source Code (repository root)

```text
pyproject.toml                       # Package metadata + pytest configuration
src/
└── gobabygo_text/
    ├── __init__.py                  # Re-exports normalize_whitespace
    └── whitespace.py                # normalize_whitespace implementation
tests/
└── unit/
    └── test_whitespace.py           # Full acceptance coverage for US1, US2, US3
.github/
└── workflows/
    ├── speckit-ledger.yml           # Managed Spec Kit ledger caller (planning branch)
    └── ci.yml                       # pytest + coverage on push and pull_request
```

**Structure Decision**: Single-project `src/` layout. The package is named `gobabygo_text` and the
module `whitespace.py`; the public import path is `from gobabygo_text import normalize_whitespace`.
The `src/` layout is chosen over a flat top-level package so that tests exercise the installed
package rather than accidentally importing from the working directory, which keeps the packaging
honest at essentially zero cost.

## Phase 0: Research

See [research.md](./research.md). The decisive finding: Python's default `str.split()` and
`str.strip()` are Unicode-aware and treat U+00A0 and U+3000 as whitespace, so the idiomatic
one-liner `" ".join(value.split())` **violates FR-009**. The implementation must use an explicit
ASCII-only character class.

## Phase 1: Design

**Contract**: see [contracts/normalize_whitespace.md](./contracts/normalize_whitespace.md).

**Usage**: see [quickstart.md](./quickstart.md).

### Chosen implementation shape

```text
_ASCII_WHITESPACE = " \t\n\r\v\f"                  # exactly the six chars of FR-003
_ASCII_WHITESPACE_RUN = re.compile(r"[ \t\n\r\v\f]+")

def normalize_whitespace(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError(...)                        # message names type(value).__name__
    return _ASCII_WHITESPACE_RUN.sub(" ", value).strip(_ASCII_WHITESPACE)
```

Ordering note: substituting first and stripping second is correct and is the required order. Every
leading or trailing run has already become exactly one space by the time `strip` runs, so
`strip(_ASCII_WHITESPACE)` removes at most one character from each end. Stripping first would also
work but would leave the reader to re-derive the argument; substitute-then-strip keeps the explicit
character set used in both steps.

`strip` MUST be called with the explicit `_ASCII_WHITESPACE` argument. Bare `value.strip()` is
Unicode-aware and would remove a leading U+00A0, violating FR-009 acceptance scenario 2.

Regex alternatives considered and rejected: `re.ASCII` (`\s` with the `re.ASCII` flag matches
exactly the six characters, but relies on a flag interaction a reader must verify, whereas the
literal class is self-evident) and `str.translate` plus manual run-collapsing (more code, no
benefit).

### Milestones and dependency order

| # | Milestone | Depends on | Delivers |
|---|---|---|---|
| M0 | Packaging scaffold | — | `pyproject.toml`, `src/gobabygo_text/__init__.py`, `tests/` tree |
| M1 | RED tests | M0 | `tests/unit/test_whitespace.py`, failing (import error or assertion) |
| M2 | GREEN implementation | M1 | `src/gobabygo_text/whitespace.py`, full suite green |
| M3 | CI | M0 | `.github/workflows/ci.yml` running pytest with coverage |
| M4 | Independent review | M2, M3 | Read-only Codex review over a frozen commit range |

### Risk controls

| Risk | Control |
|---|---|
| Naive `" ".join(value.split())` silently breaks FR-009 | Explicitly forbidden in spec Clarifications, in the contract, and in the writer's delegation brief; covered by US3 tests that fail loudly |
| Bare `.strip()` silently breaks FR-009 scenario 2 | US3 acceptance scenario 2 asserts a preserved leading U+00A0 |
| `bool` accepted because `isinstance(True, int)` | `isinstance(value, str)` is the only check; US2 scenario 4 covers `True` |
| Non-ASCII test characters mangled by tooling or terminals | Tests use explicit ` ` / `　` escapes, never literal glyphs, so the assertion cannot be corrupted by copy-paste or encoding |
| Writer edits files outside the allowlist | Delegation brief pins an exact allowed-file list; coordinator diffs the worktree against it before review |
| Reviewer mutates the tree | Reviewer brief is explicitly read-only; coordinator re-checks HEAD, `git status`, and the diff checksum after review |

### Rollback considerations

The feature is additive: it creates new files and modifies no existing source. Rollback is
`git revert` of the implementation merge commit, or deletion of `src/gobabygo_text/`,
`tests/unit/test_whitespace.py` and `pyproject.toml`. Nothing imports the function yet, so no caller
breaks. No data migration, no deployment, and no external service is involved, so rollback carries
no residual state.

## TDD policy for this feature

`TDD_MODE: required`. The feature is behavior-defining pure logic with an installed pytest harness,
so a focused automated test is entirely feasible. Observable RED evidence is required before any
production code is written: the writer must run `python3 -m pytest tests/unit/test_whitespace.py -v`
and capture the failure before creating `src/gobabygo_text/whitespace.py`. The exact test command is:

```text
python3 -m pytest tests/unit/test_whitespace.py -v
```

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

No violations. The Constitution Check gate table records one deliberate, disclosed gap (the
constitution itself is an unratified template), not a violation of a ratified principle.
