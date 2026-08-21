# Feature Specification: normalize_whitespace

**Feature Branch**: `001-normalize-whitespace`

**Created**: 2026-08-21

**Status**: Ready for Planning

**Input**: User description: "add normalize_whitespace(value: str) -> str, collapsing runs of ASCII whitespace to one space and stripping both ends; raise TypeError for non-string input"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Collapse and strip a messy string (Priority: P1)

A developer receives text from an untrusted source (form field, scraped page, CSV cell) where
indentation, line breaks and repeated spaces are meaningless noise. They call a single helper and
get back a canonical single-line string whose internal whitespace runs are exactly one space and
whose ends carry no whitespace at all.

**Why this priority**: This is the entire value of the feature. Without it there is nothing to ship.

**Independent Test**: Call `normalize_whitespace("  hello \t\n  world  ")` and assert the result is
exactly `"hello world"`. Delivers the canonical-text value on its own.

**Acceptance Scenarios**:

1. **Given** the string `"  hello \t\n  world  "`, **When** `normalize_whitespace` is called,
   **Then** it returns `"hello world"`.
2. **Given** a string with no whitespace at all such as `"hello"`, **When** it is called,
   **Then** it returns `"hello"` unchanged.
3. **Given** the empty string `""`, **When** it is called, **Then** it returns `""`.
4. **Given** a string consisting only of ASCII whitespace such as `" \t\r\n\v\f "`, **When** it is
   called, **Then** it returns `""`.
5. **Given** a string whose only whitespace is a single interior space such as `"a b"`, **When** it
   is called, **Then** it returns `"a b"` unchanged.

---

### User Story 2 - Reject non-string input loudly (Priority: P1)

A developer accidentally passes a non-string (None, an int, a bytes object, a list). Instead of a
silent coercion or a confusing downstream failure, they get an immediate, explicit `TypeError`
naming the offending type, so the bug is located at the call site.

**Why this priority**: The contract explicitly requires it, and silent coercion of `None` or bytes
is the most likely real-world misuse. It is required for a correct MVP.

**Independent Test**: Call `normalize_whitespace(None)` inside `pytest.raises(TypeError)` and assert
the message names the received type. Testable with no other part of the feature.

**Acceptance Scenarios**:

1. **Given** the input `None`, **When** `normalize_whitespace` is called, **Then** it raises
   `TypeError` and does not return a value.
2. **Given** the input `42`, **When** it is called, **Then** it raises `TypeError`.
3. **Given** the input `b"hello"` (bytes), **When** it is called, **Then** it raises `TypeError`
   rather than decoding or stringifying it.
4. **Given** the input `True` (a `bool`, which is an `int` subclass), **When** it is called,
   **Then** it raises `TypeError`.
5. **Given** any rejected input, **When** the `TypeError` is inspected, **Then** its message
   contains the actual type name that was received.

---

### User Story 3 - Leave non-ASCII whitespace untouched (Priority: P2)

A developer processes internationalized text containing a non-breaking space (U+00A0) or an
ideographic space (U+3000) that is semantically part of the content. The helper must treat those as
ordinary characters and preserve them verbatim, because the contract is scoped to ASCII whitespace.

**Why this priority**: It is the boundary that makes the contract unambiguous and is the most likely
place for a naive implementation to be silently wrong. It is not required for the very first happy
path, hence P2 rather than P1.

**Independent Test**: Call `normalize_whitespace("a b")` and assert the result is exactly
`"a b"`, with the U+00A0 still present.

**Acceptance Scenarios**:

1. **Given** the string `"a b"`, **When** it is called, **Then** it returns `"a b"`
   unchanged; the non-breaking space is neither collapsed nor converted to a plain space.
2. **Given** the string `" a "`, **When** it is called, **Then** it returns
   `" a "`; non-ASCII whitespace is not stripped from the ends.
3. **Given** the string `"a   b"` (space, U+00A0, space), **When** it is called, **Then** it
   returns `"a   b"`: each ASCII run of length one stays one space and the U+00A0 survives.
4. **Given** the string `"a　　b"` (two ideographic spaces), **When** it is called,
   **Then** it returns `"a　　b"` unchanged.

---

### Edge Cases

- **Whitespace-only input** of any length collapses to the empty string, not to a single space.
- **A single ASCII whitespace character that is not a space** (for example a lone `"\t"` between two
  words) is normalized to one `" "`, not left as a tab.
- **Mixed runs** such as `"\t \n\r"` between words collapse to exactly one space regardless of run
  length or composition.
- **Leading and trailing runs** are removed entirely rather than collapsed to one space.
- **`str` subclasses** (for example an `enum.StrEnum` member or a user subclass of `str`) are
  accepted as strings; the return value is a plain `str`.
- **Very long input** must not require recursion or quadratic string concatenation.
- **Immutability**: the input object is never mutated; a new string is returned. Returning the same
  object when nothing changes is acceptable, since Python strings are immutable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a callable named `normalize_whitespace` that accepts one
  positional argument `value` and returns a `str`.
- **FR-002**: The system MUST replace every maximal run of one or more ASCII whitespace characters
  inside the value with exactly one U+0020 space character.
- **FR-003**: The system MUST define "ASCII whitespace" as exactly these six characters: space
  (U+0020), horizontal tab (U+0009), line feed (U+000A), carriage return (U+000D), vertical tab
  (U+000B), and form feed (U+000C). No other character may be treated as whitespace.
- **FR-004**: The system MUST remove all leading and trailing ASCII whitespace from the result, so
  the returned string neither begins nor ends with an ASCII whitespace character.
- **FR-005**: The system MUST return the empty string when the input is empty or consists solely of
  ASCII whitespace.
- **FR-006**: The system MUST raise `TypeError` when `value` is not an instance of `str`, and MUST
  NOT coerce, stringify, or decode the input.
- **FR-007**: The `TypeError` message MUST include the type name of the argument that was actually
  received, so the caller can identify the mistake without a debugger.
- **FR-008**: The system MUST accept instances of `str` subclasses as valid input and MUST return a
  value that is exactly equal to the specified normalization of their text.
- **FR-009**: The system MUST preserve every non-ASCII character verbatim, including non-ASCII
  whitespace such as U+00A0 and U+3000, which MUST NOT be collapsed, stripped, or converted.
- **FR-010**: The callable MUST be importable from a stable public path documented in the plan, and
  MUST carry a type annotation of `(value: str) -> str`.
- **FR-011**: The system MUST NOT mutate its input and MUST have no side effects: no I/O, no
  logging, no global state, no network access.

### Key Entities

Not applicable. The feature is a single pure function over strings and introduces no persistent
data, schema, or entity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the acceptance scenarios in User Stories 1, 2 and 3 pass as automated tests.
- **SC-002**: Every one of the six ASCII whitespace characters listed in FR-003 is exercised by at
  least one automated test, both as an interior run and at a string end.
- **SC-003**: At least two distinct non-ASCII whitespace characters (U+00A0 and U+3000) are covered
  by automated tests asserting exact preservation.
- **SC-004**: At least four distinct non-string input types (`None`, `int`, `bytes`, `bool`) each
  have an automated test asserting `TypeError`.
- **SC-005**: Line coverage of the new source module is 100%, measured by the project's test runner.
- **SC-006**: A caller can normalize a 1,000,000-character string in well under one second on
  ordinary developer hardware, demonstrating no quadratic behavior.
- **SC-007**: The full automated test suite passes in CI on the pull request before merge.

## Clarifications

Resolved during specification; no open `[NEEDS CLARIFICATION]` markers remain.

- **Q: Which characters count as whitespace?** A: Exactly the six ASCII whitespace characters in
  FR-003. This is deliberately narrower than Python's Unicode-aware `str.split()` and `str.strip()`
  defaults, which also treat U+00A0, U+3000 and other Unicode separators as whitespace. An
  implementation built on the bare `" ".join(value.split())` idiom therefore does **not** satisfy
  FR-009 and must not be used.
- **Q: Should `bool` be accepted since `True` is int-like?** A: No. Only `str` instances are
  accepted; `bool` raises `TypeError` like any other non-string.
- **Q: Should `str` subclasses be accepted?** A: Yes, via an `isinstance` check rather than an exact
  `type(...) is str` check.
- **Q: Is a keyword call such as `normalize_whitespace(value="x")` supported?** A: Yes. The
  parameter is named `value` and is a normal positional-or-keyword parameter.
- **Q: What is the scope of this feature?** A: One pure function plus its tests and packaging. It is
  explicitly non-production and disposable.

## Assumptions

- The repository is a Python project targeting a currently supported CPython 3.x runtime; the exact
  minimum version is a planning decision, not a specification decision.
- The consumer is other Python code in this repository; no CLI, HTTP endpoint, or user interface is
  required.
- The repository currently contains no source package, so this feature also establishes the minimal
  package and test scaffolding it needs.

## Out of Scope

- Unicode-aware normalization (NFC/NFKC), casefolding, accent stripping, or any other text
  transformation beyond ASCII whitespace collapsing and stripping.
- Collapsing or stripping non-ASCII whitespace, or any configuration flag to opt into doing so.
- Preserving newlines as paragraph breaks, or any multi-line-aware behavior.
- A configurable replacement character, a configurable whitespace class, or a `max_length` argument.
- Operating on `bytes`, file objects, iterables of strings, or containers of strings.
- Performance optimization beyond avoiding pathological (quadratic or recursive) behavior.
- Publishing the package to any index, deploying anything, or changing any external service.
