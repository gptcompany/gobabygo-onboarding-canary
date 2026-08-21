import time
import pytest
from gobabygo_text import normalize_whitespace

ASCII_WHITESPACE_CHARS = [
    ("space", " "),
    ("tab", "\t"),
    ("linefeed", "\n"),
    ("carriage_return", "\r"),
    ("vertical_tab", "\v"),
    ("form_feed", "\f"),
]


# =============================================================================
# Phase 3 / User Story 1: Collapse and strip messy ASCII whitespace (T004)
# =============================================================================

class TestNormalizeWhitespaceUS1:
    """User Story 1 - Collapse and strip messy ASCII whitespace."""

    def test_acceptance_scenario_1_messy_string(self):
        assert normalize_whitespace("  hello \t\n  world  ") == "hello world"

    def test_acceptance_scenario_2_no_whitespace(self):
        assert normalize_whitespace("hello") == "hello"

    def test_acceptance_scenario_3_empty_string(self):
        assert normalize_whitespace("") == ""

    def test_acceptance_scenario_4_whitespace_only(self):
        assert normalize_whitespace(" \t\r\n\v\f ") == ""

    def test_acceptance_scenario_5_single_space_unchanged(self):
        assert normalize_whitespace("a b") == "a b"

    def test_edge_case_mixed_runs_between_words(self):
        assert normalize_whitespace("a\t \n\rb") == "a b"
        assert normalize_whitespace("hello\f\v\t\r\n world") == "hello world"

    def test_edge_case_lone_tab_between_words(self):
        assert normalize_whitespace("a\tb") == "a b"

    def test_edge_case_leading_and_trailing_removed_entirely(self):
        assert normalize_whitespace("\t\n\r hello \r\n\t") == "hello"
        assert normalize_whitespace("   multiple   words   here   ") == "multiple words here"

    @pytest.mark.parametrize("name,char", ASCII_WHITESPACE_CHARS)
    def test_sc002_each_ascii_whitespace_interior_run(self, name, char):
        # Single interior char
        assert normalize_whitespace(f"hello{char}world") == "hello world"
        # Multiple interior chars
        assert normalize_whitespace(f"hello{char}{char}{char}world") == "hello world"

    @pytest.mark.parametrize("name,char", ASCII_WHITESPACE_CHARS)
    def test_sc002_each_ascii_whitespace_at_string_ends(self, name, char):
        # Leading
        assert normalize_whitespace(f"{char}{char}hello") == "hello"
        # Trailing
        assert normalize_whitespace(f"hello{char}{char}") == "hello"
        # Both ends
        assert normalize_whitespace(f"{char}hello{char}") == "hello"

    def test_fr011_purity_and_idempotency(self):
        original = "  foo \t\n bar  "
        snapshot = str(original)
        result1 = normalize_whitespace(original)
        # Input object is unchanged
        assert original == snapshot
        assert original == "  foo \t\n bar  "
        # Idempotency: normalize_whitespace(normalize_whitespace(s)) == normalize_whitespace(s)
        result2 = normalize_whitespace(result1)
        assert result1 == "foo bar"
        assert result2 == result1

    def test_keyword_argument_invocation(self):
        assert normalize_whitespace(value="  test  ") == "test"


# =============================================================================
# Phase 4 / User Story 2: Reject non-string input loudly (T005)
# =============================================================================

class TestNormalizeWhitespaceUS2:
    """User Story 2 - Reject non-string input with TypeError naming the received type."""

    @pytest.mark.parametrize(
        "invalid_input,expected_type_name",
        [
            (None, "NoneType"),
            (42, "int"),
            (b"hello", "bytes"),
            (True, "bool"),
            (False, "bool"),
            (b"", "bytes"),
            ([1, 2, 3], "list"),
            ({"a": 1}, "dict"),
            (3.14, "float"),
            (object(), "object"),
        ],
    )
    def test_sc004_non_string_raises_typeerror_with_type_name(
        self, invalid_input, expected_type_name
    ):
        with pytest.raises(TypeError) as exc_info:
            normalize_whitespace(invalid_input)
        assert expected_type_name in str(exc_info.value)

    def test_bytes_not_decoded(self):
        with pytest.raises(TypeError) as exc_info:
            normalize_whitespace(b"hello world")
        assert "bytes" in str(exc_info.value)

    def test_bool_not_accepted(self):
        with pytest.raises(TypeError) as exc_info:
            normalize_whitespace(True)
        assert "bool" in str(exc_info.value)


# =============================================================================
# Phase 5 / User Story 3: Leave non-ASCII whitespace untouched (T006)
# =============================================================================

class TestNormalizeWhitespaceUS3:
    """User Story 3 - Leave non-ASCII whitespace untouched."""

    def test_acceptance_scenario_1_non_breaking_space_interior(self):
        assert normalize_whitespace("a\xa0b") == "a\xa0b"

    def test_acceptance_scenario_2_non_breaking_space_ends(self):
        assert normalize_whitespace("\xa0a\xa0") == "\xa0a\xa0"

    def test_acceptance_scenario_3_mixed_ascii_and_non_breaking_space(self):
        assert normalize_whitespace("a \xa0 b") == "a \xa0 b"

    def test_acceptance_scenario_4_ideographic_space(self):
        assert normalize_whitespace("a\u3000\u3000b") == "a\u3000\u3000b"

    @pytest.mark.parametrize(
        "raw_input,expected_output",
        [
            ("  custom \t string  ", "custom string"),
            ("abc", "abc"),
            ("", ""),
            ("a\xa0b", "a\xa0b"),
        ],
    )
    def test_fr008_str_subclass_accepted_returns_plain_str(
        self, raw_input, expected_output
    ):
        class CustomStr(str):
            pass

        custom_val = CustomStr(raw_input)
        result = normalize_whitespace(custom_val)
        assert result == expected_output
        assert type(result) is str


# =============================================================================
# Phase 7: Polish & Performance (T008 / SC-006)
# =============================================================================

class TestNormalizeWhitespacePerformance:
    """SC-006: Linear-time performance on large input."""

    def test_sc006_one_million_char_performance(self):
        # Note on exact size: The constructed input is 1,000,010 characters in total length
        # (7-character prefix and suffix around 83,333 12-character chunks), satisfying SC-006.
        chunk = "word   \t\n\r  "
        repeat_count = 1_000_000 // len(chunk)
        large_input = "   \n\t  " + (chunk * repeat_count) + "   \t\n  "
        expected = " ".join(["word"] * repeat_count)

        start = time.perf_counter()
        result = normalize_whitespace(large_input)
        duration = time.perf_counter() - start

        assert result == expected
        # SC-006's "well under one second" is the expected speed on developer hardware (~0.05-0.10s).
        # We assert duration < 5.0s to provide ~5x headroom against transient CPU throttling or
        # load spikes on shared CI runners, while still failing by orders of magnitude if a
        # super-linear (e.g. quadratic) algorithmic regression is introduced.
        assert duration < 5.0, f"Expected < 5.0s, took {duration:.4f}s"
