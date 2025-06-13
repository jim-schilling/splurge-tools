"""Unit tests for DSVHelper class."""
import unittest
import tempfile
from pathlib import Path
from jpy_tools.dsv_helper import DSVHelper

class TestDSVHelper(unittest.TestCase):
    """Test cases for DSVHelper class."""

    def test_parse_basic(self):
        """Test basic parsing functionality."""
        content = "a,b,c"
        result = DSVHelper.parse(content, ",")
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_with_bookend(self):
        """Test parsing with text bookends."""
        content = '"a","b","c"'
        result = DSVHelper.parse(content, ",", bookend='"')
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_with_strip(self):
        """Test parsing with whitespace stripping."""
        content = " a , b , c "
        result = DSVHelper.parse(content, ",", strip=True)
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_without_strip(self):
        """Test parsing without whitespace stripping."""
        content = " a , b , c "
        result = DSVHelper.parse(content, ",", strip=False)
        self.assertEqual(result, [" a ", " b ", " c "])

    def test_parses_basic(self):
        """Test parsing multiple strings."""
        content = ["a,b,c", "d,e,f"]
        result = DSVHelper.parses(content, ",")
        self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])

    def test_parses_with_bookend(self):
        """Test parsing multiple strings with bookends."""
        content = ['"a","b","c"', '"d","e","f"']
        result = DSVHelper.parses(content, ",", bookend='"')
        self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])

    def test_parse_file(self):
        """Test parsing from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("a,b,c\nd,e,f")
            temp_path = Path(temp_file.name)
        
        try:
            result = DSVHelper.parse_file(temp_path, ",")
            self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])
        finally:
            temp_path.unlink()

    def test_parse_file_with_bookend(self):
        """Test parsing from file with bookends."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write('"a","b","c"\n"d","e","f"')
            temp_path = Path(temp_file.name)
        
        try:
            result = DSVHelper.parse_file(temp_path, ",", bookend='"')
            self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])
        finally:
            temp_path.unlink()

    def test_invalid_delimiter(self):
        """Test handling of invalid delimiter."""
        with self.assertRaises(ValueError):
            DSVHelper.parse("a,b,c", "")

    def test_invalid_file_path(self):
        """Test handling of invalid file path."""
        with self.assertRaises(FileNotFoundError):
            DSVHelper.parse_file("nonexistent.txt", ",")

if __name__ == '__main__':
    unittest.main()