# Quickstart: normalize_whitespace

**Feature**: `001-normalize-whitespace`

## Install (editable, for development)

```bash
python3 -m pip install -e .
```

## Use

```python
from gobabygo_text import normalize_whitespace

normalize_whitespace("  hello \t\n  world  ")
# 'hello world'

normalize_whitespace("")
# ''

normalize_whitespace(" \t\r\n ")
# ''

# Non-ASCII whitespace is content, not whitespace, and is preserved:
normalize_whitespace("a\xa0b")
# 'a\xa0b'

normalize_whitespace(None)
# TypeError: normalize_whitespace() expected str, got NoneType
```

## Run the tests

```bash
python3 -m pytest tests/unit/test_whitespace.py -v
```

## Run the full suite with coverage

```bash
python3 -m pytest --cov=gobabygo_text --cov-report=term-missing
```

## What this function is not

It does not perform Unicode normalization, casefolding, or accent stripping; it does not treat
U+00A0 or U+3000 as whitespace; it does not preserve newlines as paragraph breaks; and it does not
accept `bytes`. See [contracts/normalize_whitespace.md](./contracts/normalize_whitespace.md) for the
full contract and the list of forbidden implementations.
