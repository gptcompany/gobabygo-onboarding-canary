---
description: "Task list for feature 001-normalize-whitespace"
---

# Tasks: normalize_whitespace

**Input**: Design documents from `/specs/001-normalize-whitespace/`

**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required for user stories),
[research.md](./research.md), [contracts/normalize_whitespace.md](./contracts/normalize_whitespace.md)

**Tests**: Included and mandatory. `TDD_MODE: required` per plan.md — tests are written and observed
failing (RED) before any production code exists.

**Organization**: Grouped by user story. The three RED test tasks all target the same file and are
therefore sequential, not parallel.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single project, `src/` layout: `src/gobabygo_text/`, `tests/unit/` at repository root, per
plan.md → Structure Decision.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the package and test scaffolding the repository does not yet have.

- [ ] T001 [P] Add `pyproject.toml` with src-layout packaging and pytest config
  - `[build-system]` with `requires = ["setuptools>=68"]` and `build-backend = "setuptools.build_meta"`.
  - `[project]` with `name = "gobabygo-text"`, `version = "0.1.0"`, `requires-python = ">=3.11"`,
    and an empty `dependencies = []` (no runtime dependencies).
  - `[tool.setuptools.packages.find]` with `where = ["src"]` so the src layout is discovered.
    Do not rely on bare `package-dir` alone; discovery must find `gobabygo_text` under `src/`.
  - `[tool.pytest.ini_options]` with `testpaths = ["tests"]`.
- [ ] T002 Create the `gobabygo_text` package skeleton and `tests/unit/` directory
  - `src/gobabygo_text/__init__.py` does `from gobabygo_text.whitespace import normalize_whitespace`
    and defines `__all__ = ["normalize_whitespace"]`.
  - Do **not** create `src/gobabygo_text/whitespace.py` here — its absence is what makes Phase 3 fail RED.
- [ ] T003 [P] Add `.github/workflows/ci.yml` running pytest with 100% coverage gate
  - Trigger on `push` and `pull_request`; matrix over Python 3.11 and 3.14.
  - Steps: checkout, setup-python, `python -m pip install -e .`, install `pytest` and `pytest-cov`,
    then `python -m pytest -v --cov=gobabygo_text --cov-report=term-missing --cov-fail-under=100`.

**Checkpoint**: `python3 -m pip install -e .` succeeds; `python3 -c "import gobabygo_text"` fails
with `ModuleNotFoundError: gobabygo_text.whitespace`, which is the expected pre-RED state.

---

## Phase 2: Foundational (Blocking Prerequisites)

Not applicable. The feature is a single pure function with no shared infrastructure, no database, no
authentication, no routing, and no configuration. Phase 1 is the only prerequisite for the user
stories.

---

## Phase 3: User Story 1 - Collapse and strip a messy string (Priority: P1) 🎯 MVP

**Goal**: A caller gets a canonical single-line string with interior whitespace runs collapsed to
one space and both ends stripped.

**Independent test**: `normalize_whitespace("  hello \t\n  world  ") == "hello world"`.

- [ ] T004 [US1] Write RED tests for collapsing and stripping ASCII whitespace
  - In `tests/unit/test_whitespace.py`, cover US1 acceptance scenarios 1-5 from spec.md.
  - Cover the plan.md edge cases: mixed runs `"\t \n\r"` collapse to one space; a lone `"\t"`
    between words becomes `" "`; leading/trailing runs are removed entirely, not collapsed to one space.
  - Parametrize over all six ASCII whitespace characters from FR-003, each as an interior run
    and at a string end (SC-002).
  - Assert purity per FR-011: the input string object is unchanged after the call, and the function
    is idempotent (`normalize_whitespace(normalize_whitespace(s)) == normalize_whitespace(s)`).
  - Run `python3 -m pytest tests/unit/test_whitespace.py -v` and record the failing output as RED evidence.

---

## Phase 4: User Story 2 - Reject non-string input loudly (Priority: P1)

**Goal**: Non-`str` input raises `TypeError` naming the received type, with no coercion.

**Independent test**: `pytest.raises(TypeError)` around `normalize_whitespace(None)`.

- [ ] T005 [US2] Write RED tests for TypeError on non-string input
  - Cover US2 acceptance scenarios 1-5 in the same file: `None`, `42`, `b"hello"` and `True`
    each raise `TypeError` (SC-004).
  - Assert the raised message contains `type(value).__name__` for each case (FR-007).
  - Assert explicitly that `bytes` is not decoded and `bool` is not accepted.
  - Run the suite and record the RED output.

---

## Phase 5: User Story 3 - Leave non-ASCII whitespace untouched (Priority: P2)

**Goal**: U+00A0 and U+3000 are content, preserved verbatim in position and count.

**Independent test**: `normalize_whitespace("a\xa0b") == "a\xa0b"`.

- [ ] T006 [US3] Write RED tests for non-ASCII whitespace preservation
  - Cover US3 acceptance scenarios 1-4 (SC-003): `"a\xa0b"`, `"\xa0a\xa0"`, `"a \xa0 b"`
    and `"a\u3000\u3000b"` each round trip unchanged.
  - Write these characters as `\xa0` / `\u3000` escapes, never as literal glyphs, so no encoding
    step can corrupt the assertion.
  - Add a `str` subclass case (FR-008) asserting the result equals the normalized text and
    `type(result) is str`.
  - Run the suite and record the RED output.

**Checkpoint**: All of T004, T005 and T006 fail. This combined failing run is the mandatory RED
evidence for `TDD_MODE: required` and must be captured before Phase 6 begins.

---

## Phase 6: Implementation (GREEN)

**Goal**: The minimum production code that turns the whole RED suite green.

- [ ] T007 Implement `normalize_whitespace` in `src/gobabygo_text/whitespace.py` (GREEN)
  - Implement exactly as specified in `contracts/normalize_whitespace.md`.
  - Module level: `_ASCII_WHITESPACE = " \t\n\r\v\f"` and
    `_ASCII_WHITESPACE_RUN = re.compile(r"[ \t\n\r\v\f]+")`.
  - Guard with `isinstance(value, str)`, raising `TypeError` whose message includes `type(value).__name__`.
  - Return `_ASCII_WHITESPACE_RUN.sub(" ", value).strip(_ASCII_WHITESPACE)`.
  - The forbidden implementations in the contract (`" ".join(value.split())`, `\s` without `re.ASCII`,
    any bare `.strip()`) MUST NOT be used.
  - Include a docstring stating the six ASCII whitespace characters and the non-ASCII preservation guarantee.
  - Make no other change; run `python3 -m pytest tests/unit/test_whitespace.py -v` and record GREEN output.

**Checkpoint**: Full suite green. No refactoring beyond this point unless the suite stays green.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T008 Add a linear-time performance assertion for a 1,000,000-character input
  - In `tests/unit/test_whitespace.py`, build a 1,000,000-character whitespace-heavy input (SC-006).
  - Assert both the exact expected result and that the call completes in under one second,
    measured with `time.perf_counter`.
- [ ] T009 Verify 100% line coverage of `src/gobabygo_text/`
  - Run `python3 -m pytest --cov=gobabygo_text --cov-report=term-missing --cov-fail-under=100`
    and confirm SC-005 is met.
- [ ] T010 [P] Document `normalize_whitespace` usage in `README.md`
  - Add a short usage section linking to `specs/001-normalize-whitespace/quickstart.md`.
  - Include the U+00A0 preservation caveat so callers are not surprised.

---

## Dependencies

```text
T001 ──┐
T003 ──┤ (both [P], independent files)
T002 ──┴──> T004 ──> T005 ──> T006 ──> T007 ──> T008 ──> T009
                                          └────────────> T010 [P]
```

- T001 and T003 are parallel: `pyproject.toml` and `.github/workflows/ci.yml` are different files.
- T004, T005 and T006 all edit `tests/unit/test_whitespace.py`, so they are strictly sequential.
- T007 must not start until the combined RED evidence from T004–T006 exists.
- T010 touches only `README.md` and can run in parallel with T008/T009.

## Allowed files for implementation

The implementation writer may create or modify only these paths:

```text
pyproject.toml
src/gobabygo_text/__init__.py
src/gobabygo_text/whitespace.py
tests/unit/test_whitespace.py
.github/workflows/ci.yml
README.md
```

Anything under `specs/`, `.specify/`, `.claude/`, `.agents/` or `.github/workflows/speckit-ledger.yml`
is out of bounds for the writer.

## Done criteria

- All of T001–T010 checked off in this file.
- `python3 -m pytest -v` green, with RED-before-GREEN evidence captured for T004–T007.
- 100% line coverage of `src/gobabygo_text/` (SC-005).
- CI green on the implementation pull request (SC-007).
- An independent read-only review returns `REVIEW_VERDICT: PASS` with no unresolved
  high- or medium-severity finding.
