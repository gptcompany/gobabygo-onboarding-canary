# Contract: `normalize_whitespace`

**Feature**: `001-normalize-whitespace`

**Public import path**: `from gobabygo_text import normalize_whitespace`

**Defining module**: `src/gobabygo_text/whitespace.py`

## Signature

```python
def normalize_whitespace(value: str) -> str: ...
```

`value` is a normal positional-or-keyword parameter, so both `normalize_whitespace("x")` and
`normalize_whitespace(value="x")` are supported.

## Definitions

**ASCII whitespace** means exactly these six characters and no others:

| Character | Escape | Code point |
|---|---|---|
| space | `" "` | U+0020 |
| horizontal tab | `"\t"` | U+0009 |
| line feed | `"\n"` | U+000A |
| carriage return | `"\r"` | U+000D |
| vertical tab | `"\v"` | U+000B |
| form feed | `"\f"` | U+000C |

Every other character, including U+00A0 NO-BREAK SPACE and U+3000 IDEOGRAPHIC SPACE, is **not**
whitespace for the purposes of this contract and is ordinary content.

## Preconditions

- `value` is an instance of `str` (subclasses of `str` are accepted).

## Postconditions

On success the returned value is a `str` such that:

1. Every maximal run of one or more ASCII whitespace characters in `value` that is neither leading
   nor trailing appears in the result as exactly one U+0020 space.
2. The result does not begin or end with an ASCII whitespace character.
3. All non-ASCII-whitespace characters appear in the result in their original order, unchanged.
4. `value` itself is not mutated and no side effect occurs.

## Errors

| Condition | Raised | Message requirement |
|---|---|---|
| `value` is not an instance of `str` | `TypeError` | Must contain `type(value).__name__` |

No other exception is raised for any `str` input.

## Reference behavior table

These are the normative examples. Escapes are written explicitly; the tests must use escapes rather
than literal glyphs so no encoding or copy-paste step can corrupt them.

| Input | Output | Covers |
|---|---|---|
| `"  hello \t\n  world  "` | `"hello world"` | FR-002, FR-004 |
| `"hello"` | `"hello"` | FR-002 (no-op) |
| `""` | `""` | FR-005 |
| `" \t\r\n\v\f "` | `""` | FR-005 |
| `"a b"` | `"a b"` | FR-002 (single space unchanged) |
| `"a\tb"` | `"a b"` | FR-002, FR-003 (tab becomes space) |
| `"a\xa0b"` | `"a\xa0b"` | FR-009 |
| `"\xa0a\xa0"` | `"\xa0a\xa0"` | FR-009 (ends not stripped) |
| `"a \xa0 b"` | `"a \xa0 b"` | FR-009 |
| `"a　　b"` | `"a　　b"` | FR-009 |
| `None` | raises `TypeError` | FR-006 |
| `42` | raises `TypeError` | FR-006 |
| `b"hello"` | raises `TypeError` | FR-006 (no decoding) |
| `True` | raises `TypeError` | FR-006 (`bool` is not `str`) |

## Forbidden implementations

The following are explicitly non-conforming and MUST NOT be used, because each one rewrites or
removes non-ASCII whitespace and so violates FR-009:

- `" ".join(value.split())`
- `re.sub(r"\s+", " ", value)` without the `re.ASCII` flag
- any call to `value.strip()`, `value.lstrip()`, or `value.rstrip()` without an explicit character
  set argument
