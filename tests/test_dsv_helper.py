"""
Tests for the dsv_helper module.

Tests all public methods of the DsvHelper class including
parsing, file operations, and streaming functionality.
"""

from pathlib import Path

import pytest

from splurge_tools.exceptions import (
    SplurgeParameterError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError
)
from splurge_tools.dsv_helper import DsvHelper


class TestDsvHelperParse:
    """Test the parse method."""

    def test_parse_basic_csv(self) -> None:
        """Test basic CSV parsing."""
        result = DsvHelper.parse("a,b,c", delimiter=",")
        assert result == ["a", "b", "c"]

    def test_parse_tsv(self) -> None:
        """Test TSV parsing."""
        result = DsvHelper.parse("a\tb\tc", delimiter="\t")
        assert result == ["a", "b", "c"]

    def test_parse_pipe_separated(self) -> None:
        """Test pipe-separated values."""
        result = DsvHelper.parse("a|b|c", delimiter="|")
        assert result == ["a", "b", "c"]

    def test_parse_semicolon_separated(self) -> None:
        """Test semicolon-separated values."""
        result = DsvHelper.parse("a;b;c", delimiter=";")
        assert result == ["a", "b", "c"]

    def test_parse_with_spaces(self) -> None:
        """Test parsing with spaces around delimiter."""
        result = DsvHelper.parse("a , b , c", delimiter=",")
        assert result == ["a", "b", "c"]

    def test_parse_without_strip(self) -> None:
        """Test parsing without stripping whitespace."""
        result = DsvHelper.parse("a , b , c", delimiter=",", strip=False)
        assert result == ["a ", " b ", " c"]

    def test_parse_with_empty_tokens(self) -> None:
        """Test parsing with empty tokens."""
        result = DsvHelper.parse("a,,c", delimiter=",")
        assert result == ["a", "", "c"]

    def test_parse_with_quoted_values(self) -> None:
        """Test parsing with quoted values."""
        result = DsvHelper.parse('"a","b","c"', delimiter=",", bookend='"')
        assert result == ["a", "b", "c"]

    def test_parse_with_quoted_values_no_strip(self) -> None:
        """Test parsing with quoted values without stripping."""
        result = DsvHelper.parse('"a","b","c"', delimiter=",", bookend='"', bookend_strip=False)
        assert result == ["a", "b", "c"]

    def test_parse_with_mixed_quoted_values(self) -> None:
        """Test parsing with mixed quoted and unquoted values."""
        result = DsvHelper.parse('a,"b",c', delimiter=",", bookend='"')
        assert result == ["a", "b", "c"]

    def test_parse_with_single_quotes(self) -> None:
        """Test parsing with single quotes."""
        result = DsvHelper.parse("'a','b','c'", delimiter=",", bookend="'")
        assert result == ["a", "b", "c"]

    def test_parse_with_brackets(self) -> None:
        """Test parsing with bracket bookends."""
        result = DsvHelper.parse("[a],[b],[c]", delimiter=",", bookend="[")
        assert result == ["[a]", "[b]", "[c]"]

    def test_parse_empty_string(self) -> None:
        """Test parsing empty string."""
        result = DsvHelper.parse("", delimiter=",")
        assert result == []

    def test_parse_empty_string_stripped(self) -> None:
        """Test parsing empty string with strip."""
        result = DsvHelper.parse("   ", delimiter=",", strip=True)
        assert result == []

    def test_parse_single_token(self) -> None:
        """Test parsing single token."""
        result = DsvHelper.parse("single", delimiter=",")
        assert result == ["single"]

    def test_parse_with_empty_delimiter_raises_error(self) -> None:
        """Test that empty delimiter raises error."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parse("a,b,c", delimiter="")

    def test_parse_with_none_delimiter_raises_error(self) -> None:
        """Test that None delimiter raises error."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parse("a,b,c", delimiter=None)


class TestDsvHelperParses:
    """Test the parses method."""

    def test_parses_multiple_lines(self) -> None:
        """Test parsing multiple lines."""
        content = ["a,b,c", "d,e,f", "g,h,i"]
        result = DsvHelper.parses(content, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        assert result == expected

    def test_parses_with_spaces(self) -> None:
        """Test parsing multiple lines with spaces."""
        content = ["a , b , c", "d , e , f"]
        result = DsvHelper.parses(content, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parses_without_strip(self) -> None:
        """Test parsing multiple lines without stripping."""
        content = ["a , b , c", "d , e , f"]
        result = DsvHelper.parses(content, delimiter=",", strip=False)
        expected = [["a ", " b ", " c"], ["d ", " e ", " f"]]
        assert result == expected

    def test_parses_with_quoted_values(self) -> None:
        """Test parsing multiple lines with quoted values."""
        content = ['"a","b","c"', '"d","e","f"']
        result = DsvHelper.parses(content, delimiter=",", bookend='"')
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parses_empty_list(self) -> None:
        """Test parsing empty list."""
        result = DsvHelper.parses([], delimiter=",")
        assert result == []

    def test_parses_list_with_empty_strings(self) -> None:
        """Test parsing list with empty strings."""
        content = ["", "a,b", ""]
        result = DsvHelper.parses(content, delimiter=",")
        expected = [[], ["a", "b"], []]
        assert result == expected

    def test_parses_with_different_delimiters(self) -> None:
        """Test parsing with different delimiters."""
        content = ["a|b|c", "d;e;f", "g\th\ti"]
        result_pipe = DsvHelper.parses(content, delimiter="|")
        result_semicolon = DsvHelper.parses(content, delimiter=";")
        result_tab = DsvHelper.parses(content, delimiter="\t")
        
        assert result_pipe == [["a", "b", "c"], ["d;e;f"], ["g\th\ti"]]
        assert result_semicolon == [["a|b|c"], ["d", "e", "f"], ["g\th\ti"]]
        assert result_tab == [["a|b|c"], ["d;e;f"], ["g", "h", "i"]]

    def test_parses_with_empty_delimiter_raises_error(self) -> None:
        """Test that empty delimiter raises error."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parses(["a,b,c"], delimiter="")

    def test_parses_with_none_delimiter_raises_error(self) -> None:
        """Test that None delimiter raises error."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parses(["a,b,c"], delimiter=None)

    def test_parses_with_non_string_content_raises_error(self) -> None:
        """Test that non-string content raises error."""
        with pytest.raises(SplurgeParameterError, match="content must be a list of strings"):
            DsvHelper.parses(["a,b,c", 123], delimiter=",")

    def test_parses_with_non_list_content_raises_error(self) -> None:
        """Test that non-list content raises error."""
        with pytest.raises(SplurgeParameterError, match="content must be a list"):
            DsvHelper.parses("a,b,c", delimiter=",")


class TestDsvHelperParseFile:
    """Test the parse_file method."""

    def test_parse_file_basic_csv(self, tmp_path: Path) -> None:
        """Test parsing basic CSV file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\nd,e,f\ng,h,i")
        
        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        assert result == expected

    def test_parse_file_tsv(self, tmp_path: Path) -> None:
        """Test parsing TSV file."""
        test_file = tmp_path / "test.tsv"
        test_file.write_text("a\tb\tc\nd\te\tf")
        
        result = DsvHelper.parse_file(test_file, delimiter="\t")
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_quoted_values(self, tmp_path: Path) -> None:
        """Test parsing file with quoted values."""
        test_file = tmp_path / "test.csv"
        test_file.write_text('"a","b","c"\n"d","e","f"')
        
        result = DsvHelper.parse_file(test_file, delimiter=",", bookend='"')
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_skip_header(self, tmp_path: Path) -> None:
        """Test parsing file with header skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2,header3\na,b,c\nd,e,f")
        
        result = DsvHelper.parse_file(test_file, delimiter=",", skip_header_rows=1)
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_skip_footer(self, tmp_path: Path) -> None:
        """Test parsing file with footer skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\nd,e,f\nfooter1,footer2,footer3")
        
        result = DsvHelper.parse_file(test_file, delimiter=",", skip_footer_rows=1)
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_with_skip_header_and_footer(self, tmp_path: Path) -> None:
        """Test parsing file with both header and footer skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2,header3\na,b,c\nd,e,f\nfooter1,footer2,footer3")
        
        result = DsvHelper.parse_file(test_file, delimiter=",", skip_header_rows=1, skip_footer_rows=1)
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_without_strip(self, tmp_path: Path) -> None:
        """Test parsing file without stripping."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a , b , c\nd , e , f")
        
        result = DsvHelper.parse_file(test_file, delimiter=",", strip=False)
        expected = [["a ", " b ", " c"], ["d ", " e ", " f"]]
        assert result == expected

    def test_parse_file_with_different_encoding(self, tmp_path: Path) -> None:
        """Test parsing file with different encoding."""
        test_file = tmp_path / "test.csv"
        content = "a,b,c\nd,e,f"
        test_file.write_text(content, encoding='utf-16')
        
        result = DsvHelper.parse_file(test_file, delimiter=",", encoding='utf-16')
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parse_file_empty(self, tmp_path: Path) -> None:
        """Test parsing empty file."""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("")
        
        result = DsvHelper.parse_file(test_file, delimiter=",")
        assert result == []

    def test_parse_file_single_line(self, tmp_path: Path) -> None:
        """Test parsing single line file."""
        test_file = tmp_path / "single.csv"
        test_file.write_text("a,b,c")
        
        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [["a", "b", "c"]]
        assert result == expected

    def test_parse_file_nonexistent_raises_error(self, tmp_path: Path) -> None:
        """Test that parsing non-existent file raises error."""
        test_file = tmp_path / "nonexistent.csv"
        
        with pytest.raises(SplurgeFileNotFoundError):
            DsvHelper.parse_file(test_file, delimiter=",")

    def test_parse_file_with_empty_delimiter_raises_error(self, tmp_path: Path) -> None:
        """Test that empty delimiter raises error."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c")
        
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            DsvHelper.parse_file(test_file, delimiter="")


class TestDsvHelperParseStream:
    """Test the parse_stream method."""

    def test_parse_stream_basic_csv(self, tmp_path: Path) -> None:
        """Test streaming basic CSV file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\nd,e,f\ng,h,i")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", chunk_size=100))
        expected = [[["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]]
        assert chunks == expected

    def test_parse_stream_tsv(self, tmp_path: Path) -> None:
        """Test streaming TSV file."""
        test_file = tmp_path / "test.tsv"
        test_file.write_text("a\tb\tc\nd\te\tf\ng\th\ti")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter="\t", chunk_size=100))
        expected = [[["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]]
        assert chunks == expected

    def test_parse_stream_with_quoted_values(self, tmp_path: Path) -> None:
        """Test streaming file with quoted values."""
        test_file = tmp_path / "test.csv"
        test_file.write_text('"a","b","c"\n"d","e","f"\n"g","h","i"')
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", bookend='"', chunk_size=100))
        expected = [[["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]]
        assert chunks == expected

    def test_parse_stream_with_skip_header(self, tmp_path: Path) -> None:
        """Test streaming file with header skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2,header3\na,b,c\nd,e,f\ng,h,i")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", skip_header_rows=1, chunk_size=100))
        expected = [[["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]]
        assert chunks == expected

    def test_parse_stream_with_skip_footer(self, tmp_path: Path) -> None:
        """Test streaming file with footer skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c\nd,e,f\ng,h,i\nfooter1,footer2,footer3")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", skip_footer_rows=1, chunk_size=100))
        expected = [[["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]]
        assert chunks == expected

    def test_parse_stream_with_skip_header_and_footer(self, tmp_path: Path) -> None:
        """Test streaming file with both header and footer skip."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("header1,header2,header3\na,b,c\nd,e,f\nfooter1,footer2,footer3")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", skip_header_rows=1, skip_footer_rows=1, chunk_size=2))
        expected = [[["a", "b", "c"], ["d", "e", "f"]]]
        assert chunks == expected

    def test_parse_stream_without_strip(self, tmp_path: Path) -> None:
        """Test streaming file without stripping."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a , b , c\nd , e , f")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", strip=False, chunk_size=2))
        expected = [[["a ", " b ", " c"], ["d ", " e ", " f"]]]
        assert chunks == expected

    def test_parse_stream_with_different_encoding(self, tmp_path: Path) -> None:
        """Test streaming file with different encoding."""
        test_file = tmp_path / "test.csv"
        content = "a,b,c\nd,e,f"
        test_file.write_text(content, encoding='utf-16')
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", encoding='utf-16', chunk_size=2))
        expected = [[["a", "b", "c"], ["d", "e", "f"]]]
        assert chunks == expected

    def test_parse_stream_empty_file(self, tmp_path: Path) -> None:
        """Test streaming empty file."""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", chunk_size=2))
        assert chunks == []

    def test_parse_stream_single_line(self, tmp_path: Path) -> None:
        """Test streaming single line file."""
        test_file = tmp_path / "single.csv"
        test_file.write_text("a,b,c")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", chunk_size=2))
        expected = [[["a", "b", "c"]]]
        assert chunks == expected

    def test_parse_stream_small_chunk_size(self, tmp_path: Path) -> None:
        """Test streaming with small chunk size."""
        test_file = tmp_path / "small.csv"
        test_file.write_text("a,b,c\nd,e,f\ng,h,i")
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", chunk_size=100))
        expected = [[["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]]
        assert chunks == expected

    def test_parse_stream_chunk_size_less_than_minimum(self, tmp_path: Path) -> None:
        """Test streaming with chunk size less than minimum."""
        test_file = tmp_path / "min_chunk.csv"
        lines = [f"a{i},b{i},c{i}" for i in range(1, 21)]
        test_file.write_text("\n".join(lines))
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", chunk_size=50))
        # Should use minimum chunk size (100)
        assert len(chunks) == 1
        assert len(chunks[0]) == 20

    def test_parse_stream_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that streaming non-existent file raises error."""
        test_file = tmp_path / "nonexistent.csv"
        
        with pytest.raises(SplurgeFileNotFoundError):
            list(DsvHelper.parse_stream(test_file, delimiter=","))

    def test_parse_stream_with_empty_delimiter_raises_error(self, tmp_path: Path) -> None:
        """Test that empty delimiter raises error."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("a,b,c")
        
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            list(DsvHelper.parse_stream(test_file, delimiter=""))


class TestDsvHelperEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_with_unicode_content(self) -> None:
        """Test parsing with Unicode content."""
        result = DsvHelper.parse("α,β,γ", delimiter=",")
        assert result == ["α", "β", "γ"]

    def test_parse_with_unicode_delimiter(self) -> None:
        """Test parsing with Unicode delimiter."""
        result = DsvHelper.parse("a→b→c", delimiter="→")
        assert result == ["a", "b", "c"]

    def test_parse_with_newlines_in_content(self) -> None:
        """Test parsing with newlines in content."""
        result = DsvHelper.parse("a\n,b\n,c", delimiter=",", strip=False)
        assert result == ["a\n", "b\n", "c"]

    def test_parse_with_tabs_in_content(self) -> None:
        """Test parsing with tabs in content."""
        result = DsvHelper.parse("a\t,b\t,c", delimiter=",", strip=False)
        assert result == ["a\t", "b\t", "c"]

    def test_parse_file_with_unicode_content(self, tmp_path: Path) -> None:
        """Test parsing file with Unicode content."""
        test_file = tmp_path / "unicode.csv"
        test_file.write_text("α,β,γ\nδε,ζη,θι", encoding='utf-8')
        
        result = DsvHelper.parse_file(test_file, delimiter=",")
        expected = [["α", "β", "γ"], ["δε", "ζη", "θι"]]
        assert result == expected

    def test_parse_file_with_mixed_line_endings(self, tmp_path: Path) -> None:
        """Test parsing file with mixed line endings."""
        test_file = tmp_path / "mixed.csv"
        test_file.write_text("a,b,c\r\nd,e,f\ng,h,i\r")
        
        result = DsvHelper.parse_file(test_file, delimiter=",", strip=False)
        expected = [["a", "b", "c"], [""], ["d", "e", "f"], ["g", "h", "i"]]
        assert result == expected

    def test_parse_file_with_trailing_newlines(self, tmp_path: Path) -> None:
        """Test parsing file with trailing newlines."""
        test_file = tmp_path / "trailing.csv"
        test_file.write_text("a,b,c\n\n\n")
        
        result = DsvHelper.parse_file(test_file, delimiter=",", strip=False)
        expected = [["a", "b", "c"], [""], [""]]
        assert result == expected

    def test_parse_file_with_only_newlines(self, tmp_path: Path) -> None:
        """Test parsing file with only newlines."""
        test_file = tmp_path / "newlines.csv"
        test_file.write_text("\n\n\n")
        
        result = DsvHelper.parse_file(test_file, delimiter=",", strip=False)
        expected = [[""], [""], [""]]
        assert result == expected

    def test_parse_stream_large_file(self, tmp_path: Path) -> None:
        """Test streaming a large file."""
        test_file = tmp_path / "large.csv"
        lines = [f"a{i},b{i},c{i}" for i in range(1, 1001)]
        test_file.write_text("\n".join(lines))
        
        chunks = list(DsvHelper.parse_stream(test_file, delimiter=",", chunk_size=100))
        assert len(chunks) == 10
        assert all(len(chunk) == 100 for chunk in chunks[:-1])
        assert len(chunks[-1]) == 100

    def test_parse_file_with_encoding_error(self, tmp_path: Path) -> None:
        """Test parsing file with encoding error."""
        test_file = tmp_path / "encoding_error.csv"
        # Write binary data that's not valid UTF-8
        test_file.write_bytes(b"a,b,c\n\xff\xfe\nd,e,f")
        
        with pytest.raises(SplurgeFileEncodingError):
            DsvHelper.parse_file(test_file, delimiter=",")

    def test_parse_file_with_permission_error(self, tmp_path: Path) -> None:
        """Test parsing file with permission error."""
        # Skip this test on Windows as permission handling differs
        import platform
        if platform.system() == "Windows":
            pytest.skip("Permission error test not reliable on Windows")
        
        test_file = tmp_path / "permission_error.csv"
        test_file.write_text("a,b,c")
        
        # Make file unreadable
        import os
        os.chmod(test_file, 0o000)
        
        try:
            with pytest.raises(SplurgeFilePermissionError):
                DsvHelper.parse_file(test_file, delimiter=",")
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)
