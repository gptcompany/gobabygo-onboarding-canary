# Cross-Artifact Analysis: 001-normalize-whitespace

**Date**: 2026-08-21 | **Phase**: `speckit.analyze` | **Scope**: `spec.md`, `plan.md`, `tasks.md`,
`research.md`, `contracts/normalize_whitespace.md`

**Coverage note (degraded)**: the canonical workflow assigns this step to a Codex worker. The Codex
session `codex-gobabygo-onboarding-canary` is blocked on a startup update prompt (see the report to
the operator), so this analysis was performed by the coordinator acting as lead. It is therefore a
same-model self-analysis, **not** an independent model-diverse challenge. This is recorded as
degraded planning-review coverage rather than presented as a Codex challenge that did not occur.

## Requirement → task traceability

| Requirement | Covered by | Status |
|---|---|---|
| FR-001 callable, one arg, returns `str` | T002 (export), T007 (definition) | OK |
| FR-002 collapse runs to one space | T004 (tests), T007 (impl) | OK |
| FR-003 exactly six ASCII whitespace chars | T004 (parametrized over all six), T007 | OK |
| FR-004 strip both ends | T004, T007 | OK |
| FR-005 empty / whitespace-only → `""` | T004, T007 | OK |
| FR-006 `TypeError` on non-`str`, no coercion | T005, T007 | OK |
| FR-007 message names received type | T005, T007 | OK |
| FR-008 `str` subclasses accepted | T006 (subclass case), T007 | OK |
| FR-009 non-ASCII preserved verbatim | T006, T007, contract "forbidden implementations" | OK |
| FR-010 stable import path + annotation | T002 (`__init__` re-export), T007 (annotation) | OK |
| FR-011 no mutation, no side effects | T004 (purity + idempotence assertions) | OK — *added by this analysis* |

| Success criterion | Covered by | Status |
|---|---|---|
| SC-001 all acceptance scenarios automated | T004, T005, T006 | OK |
| SC-002 all six ASCII chars, interior and at ends | T004 | OK |
| SC-003 two non-ASCII whitespace chars | T006 | OK |
| SC-004 four non-string input types | T005 | OK |
| SC-005 100% line coverage | T009, enforced by T003 `--cov-fail-under=100` | OK |
| SC-006 1,000,000 chars under one second | T008 | OK |
| SC-007 CI green before merge | T003 + implementation PR gate | OK |

| User story | Task | Independently testable |
|---|---|---|
| US1 (P1) collapse and strip | T004 | Yes |
| US2 (P1) reject non-string | T005 | Yes |
| US3 (P2) preserve non-ASCII | T006 | Yes |

No requirement, success criterion, or user story is left without a task, and no task exists that
does not trace back to at least one of them.

## Findings

Two issues were found and both were fixed in `tasks.md` before publication.

### F-001 (Medium, FIXED) — `pyproject.toml` instructions would not produce an importable package

**Evidence**: T001 originally specified only `[tool.setuptools] package-dir = {"" = "src"}`. With a
`src/` layout, setuptools also needs a discovery directive; without
`[tool.setuptools.packages.find] where = ["src"]` the build can fail to find `gobabygo_text`, and
`pip install -e .` then yields a package that does not import. That would have broken the Phase 1
checkpoint, the RED evidence in T004–T006, and CI, all at once.

**Resolution**: T001 now specifies `[build-system]`, `[project]` (name, version, `requires-python`,
empty `dependencies`), `[tool.setuptools.packages.find] where = ["src"]`, and
`[tool.pytest.ini_options]`.

### F-002 (Low, FIXED) — FR-011 had no observable assertion

**Evidence**: FR-011 requires no mutation and no side effects, but no task asserted it. Immutability
of `str` makes mutation impossible in practice, so the risk was low, but "covered by the language"
is not the same as "covered by a test", and the requirement would have shipped untraced.

**Resolution**: T004 now asserts that the input object is unchanged after the call and that the
function is idempotent. Absence of I/O, logging and global state remains verified structurally by
review of a short pure function rather than by a test, which is proportionate.

### Observations carried forward, not defects

- **Constitution is an unratified template.** Every principle in `.specify/memory/constitution.md`
  is still a placeholder. `plan.md` → Constitution Check discloses this and gates against commonly
  assumed defaults instead. Ratifying a constitution from inside a one-function change is
  deliberately out of scope; recorded as a known gap.
- **T004, T005 and T006 share one file** and are correctly marked sequential rather than `[P]`.
  The dependency graph in `tasks.md` matches.
- **`.github/workflows/speckit-ledger.yml` is excluded from the writer allowlist** in `tasks.md`,
  which is correct: it is coordinator-owned planning-plane content, not implementation.

## Consistency checks performed

| Check | Result |
|---|---|
| Package name identical across plan, contract, quickstart, tasks (`gobabygo_text`) | Consistent |
| Public import path identical across contract, quickstart, T002 | Consistent |
| Test command identical in plan TDD policy, T004–T007, quickstart | Consistent |
| Python version: plan `>=3.11`, T001 `requires-python`, T003 matrix `3.11` + `3.14` | Consistent |
| Six ASCII whitespace characters enumerated identically in spec FR-003, contract, plan, T007 | Consistent |
| Forbidden implementations listed identically in spec Clarifications, research D1/D2, contract | Consistent |
| Coverage target: SC-005 100%, T009 command, T003 `--cov-fail-under=100` | Consistent |
| Open `[NEEDS CLARIFICATION]` markers in `spec.md` | None |
| Tasks parsed by the ledger planner | 10 of 10, `blocking: []` |

## Verdict

Planning artifacts are internally consistent and complete after F-001 and F-002 were fixed. The
feature is ready for ledger publication and implementation, subject to the degraded planning-review
coverage disclosed at the top of this document.
