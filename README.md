# gobabygo-onboarding-canary
Disposable Gobabygo automatic Spec Kit onboarding canary

## Usage

`gobabygo-text` provides text processing utilities.

```python
from gobabygo_text import normalize_whitespace

# Collapses runs of ASCII whitespace to a single space and strips both ends:
normalize_whitespace("  hello \t\n  world  ")
# 'hello world'
```

For more examples and developer instructions, see [Quickstart: normalize_whitespace](specs/001-normalize-whitespace/quickstart.md).

### Non-ASCII Whitespace Caveat

`normalize_whitespace` strictly targets the six ASCII whitespace characters (` `, `\t`, `\n`, `\r`, `\v`, `\f`). Non-ASCII whitespace characters like U+00A0 (NO-BREAK SPACE) and U+3000 (IDEOGRAPHIC SPACE) are treated as ordinary content and preserved verbatim in count and position.
