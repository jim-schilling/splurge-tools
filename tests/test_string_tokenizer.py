"""
test_string_tokenizer.py

Unit tests for the StringTokenizer class.
"""

import unittest
from jpy_tools.string_tokenizer import StringTokenizer

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
        self.assertEqual(result, ["a", "c"])

    def test_parse_no_strip(self):
        """Test parsing without stripping whitespace."""
        result = StringTokenizer.parse("a, b , c", ",", strip=False)
        self.assertEqual(result, ["a", " b ", " c"])

    def test_parses_basic(self):
        """Test parsing multiple strings."""
        result = StringTokenizer.parses(["a,b", "c,d"], ",")
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

    def test_parses_with_spaces(self):
        """Test parsing multiple strings with whitespace."""
        result = StringTokenizer.parses(["a, b", "c, d"], ",")
        self.assertEqual(result, [["a", "b"], ["c", "d"]])

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

if __name__ == '__main__':
    unittest.main()