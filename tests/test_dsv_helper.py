"""Unit tests for DSVHelper class."""

import unittest

from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.exceptions import SplurgeParameterError


class TestDSVHelper(unittest.TestCase):
    """Test cases for DsvHelper class."""

    def test_parse_basic(self):
        """Test basic parsing functionality."""
        content = "a,b,c"
        result = DsvHelper.parse(content, ",")
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_with_options(self):
        """Test parsing with various options."""
        # Test with bookends
        content = '"a","b","c"'
        result = DsvHelper.parse(content, ",", bookend='"')
        self.assertEqual(result, ["a", "b", "c"])
        
        # Test with whitespace stripping
        content = " a , b , c "
        result = DsvHelper.parse(content, ",", strip=True)
        self.assertEqual(result, ["a", "b", "c"])
        
        # Test without whitespace stripping
        content = " a , b , c "
        result = DsvHelper.parse(content, ",", strip=False)
        self.assertEqual(result, [" a ", " b ", " c "])

    def test_parses_basic(self):
        """Test parsing multiple strings."""
        content = ["a,b,c", "d,e,f"]
        result = DsvHelper.parses(content, ",")
        self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])
        
        # Test with bookends
        content = ['"a","b","c"', '"d","e","f"']
        result = DsvHelper.parses(content, ",", bookend='"')
        self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])

    def test_parses_invalid_content_type(self):
        """Test parses method with invalid content type."""
        # Test with non-list content
        with self.assertRaises(SplurgeParameterError):
            DsvHelper.parses("not a list", ",")
        
        # Test with list containing non-string items
        with self.assertRaises(TypeError):
            DsvHelper.parses(["a,b,c", 123, "d,e,f"], ",")
        
        # Test with empty list
        result = DsvHelper.parses([], ",")
        self.assertEqual(result, [])

    def test_invalid_delimiter(self):
        """Test handling of invalid delimiter."""
        with self.assertRaises(SplurgeParameterError):
            DsvHelper.parse("a,b,c", "")

    def test_profile_columns_simple(self):
        """Test profile_columns with simple data."""
        data = [
            ["name", "age", "city"],
            ["John", "25", "New York"],
            ["Jane", "30", "Los Angeles"],
            ["Bob", "35", "Chicago"],
        ]
        
        result = DsvHelper.profile_columns(data)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "name")
        self.assertEqual(result[0]["datatype"], "STRING")
        
        self.assertEqual(result[1]["name"], "age")
        self.assertEqual(result[1]["datatype"], "INTEGER")

    def test_profile_columns_all_types(self):
        """Test profile_columns with all data types."""
        data = [
            ["string", "int", "float", "bool", "date", "datetime", "none"],
            ["text", "123", "123.45", "true", "2023-01-01", "2023-01-01T12:00:00", "none"],
            ["more", "456", "67.89", "false", "2023-02-01", "2023-02-01T13:00:00", ""],
            ["data", "789", "0.0", "true", "2023-03-01", "2023-03-01T14:00:00", "null"],
        ]
        
        result = DsvHelper.profile_columns(data)
        
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0]["datatype"], "STRING")
        self.assertEqual(result[1]["datatype"], "INTEGER")
        self.assertEqual(result[2]["datatype"], "FLOAT")
        self.assertEqual(result[3]["datatype"], "BOOLEAN")
        self.assertEqual(result[4]["datatype"], "DATE")
        self.assertEqual(result[5]["datatype"], "DATETIME")
        self.assertEqual(result[6]["datatype"], "NONE")

    def test_profile_columns_with_custom_header_rows(self):
        """Test profile_columns with custom header row count."""
        data = [
            ["header1", "header2", "header3"],
            ["subheader1", "subheader2", "subheader3"],
            ["John", "25", "New York"],
            ["Jane", "30", "Los Angeles"],
        ]
        
        result = DsvHelper.profile_columns(data, header_rows=2)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "header1_subheader1")
        self.assertEqual(result[0]["datatype"], "STRING")

    def test_profile_columns_with_empty_rows(self):
        """Test profile_columns with empty rows."""
        data = [
            ["name", "age", "city"],
            ["John", "25", "New York"],
            ["", "", ""],  # Empty row
            ["Jane", "30", "Los Angeles"],
        ]
        
        result = DsvHelper.profile_columns(data)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["name"], "name")
        self.assertEqual(result[0]["datatype"], "STRING")


if __name__ == "__main__":
    unittest.main()
