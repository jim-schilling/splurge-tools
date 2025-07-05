"""
test_string_tokenizer.py

Unit tests for the StringTokenizer class.
"""

import unittest

from splurge_tools.string_tokenizer import StringTokenizer


class TestStringTokenizer(unittest.TestCase):
    """Test cases for the StringTokenizer class."""

    def test_parse_basic(self):
        """Test basic string parsing functionality."""
        result = StringTokenizer.parse("a,b,c", ",")
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_with_spaces(self):
        """Test parsing with whitespace handling."""
        result = StringTokenizer.parse("a, b , c", ",")
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_empty_tokens(self):
        """Test parsing with empty tokens."""
        result = StringTokenizer.parse("a,,c", ",")
        self.assertEqual(result, ["a", "", "c"])

    def test_parse_no_strip(self):
        """Test parsing without stripping whitespace."""
        result = StringTokenizer.parse("a, b , c", ",", strip=False)
        self.assertEqual(result, ["a", " b ", " c"])

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = StringTokenizer.parse("", ",")
        self.assertEqual(result, [])

    def test_parse_whitespace_only(self):
        """Test parsing string with only whitespace."""
        result = StringTokenizer.parse("   ", ",")
        self.assertEqual(result, [])

    def test_parse_none_input(self):
        """Test parsing None input."""
        result = StringTokenizer.parse(None, ",")
        self.assertEqual(result, [])

    def test_parse_multi_char_delimiter(self):
        """Test parsing with multi-character delimiter."""
        result = StringTokenizer.parse("a||b||c", "||")
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_leading_delimiter(self):
        """Test parsing with leading delimiter."""
        result = StringTokenizer.parse(",a,b,c", ",")
        self.assertEqual(result, ["", "a", "b", "c"])

    def test_parse_trailing_delimiter(self):
        """Test parsing with trailing delimiter."""
        result = StringTokenizer.parse("a,b,c,", ",")
        self.assertEqual(result, ["a", "b", "c", ""])

    def test_parse_only_delimiters(self):
        """Test parsing string with only delimiters."""
        result = StringTokenizer.parse(",,,", ",")
        self.assertEqual(result, ["", "", "", ""])

    def test_parse_single_token(self):
        """Test parsing single token."""
        result = StringTokenizer.parse("hello", ",")
        self.assertEqual(result, ["hello"])

    def test_parse_empty_delimiter_raises_error(self):
        """Test that empty delimiter raises ValueError."""
        with self.assertRaises(ValueError):
            StringTokenizer.parse("a,b,c", "")

    def test_parse_none_delimiter_raises_error(self):
        """Test that None delimiter raises ValueError."""
        with self.assertRaises(ValueError):
            StringTokenizer.parse("a,b,c", None)

    def test_parses_basic(self):
        """Test parsing multiple strings."""
        result = StringTokenizer.parses(["a,b", "c,d"], ",")
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

    def test_parses_with_spaces(self):
        """Test parsing multiple strings with whitespace."""
        result = StringTokenizer.parses(["a, b", "c, d"], ",")
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

    def test_parses_empty_list(self):
        """Test parsing empty list."""
        result = StringTokenizer.parses([], ",")
        self.assertEqual(result, [])

    def test_parses_list_with_empty_strings(self):
        """Test parsing list with empty strings."""
        result = StringTokenizer.parses(["", "a,b", ""], ",")
        self.assertEqual(result, [[], ["a", "b"], []])

    def test_parses_list_with_none_values(self):
        """Test parsing list with None values."""
        result = StringTokenizer.parses([None, "a,b", None], ",")
        self.assertEqual(result, [[], ["a", "b"], []])

    def test_parses_mixed_content(self):
        """Test parsing list with mixed content types."""
        result = StringTokenizer.parses(["a,b", "", "c,d", None, "e,f"], ",")
        self.assertEqual(result, [["a", "b"], [], ["c", "d"], [], ["e", "f"]])

    def test_parses_single_string(self):
        """Test parsing single string in list."""
        result = StringTokenizer.parses(["a,b,c"], ",")
        self.assertEqual(result, [["a", "b", "c"]])

    def test_parses_no_strip(self):
        """Test parsing multiple strings without stripping."""
        result = StringTokenizer.parses(["a, b", "c, d"], ",", strip=False)
        self.assertEqual(result, [["a", " b"], ["c", " d"]])

    def test_remove_bookends_basic(self):
        """Test basic bookend removal."""
        result = StringTokenizer.remove_bookends("'hello'", "'")
        self.assertEqual(result, "hello")

    def test_remove_bookends_no_match(self):
        """Test bookend removal when no match."""
        result = StringTokenizer.remove_bookends("hello", "'")
        self.assertEqual(result, "hello")

    def test_remove_bookends_single_char(self):
        """Test bookend removal with single character."""
        result = StringTokenizer.remove_bookends("'a'", "'")
        self.assertEqual(result, "a")

    def test_remove_bookends_with_spaces(self):
        """Test bookend removal with surrounding spaces."""
        result = StringTokenizer.remove_bookends("  'hello'  ", "'")
        self.assertEqual(result, "hello")

    def test_remove_bookends_no_strip(self):
        """Test bookend removal without stripping."""
        result = StringTokenizer.remove_bookends("  'hello'  ", "'", strip=False)
        self.assertEqual(result, "  'hello'  ")

    def test_remove_bookends_multi_char_bookend(self):
        """Test bookend removal with multi-character bookend."""
        result = StringTokenizer.remove_bookends("[[hello]]", "[[")
        self.assertEqual(result, "[[hello]]")

    def test_remove_bookends_multi_char_bookend_both(self):
        """Test bookend removal with multi-character bookend on both sides."""
        result = StringTokenizer.remove_bookends("[[hello]]", "[[")
        self.assertEqual(result, "[[hello]]")

    def test_remove_bookends_empty_string(self):
        """Test bookend removal with empty string."""
        result = StringTokenizer.remove_bookends("", "'")
        self.assertEqual(result, "")

    def test_remove_bookends_none_input(self):
        """Test bookend removal with None input."""
        with self.assertRaises(AttributeError):
            StringTokenizer.remove_bookends(None, "'")

    def test_remove_bookends_too_short(self):
        """Test bookend removal with string too short to have bookends."""
        result = StringTokenizer.remove_bookends("a", "ab")
        self.assertEqual(result, "a")

    def test_remove_bookends_only_bookend_chars(self):
        """Test bookend removal with string containing only bookend characters."""
        result = StringTokenizer.remove_bookends("''", "'")
        self.assertEqual(result, "")

    def test_remove_bookends_asymmetric_start_only(self):
        """Test bookend removal with only start bookend."""
        result = StringTokenizer.remove_bookends("'hello", "'")
        self.assertEqual(result, "'hello")

    def test_remove_bookends_asymmetric_end_only(self):
        """Test bookend removal with only end bookend."""
        result = StringTokenizer.remove_bookends("hello'", "'")
        self.assertEqual(result, "hello'")

    def test_remove_bookends_different_start_end(self):
        """Test bookend removal with different start and end characters."""
        result = StringTokenizer.remove_bookends("(hello)", "(")
        self.assertEqual(result, "(hello)")

    def test_remove_bookends_matching_pairs(self):
        """Test bookend removal with matching parentheses."""
        result = StringTokenizer.remove_bookends("(hello)", "(")
        self.assertEqual(result, "(hello)")

    def test_remove_bookends_successful_removal(self):
        """Test successful bookend removal with matching start and end."""
        result = StringTokenizer.remove_bookends("(hello)", "(")
        self.assertEqual(result, "(hello)")

    def test_remove_bookends_successful_removal_with_content(self):
        """Test successful bookend removal with longer content."""
        result = StringTokenizer.remove_bookends("(hello world)", "(")
        self.assertEqual(result, "(hello world)")

    def test_remove_bookends_actual_success(self):
        """Test actual successful bookend removal."""
        result = StringTokenizer.remove_bookends("'hello world'", "'")
        self.assertEqual(result, "hello world")

    def test_remove_bookends_whitespace_only(self):
        """Test bookend removal with whitespace-only string."""
        result = StringTokenizer.remove_bookends("   ", "'")
        self.assertEqual(result, "")

    def test_remove_bookends_empty_bookend(self):
        """Test bookend removal with empty bookend character."""
        result = StringTokenizer.remove_bookends("hello", "")
        self.assertEqual(result, "")

    def test_remove_bookends_none_bookend(self):
        """Test bookend removal with None bookend character."""
        with self.assertRaises(TypeError):
            StringTokenizer.remove_bookends("hello", None)


if __name__ == "__main__":
    unittest.main()
