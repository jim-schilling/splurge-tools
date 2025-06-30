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


if __name__ == "__main__":
    unittest.main()
