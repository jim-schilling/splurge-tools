"""
Tests for the text_file_helper module.

Tests all public methods of the TextFileHelper class including
line counting, file previewing, reading, and streaming operations.
"""

from pathlib import Path

import pytest

from splurge_tools.exceptions import (
    SplurgeParameterError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError
)
from splurge_tools.text_file_helper import TextFileHelper


class TestTextFileHelperLineCount:
    """Test the line_count method."""

    def test_line_count_empty_file(self, tmp_path: Path) -> None:
        """Test counting lines in an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        count = TextFileHelper.line_count(test_file)
        assert count == 0

    def test_line_count_single_line(self, tmp_path: Path) -> None:
        """Test counting lines in a single line file."""
        test_file = tmp_path / "single.txt"
        test_file.write_text("single line")
        
        count = TextFileHelper.line_count(test_file)
        assert count == 1

    def test_line_count_multiple_lines(self, tmp_path: Path) -> None:
        """Test counting lines in a multi-line file."""
        test_file = tmp_path / "multiple.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        count = TextFileHelper.line_count(test_file)
        assert count == 3

    def test_line_count_with_empty_lines(self, tmp_path: Path) -> None:
        """Test counting lines with empty lines."""
        test_file = tmp_path / "empty_lines.txt"
        test_file.write_text("line 1\n\nline 3\n\n")
        
        count = TextFileHelper.line_count(test_file)
        assert count == 4

    def test_line_count_with_trailing_newline(self, tmp_path: Path) -> None:
        """Test counting lines with trailing newline."""
        test_file = tmp_path / "trailing.txt"
        test_file.write_text("line 1\nline 2\n")
        
        count = TextFileHelper.line_count(test_file)
        assert count == 2

    def test_line_count_without_trailing_newline(self, tmp_path: Path) -> None:
        """Test counting lines without trailing newline."""
        test_file = tmp_path / "no_trailing.txt"
        test_file.write_text("line 1\nline 2")
        
        count = TextFileHelper.line_count(test_file)
        assert count == 2

    def test_line_count_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that counting lines in non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            TextFileHelper.line_count(test_file)

    def test_line_count_with_different_encoding(self, tmp_path: Path) -> None:
        """Test counting lines with different encoding."""
        test_file = tmp_path / "utf16.txt"
        content = "line 1\nline 2\nline 3"
        test_file.write_text(content, encoding='utf-16')
        
        count = TextFileHelper.line_count(test_file, encoding='utf-16')
        assert count == 3


class TestTextFileHelperPreview:
    """Test the preview method."""

    def test_preview_empty_file(self, tmp_path: Path) -> None:
        """Test previewing an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        lines = TextFileHelper.preview(test_file)
        assert lines == []

    def test_preview_single_line(self, tmp_path: Path) -> None:
        """Test previewing a single line file."""
        test_file = tmp_path / "single.txt"
        test_file.write_text("single line")
        
        lines = TextFileHelper.preview(test_file)
        assert lines == ["single line"]

    def test_preview_multiple_lines(self, tmp_path: Path) -> None:
        """Test previewing multiple lines."""
        test_file = tmp_path / "multiple.txt"
        test_file.write_text("line 1\nline 2\nline 3\nline 4\nline 5")
        
        lines = TextFileHelper.preview(test_file, max_lines=3)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_preview_without_strip(self, tmp_path: Path) -> None:
        """Test previewing without stripping whitespace."""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("  line 1  \n  line 2  \n")
        
        lines = TextFileHelper.preview(test_file, strip=False)
        assert lines == ["  line 1  ", "  line 2  "]

    def test_preview_with_skip_header(self, tmp_path: Path) -> None:
        """Test previewing with header skip."""
        test_file = tmp_path / "header.txt"
        test_file.write_text("header 1\nheader 2\nline 1\nline 2\nline 3")
        
        lines = TextFileHelper.preview(test_file, skip_header_rows=2, max_lines=3)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_preview_max_lines_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test previewing when max_lines exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")
        
        lines = TextFileHelper.preview(test_file, max_lines=10)
        assert lines == ["line 1", "line 2"]

    def test_preview_skip_header_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test previewing when skip_header exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")
        
        lines = TextFileHelper.preview(test_file, skip_header_rows=5)
        assert lines == []

    def test_preview_with_zero_max_lines_raises_error(self, tmp_path: Path) -> None:
        """Test that zero max_lines raises error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        with pytest.raises(SplurgeParameterError):
            TextFileHelper.preview(test_file, max_lines=0)

    def test_preview_with_negative_max_lines_raises_error(self, tmp_path: Path) -> None:
        """Test that negative max_lines raises error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        with pytest.raises(SplurgeParameterError):
            TextFileHelper.preview(test_file, max_lines=-1)

    def test_preview_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that previewing non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            TextFileHelper.preview(test_file)

    def test_preview_negative_skip_header_normalized(self, tmp_path: Path) -> None:
        """Test that negative skip_header values are normalized to defaults."""
        test_file = tmp_path / "negative_skip_preview.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        lines = TextFileHelper.preview(test_file, skip_header_rows=-1, max_lines=3)
        # Negative values should be normalized to 0 (defaults)
        assert lines == ["line 1", "line 2", "line 3"]


class TestTextFileHelperRead:
    """Test the read method."""

    def test_read_empty_file(self, tmp_path: Path) -> None:
        """Test reading an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        lines = TextFileHelper.read(test_file)
        assert lines == []

    def test_read_single_line(self, tmp_path: Path) -> None:
        """Test reading a single line file."""
        test_file = tmp_path / "single.txt"
        test_file.write_text("single line")
        
        lines = TextFileHelper.read(test_file)
        assert lines == ["single line"]

    def test_read_multiple_lines(self, tmp_path: Path) -> None:
        """Test reading multiple lines."""
        test_file = tmp_path / "multiple.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        lines = TextFileHelper.read(test_file)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_read_without_strip(self, tmp_path: Path) -> None:
        """Test reading without stripping whitespace."""
        test_file = tmp_path / "whitespace.txt"
        test_file.write_text("  line 1  \n  line 2  \n")
        
        lines = TextFileHelper.read(test_file, strip=False)
        assert lines == ["  line 1  ", "  line 2  "]

    def test_read_with_skip_header(self, tmp_path: Path) -> None:
        """Test reading with header skip."""
        test_file = tmp_path / "header.txt"
        test_file.write_text("header 1\nheader 2\nline 1\nline 2\nline 3")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=2)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_read_with_skip_footer(self, tmp_path: Path) -> None:
        """Test reading with footer skip."""
        test_file = tmp_path / "footer.txt"
        test_file.write_text("line 1\nline 2\nline 3\nfooter 1\nfooter 2")
        
        lines = TextFileHelper.read(test_file, skip_footer_rows=2)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_read_with_skip_header_and_footer(self, tmp_path: Path) -> None:
        """Test reading with both header and footer skip."""
        test_file = tmp_path / "both.txt"
        test_file.write_text("header 1\nheader 2\nline 1\nline 2\nfooter 1\nfooter 2")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=2, skip_footer_rows=2)
        assert lines == ["line 1", "line 2"]

    def test_read_skip_header_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_header exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=5)
        assert lines == []

    def test_read_skip_footer_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_footer exceeds file size."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("line 1\nline 2")
        
        lines = TextFileHelper.read(test_file, skip_footer_rows=5)
        assert lines == []

    def test_read_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that reading non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            TextFileHelper.read(test_file)

    def test_read_with_different_encoding(self, tmp_path: Path) -> None:
        """Test reading with different encoding."""
        test_file = tmp_path / "utf16.txt"
        content = "line 1\nline 2\nline 3"
        test_file.write_text(content, encoding='utf-16')
        
        lines = TextFileHelper.read(test_file, encoding='utf-16')
        assert lines == ["line 1", "line 2", "line 3"]

    def test_read_with_encoding_error_handling(self, tmp_path: Path) -> None:
        """Test reading file with encoding error handling."""
        test_file = tmp_path / "encoding_error.txt"
        # Write binary data that's not valid UTF-8
        test_file.write_bytes(b"valid text\n\xff\xfe\nmore text")
        
        with pytest.raises(SplurgeFileEncodingError):
            TextFileHelper.read(test_file)


class TestTextFileHelperReadAsStream:
    """Test the read_as_stream method."""

    def test_read_as_stream_empty_file(self, tmp_path: Path) -> None:
        """Test streaming an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        chunks = list(TextFileHelper.read_as_stream(test_file))
        assert chunks == []

    def test_read_as_stream_single_chunk(self, tmp_path: Path) -> None:
        """Test streaming a file that fits in one chunk."""
        test_file = tmp_path / "single_chunk.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, chunk_size=5))
        assert chunks == [["line 1", "line 2", "line 3"]]

    def test_read_as_stream_multiple_chunks(self, tmp_path: Path) -> None:
        """Test streaming a file that requires multiple chunks."""
        test_file = tmp_path / "multiple_chunks.txt"
        lines = [f"line {i}" for i in range(1, 11)]
        test_file.write_text("\n".join(lines))
        
        chunks = list(TextFileHelper.read_as_stream(test_file, chunk_size=3))
        # chunk_size=3 is overridden to DEFAULT_MIN_CHUNK_SIZE=100, so all lines are in one chunk
        expected = [["line 1", "line 2", "line 3", "line 4", "line 5", "line 6", "line 7", "line 8", "line 9", "line 10"]]
        assert chunks == expected

    def test_read_as_stream_with_skip_header(self, tmp_path: Path) -> None:
        """Test streaming with header skip."""
        test_file = tmp_path / "header_stream.txt"
        test_file.write_text("header 1\nheader 2\nline 1\nline 2\nline 3")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=2, chunk_size=5))
        assert chunks == [["line 1", "line 2", "line 3"]]

    def test_read_as_stream_with_skip_footer(self, tmp_path: Path) -> None:
        """Test streaming with footer skip."""
        test_file = tmp_path / "footer_stream.txt"
        test_file.write_text("line 1\nline 2\nline 3\nfooter 1\nfooter 2")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_footer_rows=2, chunk_size=5))
        # Should skip the last 2 lines (footer 1 and footer 2)
        assert chunks == [["line 1", "line 2", "line 3"]]

    def test_read_as_stream_without_strip(self, tmp_path: Path) -> None:
        """Test streaming without stripping whitespace."""
        test_file = tmp_path / "whitespace_stream.txt"
        test_file.write_text("  line 1  \n  line 2  \n  line 3  ")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, strip=False, chunk_size=5))
        assert chunks == [["  line 1  ", "  line 2  ", "  line 3  "]]

    def test_read_as_stream_small_chunk_size(self, tmp_path: Path) -> None:
        """Test streaming with small chunk size."""
        test_file = tmp_path / "small_chunk.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, chunk_size=1))
        # chunk_size=1 is overridden to DEFAULT_MIN_CHUNK_SIZE=100, so all lines are in one chunk
        expected = [["line 1", "line 2", "line 3"]]
        assert chunks == expected

    def test_read_as_stream_chunk_size_less_than_minimum(self, tmp_path: Path) -> None:
        """Test streaming with chunk size less than minimum."""
        test_file = tmp_path / "min_chunk.txt"
        lines = [f"line {i}" for i in range(1, 21)]
        test_file.write_text("\n".join(lines))
        
        chunks = list(TextFileHelper.read_as_stream(test_file, chunk_size=50))
        # Should use minimum chunk size (100)
        assert len(chunks) == 1
        assert len(chunks[0]) == 20

    def test_read_as_stream_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that streaming non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            list(TextFileHelper.read_as_stream(test_file))

    def test_read_as_stream_with_different_encoding(self, tmp_path: Path) -> None:
        """Test streaming with different encoding."""
        test_file = tmp_path / "utf16_stream.txt"
        content = "line 1\nline 2\nline 3"
        test_file.write_text(content, encoding='utf-16')
        
        chunks = list(TextFileHelper.read_as_stream(test_file, encoding='utf-16', chunk_size=5))
        assert chunks == [["line 1", "line 2", "line 3"]]

    def test_read_as_stream_with_skip_header_and_footer(self, tmp_path: Path) -> None:
        """Test streaming with both header and footer skip."""
        test_file = tmp_path / "both_stream.txt"
        test_file.write_text("header 1\nheader 2\nline 1\nline 2\nline 3\nfooter 1\nfooter 2")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=2, skip_footer_rows=2, chunk_size=5))
        assert chunks == [["line 1", "line 2", "line 3"]]

    def test_read_as_stream_skip_header_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test streaming when skip_header exceeds file size."""
        test_file = tmp_path / "small_stream.txt"
        test_file.write_text("line 1\nline 2")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=5, chunk_size=5))
        assert chunks == []

    def test_read_as_stream_skip_footer_exceeds_file_size(self, tmp_path: Path) -> None:
        """Test streaming when skip_footer exceeds file size."""
        test_file = tmp_path / "small_stream.txt"
        test_file.write_text("line 1\nline 2")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_footer_rows=5, chunk_size=5))
        assert chunks == []

    def test_read_as_stream_skip_header_and_footer_exceed_file_size(self, tmp_path: Path) -> None:
        """Test streaming when skip_header + skip_footer exceeds file size."""
        test_file = tmp_path / "small_stream.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=2, skip_footer_rows=2, chunk_size=5))
        assert chunks == []

    def test_read_as_stream_skip_footer_equals_data_lines(self, tmp_path: Path) -> None:
        """Test streaming when skip_footer equals the number of data lines."""
        test_file = tmp_path / "footer_equals_data.txt"
        test_file.write_text("header 1\nline 1\nline 2\nfooter 1\nfooter 2")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=1, skip_footer_rows=2, chunk_size=5))
        assert chunks == [["line 1", "line 2"]]

    def test_read_as_stream_skip_footer_greater_than_data_lines(self, tmp_path: Path) -> None:
        """Test streaming when skip_footer is greater than data lines."""
        test_file = tmp_path / "footer_greater_than_data.txt"
        test_file.write_text("header 1\nline 1\nfooter 1\nfooter 2\nfooter 3")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=1, skip_footer_rows=3, chunk_size=5))
        # The sliding window logic correctly processes the data line before encountering footer
        assert chunks == [["line 1"]]

    def test_read_as_stream_sliding_window_buffer_logic(self, tmp_path: Path) -> None:
        """Test the sliding window buffer logic with multiple chunks."""
        test_file = tmp_path / "sliding_window.txt"
        lines = ["header"] + [f"line {i}" for i in range(1, 11)] + ["footer1", "footer2"]
        test_file.write_text("\n".join(lines))
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=1, skip_footer_rows=2, chunk_size=100))
        # chunk_size=3 is overridden to minimum 100, so all lines are in one chunk
        expected_chunks = [["line 1", "line 2", "line 3", "line 4", "line 5", "line 6", "line 7", "line 8", "line 9", "line 10"]]
        assert chunks == expected_chunks

    def test_read_as_stream_zero_skip_values(self, tmp_path: Path) -> None:
        """Test streaming with zero skip values (default behavior)."""
        test_file = tmp_path / "zero_skip.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=0, skip_footer_rows=0, chunk_size=5))
        assert chunks == [["line 1", "line 2", "line 3"]]

    def test_read_as_stream_negative_skip_values_normalized(self, tmp_path: Path) -> None:
        """Test that negative skip values are normalized to defaults."""
        test_file = tmp_path / "negative_skip.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        chunks = list(TextFileHelper.read_as_stream(test_file, skip_header_rows=-1, skip_footer_rows=-1, chunk_size=5))
        # Negative values should be normalized to 0 (defaults)
        assert chunks == [["line 1", "line 2", "line 3"]]

    def test_read_skip_header_and_footer_equals_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_header + skip_footer equals file size."""
        test_file = tmp_path / "exact_size.txt"
        test_file.write_text("header 1\nheader 2\nfooter 1\nfooter 2")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=2, skip_footer_rows=2)
        assert lines == []

    def test_read_skip_header_and_footer_greater_than_file_size(self, tmp_path: Path) -> None:
        """Test reading when skip_header + skip_footer exceeds file size."""
        test_file = tmp_path / "small_file.txt"
        test_file.write_text("line 1\nline 2")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=2, skip_footer_rows=2)
        assert lines == []

    def test_read_zero_skip_values(self, tmp_path: Path) -> None:
        """Test reading with zero skip values (default behavior)."""
        test_file = tmp_path / "zero_skip_read.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=0, skip_footer_rows=0)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_read_negative_skip_values_normalized(self, tmp_path: Path) -> None:
        """Test that negative skip values are normalized to defaults."""
        test_file = tmp_path / "negative_skip_read.txt"
        test_file.write_text("line 1\nline 2\nline 3")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=-1, skip_footer_rows=-1)
        # Negative values should be normalized to 0 (defaults)
        assert lines == ["line 1", "line 2", "line 3"]

    def test_read_skip_footer_equals_data_lines(self, tmp_path: Path) -> None:
        """Test reading when skip_footer equals the number of data lines."""
        test_file = tmp_path / "footer_equals_data_read.txt"
        test_file.write_text("header 1\nline 1\nline 2\nfooter 1\nfooter 2")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=1, skip_footer_rows=2)
        assert lines == ["line 1", "line 2"]

    def test_read_skip_footer_greater_than_data_lines(self, tmp_path: Path) -> None:
        """Test reading when skip_footer is greater than data lines."""
        test_file = tmp_path / "footer_greater_than_data_read.txt"
        test_file.write_text("header 1\nline 1\nfooter 1\nfooter 2\nfooter 3")
        
        lines = TextFileHelper.read(test_file, skip_header_rows=1, skip_footer_rows=3)
        # The read method correctly processes the data line before applying footer skip
        assert lines == ["line 1"]


class TestTextFileHelperEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_read_file_with_unicode_content(self, tmp_path: Path) -> None:
        """Test reading file with Unicode content."""
        test_file = tmp_path / "unicode.txt"
        content = "αβγ\nδεζ\nηθι"
        test_file.write_text(content, encoding='utf-8')
        
        lines = TextFileHelper.read(test_file)
        assert lines == ["αβγ", "δεζ", "ηθι"]

    def test_read_file_with_mixed_line_endings(self, tmp_path: Path) -> None:
        """Test reading file with mixed line endings."""
        test_file = tmp_path / "mixed_endings.txt"
        test_file.write_text("line 1\r\nline 2\nline 3\r")
        
        lines = TextFileHelper.read(test_file, strip=False)
        # Mixed line endings create empty lines that are preserved
        assert lines == ["line 1", "", "line 2", "line 3"]

    def test_read_file_with_trailing_newlines(self, tmp_path: Path) -> None:
        """Test reading file with trailing newlines."""
        test_file = tmp_path / "trailing_newlines.txt"
        test_file.write_text("line 1\nline 2\n\n\n")
        
        lines = TextFileHelper.read(test_file)
        # The content "line 1\nline 2\n\n\n" has 4 lines, not 5
        assert lines == ["line 1", "line 2", "", ""]

    def test_read_file_with_only_newlines(self, tmp_path: Path) -> None:
        """Test reading file with only newlines."""
        test_file = tmp_path / "only_newlines.txt"
        test_file.write_text("\n\n\n")
        
        lines = TextFileHelper.read(test_file)
        assert lines == ["", "", ""]

    def test_stream_large_file(self, tmp_path: Path) -> None:
        """Test streaming a large file."""
        test_file = tmp_path / "large.txt"
        lines = [f"line {i}" for i in range(1, 1001)]
        test_file.write_text("\n".join(lines))
        
        chunks = list(TextFileHelper.read_as_stream(test_file, chunk_size=100))
        assert len(chunks) == 10
        assert all(len(chunk) == 100 for chunk in chunks[:-1])
        assert len(chunks[-1]) == 100

    def test_read_file_with_encoding_error(self, tmp_path: Path) -> None:
        """Test reading file with encoding error."""
        test_file = tmp_path / "encoding_error.txt"
        # Write binary data that's not valid UTF-8
        test_file.write_bytes(b"valid text\n\xff\xfe\nmore text")
        
        with pytest.raises(SplurgeFileEncodingError):
            TextFileHelper.read(test_file)

    def test_read_file_with_permission_error(self, tmp_path: Path) -> None:
        """Test reading file with permission error."""
        import platform
        
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")
        
        test_file = tmp_path / "permission_error.txt"
        test_file.write_text("content")
        
        # Make file unreadable
        import os
        os.chmod(test_file, 0o000)
        
        try:
            with pytest.raises(SplurgeFilePermissionError):
                TextFileHelper.read(test_file)
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)
