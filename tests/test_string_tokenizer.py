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

    def test_parse_edge_cases(self):
        """Test parsing edge cases: empty string, whitespace only, None input."""
        # Empty string
        result = StringTokenizer.parse("", ",")
        self.assertEqual(result, [])
        
        # Whitespace only
        result = StringTokenizer.parse("   ", ",")
        self.assertEqual(result, [])
        
        # None input
        result = StringTokenizer.parse(None, ",")
        self.assertEqual(result, [])

    def test_parse_multi_char_delimiter(self):
        """Test parsing with multi-character delimiter."""
        result = StringTokenizer.parse("a||b||c", "||")
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_delimiter_positions(self):
        """Test parsing with delimiters at various positions."""
        # Leading delimiter
        result = StringTokenizer.parse(",a,b,c", ",")
        self.assertEqual(result, ["", "a", "b", "c"])
        
        # Trailing delimiter
        result = StringTokenizer.parse("a,b,c,", ",")
        self.assertEqual(result, ["a", "b", "c", ""])
        
        # Only delimiters
        result = StringTokenizer.parse(",,,", ",")
        self.assertEqual(result, ["", "", "", ""])

    def test_parse_single_token(self):
        """Test parsing single token."""
        result = StringTokenizer.parse("hello", ",")
        self.assertEqual(result, ["hello"])

    def test_parse_invalid_delimiter(self):
        """Test that invalid delimiters raise ValueError."""
        # Empty delimiter
        with self.assertRaises(ValueError):
            StringTokenizer.parse("a,b,c", "")
        
        # None delimiter
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

    def test_parses_edge_cases(self):
        """Test parsing edge cases for multiple strings."""
        # Empty list
        result = StringTokenizer.parses([], ",")
        self.assertEqual(result, [])
        
        # List with empty strings
        result = StringTokenizer.parses(["", "a,b", ""], ",")
        self.assertEqual(result, [[], ["a", "b"], []])
        
        # List with None values
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
        
        # Test case where string is too short to have bookends
        result = StringTokenizer.remove_bookends("ab", "ab")
        self.assertEqual(result, "ab")

    def test_remove_bookends_with_spaces(self):
        """Test bookend removal with surrounding spaces."""
        result = StringTokenizer.remove_bookends("  'hello'  ", "'")
        self.assertEqual(result, "hello")

    def test_remove_bookends_no_strip(self):
        """Test bookend removal without stripping."""
        result = StringTokenizer.remove_bookends("  'hello'  ", "'", strip=False)
        self.assertEqual(result, "  'hello'  ")

    def test_remove_bookends_edge_cases(self):
        """Test bookend removal edge cases."""
        # Empty string
        result = StringTokenizer.remove_bookends("", "'")
        self.assertEqual(result, "")
        
        # Single character
        result = StringTokenizer.remove_bookends("'a'", "'")
        self.assertEqual(result, "a")
        
        # String too short
        result = StringTokenizer.remove_bookends("a", "ab")
        self.assertEqual(result, "a")
        
        # Only bookend characters
        result = StringTokenizer.remove_bookends("''", "'")
        self.assertEqual(result, "")

    def test_remove_bookends_asymmetric(self):
        """Test bookend removal with asymmetric bookends."""
        # Only start bookend
        result = StringTokenizer.remove_bookends("'hello", "'")
        self.assertEqual(result, "'hello")
        
        # Only end bookend
        result = StringTokenizer.remove_bookends("hello'", "'")
        self.assertEqual(result, "hello'")

    def test_remove_bookends_invalid_inputs(self):
        """Test bookend removal with invalid inputs."""
        # None input
        with self.assertRaises(AttributeError):
            StringTokenizer.remove_bookends(None, "'")
        
        # Empty bookend
        result = StringTokenizer.remove_bookends("hello", "")
        self.assertEqual(result, "")
        
        # None bookend
        with self.assertRaises(TypeError):
            StringTokenizer.remove_bookends("hello", None)


if __name__ == "__main__":
    unittest.main()
