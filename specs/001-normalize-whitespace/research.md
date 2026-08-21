# Phase 0 Research: normalize_whitespace

**Feature**: `001-normalize-whitespace` | **Date**: 2026-08-21

All findings below were verified by execution on the installed interpreter (CPython 3.14.4), not
recalled from memory. The verification transcript is reproduced under each decision.

## Decision 1: Do not use `" ".join(value.split())`

**Decision**: Rejected. The implementation MUST NOT use the bare split/join idiom.

**Rationale**: `str.split()` with no argument splits on *Unicode* whitespace, which includes
U+00A0 NO-BREAK SPACE and U+3000 IDEOGRAPHIC SPACE. Using it silently rewrites non-ASCII whitespace
into an ASCII space, directly violating FR-009.

**Evidence**:

```text
>>> " ".join("a\xa0b".split())
'a b'                       # WRONG: U+00A0 was replaced by U+0020
>>> "\xa0a\xa0".strip()
'a'                         # WRONG: U+00A0 was stripped from both ends
>>> "\xa0".isspace()
True                        # U+00A0 is Unicode whitespace
>>> "　".isspace()
True                        # U+3000 is Unicode whitespace
```

**Alternatives considered**: None viable. Every whitespace helper in the standard library that
takes no explicit character set (`split`, `strip`, `lstrip`, `rstrip`, `\s` without `re.ASCII`) is
Unicode-aware and fails the same way.

## Decision 2: Use an explicit ASCII whitespace character class in `re`

**Decision**: Use `re.compile(r"[ \t\n\r\v\f]+")` and `str.strip(" \t\n\r\v\f")`.

**Rationale**: The literal class enumerates exactly the six characters named in FR-003, so the code
states the contract rather than depending on a library's whitespace definition. It is
self-evidently correct to a reader with no need to look anything up.

**Evidence**:

```text
>>> re.match(r"\s", "\xa0")               # Unicode default
<re.Match object; span=(0, 1), match='\xa0'>        # matches: unsuitable
>>> re.match(r"\s", "\xa0", re.ASCII)
None                                                 # does not match
>>> re.match(r"[ \t\n\r\v\f]", "\xa0")
None                                                 # does not match
```

**Alternatives considered**:

- **`\s` with the `re.ASCII` flag**: functionally correct (shown above: it does not match U+00A0),
  but it makes correctness depend on a flag whose scope a reader must verify, and the flag is easy
  to drop in a later edit without any test noticing at the pattern level. The literal class carries
  its own proof. Rejected on legibility, not on behavior.
- **`str.translate` plus a manual run-collapsing loop**: more code, a mutable accumulator, and no
  behavioral advantage. Rejected on simplicity (YAGNI).
- **`textwrap.dedent` / `shlex`**: solve unrelated problems. Rejected as not applicable.

## Decision 3: Substitute first, then strip with the explicit set

**Decision**: `_RUN.sub(" ", value).strip(_ASCII_WHITESPACE)`.

**Rationale**: After the substitution, any leading or trailing whitespace run is exactly one space,
so `strip` removes at most one character from each end. Passing the explicit `_ASCII_WHITESPACE`
argument (rather than calling bare `.strip()`) is what keeps a leading U+00A0 intact.

**Evidence** (reference implementation run over every acceptance scenario in spec.md):

```text
'  hello \t\n  world  '  -> 'hello world'      # US1.1
'hello'                  -> 'hello'            # US1.2
''                       -> ''                 # US1.3
' \t\r\n\x0b\x0c '       -> ''                 # US1.4
'a b'                    -> 'a b'              # US1.5
'a\xa0b'                 -> 'a\xa0b'           # US3.1 preserved
'\xa0a\xa0'              -> '\xa0a\xa0'        # US3.2 preserved at both ends
'a \xa0 b'               -> 'a \xa0 b'         # US3.3 preserved between spaces
'a　　b'         -> 'a　　b'   # US3.4 preserved
```

**Alternatives considered**: Strip-then-substitute produces identical output but requires the
reader to re-derive why the strip argument matters before the runs have been normalized. Rejected
on legibility only; either order is behaviorally acceptable.

## Decision 4: `isinstance(value, str)` for the type guard

**Decision**: Guard with `if not isinstance(value, str): raise TypeError(...)`.

**Rationale**: `isinstance` accepts `str` subclasses as required by FR-008 while rejecting `bool`,
`int`, `bytes` and `None` as required by FR-006. `type(value) is str` would wrongly reject a
`StrEnum` member. A duck-typed `hasattr(value, "strip")` check would wrongly accept `bytes`, which
has a `strip` method.

**Evidence**:

```text
None    -> TypeError: normalize_whitespace() expected str, got NoneType
42      -> TypeError: normalize_whitespace() expected str, got int
b'hello'-> TypeError: normalize_whitespace() expected str, got bytes
True    -> TypeError: normalize_whitespace() expected str, got bool
```

Note that `True` is reported as `bool`, satisfying FR-007's requirement that the message name the
type actually received.

## Decision 5: Performance characteristics

**Decision**: No optimization work is needed; a single precompiled `re.sub` pass is linear.

**Rationale**: `re.sub` scans the input once and builds the result with an internal buffer, so
there is no quadratic concatenation and no recursion. SC-006 (1,000,000 characters in well under a
second) is satisfied with a wide margin. This is asserted here as a design expectation and is
verified as an actual measured assertion in task T009.

**Alternatives considered**: Chunked or streaming processing. Rejected as premature; the contract
takes a single in-memory `str`, which is already fully materialized.

## Open questions

None. All specification clarifications were resolved before planning.
