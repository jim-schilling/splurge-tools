"""Streaming tests for TextFileHelper class."""

import os
import tempfile
import unittest

from splurge_tools.text_file_helper import TextFileHelper
from splurge_tools.exceptions import SplurgeFileNotFoundError, SplurgeValidationError


class TestTextFileHelperStreaming(unittest.TestCase):
    """Test cases for TextFileHelper streaming functionality."""

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
            with self.assertRaises(SplurgeValidationError):
                list(TextFileHelper.load_as_stream(large_file_path, chunk_size=50))

            # Test file not found
            with self.assertRaises(SplurgeFileNotFoundError):
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