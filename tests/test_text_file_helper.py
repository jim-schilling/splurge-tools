import os
import tempfile
import unittest

from splurge_tools.text_file_helper import TextFileHelper


class TestTextFileHelper(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
        self.test_content = [
            "Line 1",
            "Line 2",
            "Line 3",
            "  Line 4 with spaces  ",
            "Line 5",
        ]
        self.temp_file.write("\n".join(self.test_content))
        self.temp_file.close()

    def tearDown(self):
        # Clean up the temporary file
        os.unlink(self.temp_file.name)

    def test_line_count(self):
        """Test line counting functionality"""
        # Test normal case
        self.assertEqual(TextFileHelper.line_count(self.temp_file.name), 5)

        # Test empty file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as empty_file:
            empty_file.write("")
        self.assertEqual(TextFileHelper.line_count(empty_file.name), 0)
        os.unlink(empty_file.name)

        # Test file not found
        with self.assertRaises(FileNotFoundError):
            TextFileHelper.line_count("nonexistent_file.txt")

        # Test with different encoding
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-16", delete=False
        ) as encoded_file:
            encoded_file.write("Line 1\nLine 2")
        self.assertEqual(
            TextFileHelper.line_count(encoded_file.name, encoding="utf-16"), 2
        )
        os.unlink(encoded_file.name)

    def test_preview(self):
        """Test file preview functionality"""
        # Test normal case with default parameters
        preview_lines = TextFileHelper.preview(self.temp_file.name)
        self.assertEqual(len(preview_lines), 5)
        self.assertEqual(preview_lines[0], "Line 1")
        self.assertEqual(preview_lines[3], "Line 4 with spaces")

        # Test with strip=False
        preview_lines = TextFileHelper.preview(self.temp_file.name, strip=False)
        self.assertEqual(preview_lines[3], "  Line 4 with spaces  ")

        # Test with max_lines limit
        preview_lines = TextFileHelper.preview(self.temp_file.name, max_lines=3)
        self.assertEqual(len(preview_lines), 3)
        self.assertEqual(preview_lines[2], "Line 3")

        # Test with skip_header_rows
        preview_lines = TextFileHelper.preview(self.temp_file.name, skip_header_rows=2)
        self.assertEqual(len(preview_lines), 3)
        self.assertEqual(preview_lines[0], "Line 3")
        self.assertEqual(preview_lines[2], "Line 5")

        # Test with skip_header_rows and max_lines combination
        preview_lines = TextFileHelper.preview(self.temp_file.name, max_lines=2, skip_header_rows=1)
        self.assertEqual(len(preview_lines), 2)
        self.assertEqual(preview_lines[0], "Line 2")
        self.assertEqual(preview_lines[1], "Line 3")

        # Test with skip_header_rows larger than file
        preview_lines = TextFileHelper.preview(self.temp_file.name, skip_header_rows=10)
        self.assertEqual(len(preview_lines), 0)

        # Test with skip_header_rows equal to file size
        preview_lines = TextFileHelper.preview(self.temp_file.name, skip_header_rows=5)
        self.assertEqual(len(preview_lines), 0)

        # Test with negative skip_header_rows (should be treated as 0)
        preview_lines = TextFileHelper.preview(self.temp_file.name, skip_header_rows=-2)
        self.assertEqual(len(preview_lines), 5)
        self.assertEqual(preview_lines[0], "Line 1")

        # Test with different encoding
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-16", delete=False
        ) as encoded_file:
            encoded_file.write("Line 1\nLine 2")
        preview_lines = TextFileHelper.preview(encoded_file.name, encoding="utf-16")
        self.assertEqual(preview_lines, ["Line 1", "Line 2"])
        os.unlink(encoded_file.name)

        # Test invalid max_lines
        with self.assertRaises(ValueError):
            TextFileHelper.preview(self.temp_file.name, max_lines=0)

        # Test file not found
        with self.assertRaises(FileNotFoundError):
            TextFileHelper.preview("nonexistent_file.txt")

    def test_load(self):
        """Test file loading functionality"""
        # Test normal case with default parameters (strip=True)
        loaded_lines = TextFileHelper.load(self.temp_file.name)
        self.assertEqual(len(loaded_lines), 5)
        self.assertEqual(loaded_lines[0], "Line 1")
        self.assertEqual(loaded_lines[3], "Line 4 with spaces")

        # Test with strip=False
        loaded_lines = TextFileHelper.load(self.temp_file.name, strip=False)
        self.assertEqual(loaded_lines[3], "  Line 4 with spaces  ")

        # Test with skip_header_rows
        loaded_lines = TextFileHelper.load(self.temp_file.name, skip_header_rows=2)
        self.assertEqual(len(loaded_lines), 3)
        self.assertEqual(loaded_lines[0], "Line 3")

        # Test with skip_footer_rows
        loaded_lines = TextFileHelper.load(self.temp_file.name, skip_footer_rows=2)
        self.assertEqual(len(loaded_lines), 3)
        self.assertEqual(loaded_lines[-1], "Line 3")

        # Test with both skip_header_rows and skip_footer_rows
        loaded_lines = TextFileHelper.load(
            self.temp_file.name, skip_header_rows=1, skip_footer_rows=1
        )
        self.assertEqual(len(loaded_lines), 3)
        self.assertEqual(loaded_lines[0], "Line 2")
        self.assertEqual(loaded_lines[-1], "Line 4 with spaces")

        # Test with different encoding
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-16", delete=False
        ) as encoded_file:
            encoded_file.write("Line 1\nLine 2")
        loaded_lines = TextFileHelper.load(encoded_file.name, encoding="utf-16")
        self.assertEqual(loaded_lines, ["Line 1", "Line 2"])
        os.unlink(encoded_file.name)

        # Test empty file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as empty_file:
            empty_file.write("")
        self.assertEqual(TextFileHelper.load(empty_file.name), [])
        os.unlink(empty_file.name)

        # Test file not found
        with self.assertRaises(FileNotFoundError):
            TextFileHelper.load("nonexistent_file.txt")

    def test_load_as_stream(self):
        """Test streaming file loading functionality"""
        # Create a larger test file for streaming tests
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as large_file:
            large_content = [f"Line {i}" for i in range(1, 1501)]  # 1500 lines
            large_file.write("\n".join(large_content))
            large_file_path = large_file.name

        try:
            # Test normal case with default chunk size (500)
            chunks = list(TextFileHelper.load_as_stream(large_file_path))
            self.assertEqual(len(chunks), 3)  # 1500 lines / 500 = 3 chunks
            self.assertEqual(len(chunks[0]), 500)
            self.assertEqual(len(chunks[1]), 500)
            self.assertEqual(len(chunks[2]), 500)
            self.assertEqual(chunks[0][0], "Line 1")
            self.assertEqual(chunks[0][499], "Line 500")
            self.assertEqual(chunks[1][0], "Line 501")
            self.assertEqual(chunks[2][499], "Line 1500")

            # Test with custom chunk size
            chunks = list(TextFileHelper.load_as_stream(large_file_path, chunk_size=300))
            self.assertEqual(len(chunks), 5)  # 1500 lines / 300 = 5 chunks
            self.assertEqual(len(chunks[0]), 300)
            self.assertEqual(len(chunks[4]), 300)
            self.assertEqual(chunks[0][0], "Line 1")
            self.assertEqual(chunks[4][299], "Line 1500")

            # Test with strip=False
            chunks = list(TextFileHelper.load_as_stream(large_file_path, strip=False))
            self.assertEqual(len(chunks), 3)
            self.assertEqual(chunks[0][0], "Line 1")

            # Test with skip_header_rows
            chunks = list(TextFileHelper.load_as_stream(large_file_path, skip_header_rows=100))
            self.assertEqual(len(chunks), 3)  # 1400 lines / 500 = 3 chunks
            self.assertEqual(chunks[0][0], "Line 101")
            self.assertEqual(chunks[2][399], "Line 1500")

            # Test with skip_footer_rows
            chunks = list(TextFileHelper.load_as_stream(large_file_path, skip_footer_rows=100))
            self.assertEqual(len(chunks), 3)  # 1400 lines / 500 = 3 chunks
            self.assertEqual(chunks[0][0], "Line 1")
            self.assertEqual(chunks[2][399], "Line 1400")

            # Test with both skip_header_rows and skip_footer_rows
            chunks = list(TextFileHelper.load_as_stream(
                large_file_path, 
                skip_header_rows=200, 
                skip_footer_rows=200
            ))
            self.assertEqual(len(chunks), 3)  # 1100 lines / 500 = 3 chunks
            self.assertEqual(chunks[0][0], "Line 201")
            self.assertEqual(chunks[2][99], "Line 1300")

            # Test with different encoding
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-16", delete=False) as encoded_file:
                encoded_file.write("Line 1\nLine 2\nLine 3")
                encoded_file_path = encoded_file.name
            
            try:
                chunks = list(TextFileHelper.load_as_stream(encoded_file_path, encoding="utf-16", chunk_size=100))
                self.assertEqual(len(chunks), 1)
                self.assertEqual(chunks[0], ["Line 1", "Line 2", "Line 3"])
            finally:
                os.unlink(encoded_file_path)

            # Test empty file
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as empty_file:
                empty_file.write("")
                empty_file_path = empty_file.name
            
            try:
                chunks = list(TextFileHelper.load_as_stream(empty_file_path))
                self.assertEqual(len(chunks), 0)
            finally:
                os.unlink(empty_file_path)

            # Test file with fewer lines than chunk size
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as small_file:
                small_file.write("Line 1\nLine 2\nLine 3")
                small_file_path = small_file.name
            
            try:
                chunks = list(TextFileHelper.load_as_stream(small_file_path, chunk_size=100))
                self.assertEqual(len(chunks), 1)
                self.assertEqual(len(chunks[0]), 3)
                self.assertEqual(chunks[0], ["Line 1", "Line 2", "Line 3"])
            finally:
                os.unlink(small_file_path)

            # Test invalid chunk_size
            with self.assertRaises(ValueError):
                list(TextFileHelper.load_as_stream(large_file_path, chunk_size=50))

            # Test file not found
            with self.assertRaises(FileNotFoundError):
                list(TextFileHelper.load_as_stream("nonexistent_file.txt"))

        finally:
            os.unlink(large_file_path)

    def test_load_as_stream_edge_cases(self):
        """Test edge cases for streaming file loading"""
        # Test file with exactly chunk_size lines
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as exact_file:
            exact_content = [f"Line {i}" for i in range(1, 501)]  # Exactly 500 lines
            exact_file.write("\n".join(exact_content))
            exact_file_path = exact_file.name

        try:
            chunks = list(TextFileHelper.load_as_stream(exact_file_path, chunk_size=500))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(len(chunks[0]), 500)
            self.assertEqual(chunks[0][0], "Line 1")
            self.assertEqual(chunks[0][499], "Line 500")
        finally:
            os.unlink(exact_file_path)

        # Test skip_footer_rows larger than file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as small_file:
            small_file.write("Line 1\nLine 2\nLine 3")
            small_file_path = small_file.name

        try:
            chunks = list(TextFileHelper.load_as_stream(small_file_path, skip_footer_rows=10))
            self.assertEqual(len(chunks), 0)  # All lines skipped
        finally:
            os.unlink(small_file_path)

        # Test skip_header_rows larger than file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as small_file:
            small_file.write("Line 1\nLine 2\nLine 3")
            small_file_path = small_file.name

        try:
            chunks = list(TextFileHelper.load_as_stream(small_file_path, skip_header_rows=10))
            self.assertEqual(len(chunks), 0)  # All lines skipped
        finally:
            os.unlink(small_file_path)

        # Test with whitespace handling
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as whitespace_file:
            whitespace_file.write("  Line 1  \nLine 2\n  Line 3  ")
            whitespace_file_path = whitespace_file.name

        try:
            # Test with strip=True (default)
            chunks = list(TextFileHelper.load_as_stream(whitespace_file_path, chunk_size=100))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0], ["Line 1", "Line 2", "Line 3"])

            # Test with strip=False
            chunks = list(TextFileHelper.load_as_stream(whitespace_file_path, strip=False, chunk_size=100))
            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0], ["  Line 1  ", "Line 2", "  Line 3  "])
        finally:
            os.unlink(whitespace_file_path)


if __name__ == "__main__":
    unittest.main()
