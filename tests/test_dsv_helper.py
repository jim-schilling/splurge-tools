"""Unit tests for DSVHelper class."""

import math
import tempfile
import unittest
from pathlib import Path

from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.type_helper import DataType


class TestDSVHelper(unittest.TestCase):
    """Test cases for DsvHelper class."""

    def test_parse_basic(self):
        """Test basic parsing functionality."""
        content = "a,b,c"
        result = DsvHelper.parse(content, ",")
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_with_bookend(self):
        """Test parsing with text bookends."""
        content = '"a","b","c"'
        result = DsvHelper.parse(content, ",", bookend='"')
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_with_strip(self):
        """Test parsing with whitespace stripping."""
        content = " a , b , c "
        result = DsvHelper.parse(content, ",", strip=True)
        self.assertEqual(result, ["a", "b", "c"])

    def test_parse_without_strip(self):
        """Test parsing without whitespace stripping."""
        content = " a , b , c "
        result = DsvHelper.parse(content, ",", strip=False)
        self.assertEqual(result, [" a ", " b ", " c "])

    def test_parses_basic(self):
        """Test parsing multiple strings."""
        content = ["a,b,c", "d,e,f"]
        result = DsvHelper.parses(content, ",")
        self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])

    def test_parses_with_bookend(self):
        """Test parsing multiple strings with bookends."""
        content = ['"a","b","c"', '"d","e","f"']
        result = DsvHelper.parses(content, ",", bookend='"')
        self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])

    def test_parses_invalid_content_type(self):
        """Test parses method with invalid content type."""
        # Test with non-list content
        with self.assertRaises(TypeError):
            DsvHelper.parses("not a list", ",")
        
        # Test with list containing non-string items
        with self.assertRaises(TypeError):
            DsvHelper.parses(["a,b,c", 123, "d,e,f"], ",")
        
        # Test with empty list
        result = DsvHelper.parses([], ",")
        self.assertEqual(result, [])

    def test_parse_file(self):
        """Test parsing from file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("a,b,c\nd,e,f")
            temp_path = Path(temp_file.name)

        try:
            result = DsvHelper.parse_file(temp_path, ",")
            self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])
        finally:
            temp_path.unlink()

    def test_parse_file_with_bookend(self):
        """Test parsing from file with bookends."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write('"a","b","c"\n"d","e","f"')
            temp_path = Path(temp_file.name)

        try:
            result = DsvHelper.parse_file(temp_path, ",", bookend='"')
            self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])
        finally:
            temp_path.unlink()

    def test_parse_file_with_skip_rows(self):
        """Test parsing from file with header and footer skipping."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("header1,header2,header3\na,b,c\nd,e,f\nfooter1,footer2,footer3")
            temp_path = Path(temp_file.name)

        try:
            result = DsvHelper.parse_file(
                temp_path, ",", skip_header_rows=1, skip_footer_rows=1
            )
            self.assertEqual(result, [["a", "b", "c"], ["d", "e", "f"]])
        finally:
            temp_path.unlink()

    def test_invalid_delimiter(self):
        """Test handling of invalid delimiter."""
        with self.assertRaises(ValueError):
            DsvHelper.parse("a,b,c", "")

    def test_invalid_file_path(self):
        """Test handling of invalid file path."""
        with self.assertRaises(FileNotFoundError):
            DsvHelper.parse_file("nonexistent.txt", ",")

    def test_parse_stream_basic(self):
        """Test parse_stream yields correct chunks and parses all rows."""
        total_rows = 2499
        chunk_size = 500
        lines = [f"a{i},b{i},c{i}" for i in range(total_rows)]
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(lines))
            temp_path = Path(temp_file.name)

        try:
            chunks = list(DsvHelper.parse_stream(temp_path, ",", chunk_size=chunk_size))
            # Should yield 5 chunks: 500, 500, 500, 500, 499
            self.assertEqual(len(chunks), math.ceil(total_rows / chunk_size))
            self.assertEqual(len(chunks[0]), chunk_size)
            self.assertEqual(len(chunks[1]), chunk_size)
            self.assertEqual(len(chunks[2]), chunk_size)
            self.assertEqual(len(chunks[3]), chunk_size)
            self.assertEqual(len(chunks[4]), total_rows - 4 * chunk_size)
            # Check content of first and last row
            self.assertEqual(chunks[0][0], ["a0", "b0", "c0"])
            self.assertEqual(chunks[-1][-1], [f"a{total_rows-1}", f"b{total_rows-1}", f"c{total_rows-1}"])
        finally:
            temp_path.unlink()

    def test_parse_stream_with_header_footer(self):
        """Test parse_stream with header and footer skipping."""
        total_rows = 2499
        chunk_size = 500
        header = ["header1,header2,header3"]
        footer = ["footer1,footer2,footer3"]
        data = [f"a{i},b{i},c{i}" for i in range(total_rows)]
        lines = header + data + footer
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(lines))
            temp_path = Path(temp_file.name)

        try:
            chunks = list(DsvHelper.parse_stream(
                temp_path, ",", chunk_size=chunk_size, skip_header_rows=1, skip_footer_rows=1
            ))
            # Should yield 5 chunks: 500, 500, 500, 500, 499
            self.assertEqual(len(chunks), 5)
            self.assertEqual(len(chunks[0]), chunk_size)
            self.assertEqual(len(chunks[1]), chunk_size)
            self.assertEqual(len(chunks[2]), chunk_size)
            self.assertEqual(len(chunks[3]), chunk_size)
            self.assertEqual(len(chunks[4]), total_rows - 4 * chunk_size)
            # Check first and last data row
            self.assertEqual(chunks[0][0], ["a0", "b0", "c0"])
            self.assertEqual(chunks[-1][-1], [f"a{total_rows-1}", f"b{total_rows-1}", f"c{total_rows-1}"])
        finally:
            temp_path.unlink()

    def test_parse_stream_iteration(self):
        """Test iterating over parse_stream yields correct data."""
        total_rows = 2499
        chunk_size = 500
        lines = [f"a{i},b{i},c{i}" for i in range(total_rows)]
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(lines))
            temp_path = Path(temp_file.name)

        try:
            # Test iteration over parse_stream
            chunk_count = 0
            total_parsed_rows = 0
            expected_chunks = 5  # 2499 rows / 500 chunk_size = 5 chunks
            
            for chunk in DsvHelper.parse_stream(temp_path, ",", chunk_size=chunk_size):
                chunk_count += 1
                total_parsed_rows += len(chunk)
                
                # Verify each chunk has correct structure
                for row in chunk:
                    self.assertEqual(len(row), 3)  # Each row should have 3 columns
                    self.assertTrue(all(isinstance(cell, str) for cell in row))
                
                # Verify chunk sizes (last chunk may be smaller)
                if chunk_count < expected_chunks:
                    self.assertEqual(len(chunk), chunk_size)
                else:
                    self.assertEqual(len(chunk), total_rows - (expected_chunks - 1) * chunk_size)
            
            # Verify total counts
            self.assertEqual(chunk_count, expected_chunks)
            self.assertEqual(total_parsed_rows, total_rows)
            
            # Verify first and last rows across all chunks
            stream = DsvHelper.parse_stream(temp_path, ",", chunk_size=chunk_size)
            first_chunk = next(stream)
            self.assertEqual(first_chunk[0], ["a0", "b0", "c0"])
            
            # Get last chunk
            last_chunk = None
            for chunk in stream:
                last_chunk = chunk
            
            self.assertEqual(last_chunk[-1], [f"a{total_rows-1}", f"b{total_rows-1}", f"c{total_rows-1}"])
            
        finally:
            temp_path.unlink()

    def test_parse_stream_invalid_delimiter(self):
        """Test parse_stream with invalid delimiter."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("a,b,c\nd,e,f")
            temp_path = Path(temp_file.name)

        try:
            with self.assertRaises(ValueError):
                list(DsvHelper.parse_stream(temp_path, ""))
        finally:
            temp_path.unlink()

    def test_parse_stream_invalid_chunk_size(self):
        """Test parse_stream with invalid chunk size."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("a,b,c\nd,e,f")
            temp_path = Path(temp_file.name)

        try:
            with self.assertRaises(ValueError):
                list(DsvHelper.parse_stream(temp_path, ",", chunk_size=50))
        finally:
            temp_path.unlink()

    def test_parse_stream_invalid_skip_rows(self):
        """Test parse_stream with invalid skip rows parameters."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("a,b,c\nd,e,f")
            temp_path = Path(temp_file.name)

        try:
            with self.assertRaises(ValueError):
                list(DsvHelper.parse_stream(temp_path, ",", skip_header_rows=-1))
            
            with self.assertRaises(ValueError):
                list(DsvHelper.parse_stream(temp_path, ",", skip_footer_rows=-1))
        finally:
            temp_path.unlink()

    def test_parse_stream_header_exceeds_file(self):
        """Test parse_stream when header rows exceed file content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("a,b,c\nd,e,f")
            temp_path = Path(temp_file.name)

        try:
            # Should return empty iterator when header rows exceed file content
            chunks = list(DsvHelper.parse_stream(temp_path, ",", skip_header_rows=10))
            self.assertEqual(chunks, [])
        finally:
            temp_path.unlink()

    def test_parse_stream_small_file(self):
        """Test parse_stream with a small file that fits in one chunk."""
        lines = ["a,b,c", "d,e,f", "g,h,i"]
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(lines))
            temp_path = Path(temp_file.name)

        try:
            chunks = list(DsvHelper.parse_stream(temp_path, ",", chunk_size=100))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(len(chunks[0]), 3)
            self.assertEqual(chunks[0], [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]])
        finally:
            temp_path.unlink()

    def test_parse_stream_with_bookend(self):
        """Test parse_stream with bookend processing."""
        lines = ['"a","b","c"', '"d","e","f"', '"g","h","i"']
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(lines))
            temp_path = Path(temp_file.name)

        try:
            chunks = list(DsvHelper.parse_stream(temp_path, ",", bookend='"', chunk_size=100))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0], [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]])
        finally:
            temp_path.unlink()

    def test_parse_stream_without_strip(self):
        """Test parse_stream without stripping whitespace."""
        lines = [" a , b , c ", " d , e , f "]
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(lines))
            temp_path = Path(temp_file.name)

        try:
            chunks = list(DsvHelper.parse_stream(temp_path, ",", strip=False, chunk_size=100))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0], [[" a ", " b ", " c "], [" d ", " e ", " f "]])
        finally:
            temp_path.unlink()

    def test_parse_stream_footer_only(self):
        """Test parse_stream with only footer rows to skip."""
        lines = ["a,b,c", "d,e,f", "footer1,footer2,footer3"]
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("\n".join(lines))
            temp_path = Path(temp_file.name)

        try:
            chunks = list(DsvHelper.parse_stream(temp_path, ",", skip_footer_rows=1, chunk_size=100))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(len(chunks[0]), 2)
            self.assertEqual(chunks[0], [["a", "b", "c"], ["d", "e", "f"]])
        finally:
            temp_path.unlink()

    def test_parse_stream_empty_file(self):
        """Test parse_stream with an empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write("")
            temp_path = Path(temp_file.name)

        try:
            chunks = list(DsvHelper.parse_stream(temp_path, ",", chunk_size=100))
            self.assertEqual(chunks, [])
        finally:
            temp_path.unlink()

    def test_profile_columns_simple(self):
        """
        Test DsvHelper.profile_columns returns correct column names and datatypes for a simple DSV input.
        """
        # Example DSV data: header + two rows
        data = [
            ["Name", "Age", "Active"],
            ["Alice", "30", "true"],
            ["Bob", "25", "false"]
        ]
        expected = [
            {"name": "Name", "datatype": DataType.STRING.name.upper()},
            {"name": "Age", "datatype": DataType.INTEGER.name.upper()},
            {"name": "Active", "datatype": DataType.BOOLEAN.name.upper()}
        ]
        result = DsvHelper.profile_columns(data)
        self.assertEqual(result, expected)

    def test_profile_columns_all_types(self):
        """
        Test DsvHelper.profile_columns detects all supported datatypes.
        """
        # Header row and one value row for each type
        data = [
            [
                "StringCol", "IntCol", "FloatCol", "BoolCol", "DateCol", "TimeCol", "DateTimeCol", "MixedCol", "EmptyCol", "NoneCol"
            ],
            [
                "hello", "42", "3.14", "true", "2024-07-01", "13:45:00", "2024-07-01T13:45:00", "abc", "", "none"
            ],
            [
                "world", "-7", "2.71", "false", "2023-12-31", "23:59:59", "2023-12-31T23:59:59", "123", "", "null"
            ],
            [
                "!@#", "0", "0.0", "TRUE", "2022-01-01", "00:00:00", "2022-01-01T00:00:00", "3.14", "", "None"
            ],
        ]
        expected = [
            {"name": "StringCol", "datatype": DataType.STRING.name.upper()},
            {"name": "IntCol", "datatype": DataType.INTEGER.name.upper()},
            {"name": "FloatCol", "datatype": DataType.FLOAT.name.upper()},
            {"name": "BoolCol", "datatype": DataType.BOOLEAN.name.upper()},
            {"name": "DateCol", "datatype": DataType.DATE.name.upper()},
            {"name": "TimeCol", "datatype": DataType.TIME.name.upper()},
            {"name": "DateTimeCol", "datatype": DataType.DATETIME.name.upper()},
            {"name": "MixedCol", "datatype": DataType.MIXED.name.upper()},
            {"name": "EmptyCol", "datatype": DataType.EMPTY.name.upper()},
            {"name": "NoneCol", "datatype": DataType.NONE.name.upper()},
        ]
        result = DsvHelper.profile_columns(data)
        self.assertEqual(result, expected)

    def test_profile_columns_with_custom_header_rows(self):
        """Test profile_columns with custom header rows count."""
        data = [
            ["Header1", "Header2", "Header3"],
            ["SubHeader1", "SubHeader2", "SubHeader3"],
            ["Alice", "30", "true"],
            ["Bob", "25", "false"]
        ]
        expected = [
            {"name": "Header1_SubHeader1", "datatype": DataType.STRING.name.upper()},
            {"name": "Header2_SubHeader2", "datatype": DataType.INTEGER.name.upper()},
            {"name": "Header3_SubHeader3", "datatype": DataType.BOOLEAN.name.upper()}
        ]
        result = DsvHelper.profile_columns(data, header_rows=2)
        self.assertEqual(result, expected)

    def test_profile_columns_with_empty_rows(self):
        """Test profile_columns with empty rows handling."""
        data = [
            ["Name", "Age", "Active"],
            ["Alice", "30", "true"],
            ["", "", ""],  # Empty row
            ["Bob", "25", "false"]
        ]
        expected = [
            {"name": "Name", "datatype": DataType.STRING.name.upper()},
            {"name": "Age", "datatype": DataType.INTEGER.name.upper()},
            {"name": "Active", "datatype": DataType.BOOLEAN.name.upper()}
        ]
        result = DsvHelper.profile_columns(data, skip_empty_rows=True)
        self.assertEqual(result, expected)

        # Test without skipping empty rows
        result_with_empty = DsvHelper.profile_columns(data, skip_empty_rows=False)
        self.assertEqual(len(result_with_empty), 3)
        # The empty row should affect the data type inference


if __name__ == "__main__":
    unittest.main()
