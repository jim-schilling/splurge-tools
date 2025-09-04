"""
Tests for the string_tokenizer module.

Tests all public methods of the StringTokenizer class including
parsing, multiple string processing, and bookend removal.
"""

import pytest

from splurge_tools.exceptions import SplurgeParameterError
from splurge_tools.string_tokenizer import StringTokenizer


class TestStringTokenizerParse:
    """Test the parse method."""

    def test_basic_parsing(self) -> None:
        """Test basic string parsing with comma delimiter."""
        result = StringTokenizer.parse("a,b,c", delimiter=",")
        assert result == ["a", "b", "c"]

    def test_parsing_with_spaces(self) -> None:
        """Test parsing with spaces around delimiter."""
        result = StringTokenizer.parse("a , b , c", delimiter=",")
        assert result == ["a", "b", "c"]

    def test_parsing_without_strip(self) -> None:
        """Test parsing without stripping whitespace."""
        result = StringTokenizer.parse("a , b , c", delimiter=",", strip=False)
        assert result == ["a ", " b ", " c"]

    def test_parsing_with_empty_tokens(self) -> None:
        """Test parsing with empty tokens."""
        result = StringTokenizer.parse("a,,c", delimiter=",")
        assert result == ["a", "", "c"]

    def test_parsing_with_empty_tokens_no_strip(self) -> None:
        """Test parsing with empty tokens without stripping."""
        result = StringTokenizer.parse("a,,c", delimiter=",", strip=False)
        assert result == ["a", "", "c"]

    def test_parsing_with_tab_delimiter(self) -> None:
        """Test parsing with tab delimiter."""
        result = StringTokenizer.parse("a\tb\tc", delimiter="\t")
        assert result == ["a", "b", "c"]

    def test_parsing_with_pipe_delimiter(self) -> None:
        """Test parsing with pipe delimiter."""
        result = StringTokenizer.parse("a|b|c", delimiter="|")
        assert result == ["a", "b", "c"]

    def test_parsing_with_semicolon_delimiter(self) -> None:
        """Test parsing with semicolon delimiter."""
        result = StringTokenizer.parse("a;b;c", delimiter=";")
        assert result == ["a", "b", "c"]

    def test_parsing_empty_string(self) -> None:
        """Test parsing an empty string."""
        result = StringTokenizer.parse("", delimiter=",", strip=False)
        assert result == [""]

    def test_parsing_empty_string_stripped(self) -> None:
        """Test parsing an empty string with strip=True."""
        result = StringTokenizer.parse("   ", delimiter=",", strip=True)
        assert result == []

    def test_parsing_none_content(self) -> None:
        """Test parsing None content."""
        result = StringTokenizer.parse(None, delimiter=",")
        assert result == []

    def test_parsing_single_token(self) -> None:
        """Test parsing a string with no delimiter."""
        result = StringTokenizer.parse("single", delimiter=",")
        assert result == ["single"]

    def test_parsing_with_multiple_spaces(self) -> None:
        """Test parsing with multiple spaces between tokens."""
        result = StringTokenizer.parse("a   b   c", delimiter=" ", strip=False)
        assert result == ["a", "", "", "b", "", "", "c"]

    def test_parsing_with_multiple_spaces_stripped(self) -> None:
        """Test parsing with multiple spaces between tokens, stripped."""
        result = StringTokenizer.parse("a   b   c", delimiter=" ", strip=True)
        assert result == ["a", "", "", "b", "", "", "c"]

    def test_parsing_with_empty_delimiter_raises_error(self) -> None:
        """Test that empty delimiter raises SplurgeParameterError."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            StringTokenizer.parse("a,b,c", delimiter="")

    def test_parsing_with_none_delimiter_raises_error(self) -> None:
        """Test that None delimiter raises SplurgeParameterError."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            StringTokenizer.parse("a,b,c", delimiter=None)


class TestStringTokenizerParses:
    """Test the parses method."""

    def test_parsing_multiple_strings(self) -> None:
        """Test parsing multiple strings."""
        content = ["a,b,c", "d,e,f", "g,h,i"]
        result = StringTokenizer.parses(content, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
        assert result == expected

    def test_parsing_multiple_strings_with_spaces(self) -> None:
        """Test parsing multiple strings with spaces."""
        content = ["a , b , c", "d , e , f"]
        result = StringTokenizer.parses(content, delimiter=",")
        expected = [["a", "b", "c"], ["d", "e", "f"]]
        assert result == expected

    def test_parsing_multiple_strings_without_strip(self) -> None:
        """Test parsing multiple strings without stripping."""
        content = ["a , b , c", "d , e , f"]
        result = StringTokenizer.parses(content, delimiter=",", strip=False)
        expected = [["a ", " b ", " c"], ["d ", " e ", " f"]]
        assert result == expected

    def test_parsing_empty_list(self) -> None:
        """Test parsing an empty list."""
        result = StringTokenizer.parses([], delimiter=",")
        assert result == []

    def test_parsing_list_with_empty_strings(self) -> None:
        """Test parsing a list with empty strings."""
        content = ["", "a,b", ""]
        result = StringTokenizer.parses(content, delimiter=",", strip=False)
        expected = [[""], ["a", "b"], [""]]
        assert result == expected

    def test_parsing_list_with_empty_strings_stripped(self) -> None:
        """Test parsing a list with empty strings, stripped."""
        content = ["   ", "a,b", "   "]
        result = StringTokenizer.parses(content, delimiter=",", strip=True)
        expected = [[], ["a", "b"], []]
        assert result == expected

    def test_parsing_with_different_delimiters(self) -> None:
        """Test parsing with different delimiters."""
        content = ["a|b|c", "d;e;f", "g\th\ti"]
        result_pipe = StringTokenizer.parses(content, delimiter="|")
        result_semicolon = StringTokenizer.parses(content, delimiter=";")
        result_tab = StringTokenizer.parses(content, delimiter="\t")
        
        assert result_pipe == [["a", "b", "c"], ["d;e;f"], ["g\th\ti"]]
        assert result_semicolon == [["a|b|c"], ["d", "e", "f"], ["g\th\ti"]]
        assert result_tab == [["a|b|c"], ["d;e;f"], ["g", "h", "i"]]

    def test_parsing_with_empty_delimiter_raises_error(self) -> None:
        """Test that empty delimiter raises SplurgeParameterError."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            StringTokenizer.parses(["a,b,c"], delimiter="")

    def test_parsing_with_none_delimiter_raises_error(self) -> None:
        """Test that None delimiter raises SplurgeParameterError."""
        with pytest.raises(SplurgeParameterError, match="delimiter cannot be empty or None"):
            StringTokenizer.parses(["a,b,c"], delimiter=None)


class TestStringTokenizerRemoveBookends:
    """Test the remove_bookends method."""

    def test_remove_single_quotes(self) -> None:
        """Test removing single quotes from both ends."""
        result = StringTokenizer.remove_bookends("'hello'", bookend="'")
        assert result == "hello"

    def test_remove_double_quotes(self) -> None:
        """Test removing double quotes from both ends."""
        result = StringTokenizer.remove_bookends('"hello"', bookend='"')
        assert result == "hello"

    def test_remove_brackets(self) -> None:
        """Test removing brackets from both ends."""
        # Since [hello] doesn't end with [, nothing is removed
        result = StringTokenizer.remove_bookends("[hello]", bookend="[")
        assert result == "[hello]"
        
    def test_remove_matching_brackets(self) -> None:
        """Test removing matching brackets from both ends."""
        # Since [hello] doesn't end with [, nothing is removed
        result = StringTokenizer.remove_bookends("[hello]", bookend="[")
        assert result == "[hello]"
        
    def test_remove_matching_quotes(self) -> None:
        """Test removing matching quotes from both ends."""
        result = StringTokenizer.remove_bookends("'hello'", bookend="'")
        assert result == "hello"
        
    def test_remove_matching_brackets_both_ends(self) -> None:
        """Test removing matching brackets when they appear on both ends."""
        result = StringTokenizer.remove_bookends("[hello]", bookend="[")
        assert result == "[hello]"
        
    def test_remove_matching_parentheses_both_ends(self) -> None:
        """Test removing matching parentheses when they appear on both ends."""
        result = StringTokenizer.remove_bookends("(hello)", bookend="(")
        assert result == "(hello)"
        
    def test_remove_matching_brackets_actual(self) -> None:
        """Test removing matching brackets when they actually match on both ends."""
        result = StringTokenizer.remove_bookends("[hello[", bookend="[")
        assert result == "hello"
        
    def test_remove_matching_parentheses_actual(self) -> None:
        """Test removing matching parentheses when they actually match on both ends."""
        result = StringTokenizer.remove_bookends("(hello(", bookend="(")
        assert result == "hello"
        
    def test_remove_matching_double_brackets(self) -> None:
        """Test removing matching double brackets when they actually match on both ends."""
        result = StringTokenizer.remove_bookends("[[hello[[", bookend="[[")
        assert result == "hello"

    def test_remove_parentheses(self) -> None:
        """Test removing parentheses from both ends."""
        # Since (hello) doesn't end with (, nothing is removed
        result = StringTokenizer.remove_bookends("(hello)", bookend="(")
        assert result == "(hello)"

    def test_remove_with_spaces(self) -> None:
        """Test removing bookends with spaces."""
        result = StringTokenizer.remove_bookends(" 'hello' ", bookend="'")
        assert result == "hello"

    def test_remove_without_strip(self) -> None:
        """Test removing bookends without stripping."""
        result = StringTokenizer.remove_bookends(" 'hello' ", bookend="'", strip=False)
        assert result == " 'hello' "

    def test_remove_partial_bookends(self) -> None:
        """Test behavior when only one bookend is present."""
        result = StringTokenizer.remove_bookends("'hello", bookend="'")
        assert result == "'hello"

    def test_remove_no_bookends(self) -> None:
        """Test behavior when no bookends are present."""
        result = StringTokenizer.remove_bookends("hello", bookend="'")
        assert result == "hello"

    def test_remove_single_character_bookend(self) -> None:
        """Test removing single character bookend."""
        result = StringTokenizer.remove_bookends("'a'", bookend="'")
        assert result == "a"

    def test_remove_empty_string(self) -> None:
        """Test removing bookends from empty string."""
        result = StringTokenizer.remove_bookends("", bookend="'")
        assert result == ""

    def test_remove_whitespace_only(self) -> None:
        """Test removing bookends from whitespace-only string."""
        result = StringTokenizer.remove_bookends("   ", bookend="'")
        assert result == ""

    def test_remove_whitespace_only_no_strip(self) -> None:
        """Test removing bookends from whitespace-only string without strip."""
        result = StringTokenizer.remove_bookends("   ", bookend="'", strip=False)
        assert result == "   "

    def test_remove_with_empty_bookend_raises_error(self) -> None:
        """Test that empty bookend raises SplurgeParameterError."""
        with pytest.raises(SplurgeParameterError, match="bookend cannot be empty or None"):
            StringTokenizer.remove_bookends("'hello'", bookend="")

    def test_remove_with_none_bookend_raises_error(self) -> None:
        """Test that None bookend raises SplurgeParameterError."""
        with pytest.raises(SplurgeParameterError, match="bookend cannot be empty or None"):
            StringTokenizer.remove_bookends("'hello'", bookend=None)

    def test_remove_with_multiple_character_bookend(self) -> None:
        """Test removing multi-character bookend."""
        # Since [[hello]] doesn't end with [[, nothing is removed
        result = StringTokenizer.remove_bookends("[[hello]]", bookend="[[")
        assert result == "[[hello]]"

    def test_remove_with_complex_bookend(self) -> None:
        """Test removing complex bookend pattern."""
        # Since STARThelloEND doesn't end with START, nothing is removed
        result = StringTokenizer.remove_bookends("STARThelloEND", bookend="START")
        assert result == "STARThelloEND"


class TestStringTokenizerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_with_unicode_delimiter(self) -> None:
        """Test parsing with Unicode delimiter."""
        result = StringTokenizer.parse("a→b→c", delimiter="→")
        assert result == ["a", "b", "c"]

    def test_parse_with_unicode_content(self) -> None:
        """Test parsing with Unicode content."""
        result = StringTokenizer.parse("α,β,γ", delimiter=",")
        assert result == ["α", "β", "γ"]

    def test_remove_bookends_with_unicode(self) -> None:
        """Test removing bookends with Unicode content."""
        # Since «αβγ» doesn't end with «, nothing is removed
        result = StringTokenizer.remove_bookends("«αβγ»", bookend="«")
        assert result == "«αβγ»"
        
    def test_remove_bookends_with_matching_unicode(self) -> None:
        """Test removing matching Unicode bookends from both ends."""
        # String starts and ends with «, so both should be removed
        result = StringTokenizer.remove_bookends("«αβγ«", bookend="«")
        assert result == "αβγ"

    def test_parse_with_newlines(self) -> None:
        """Test parsing with newlines in content."""
        result = StringTokenizer.parse("a\n,b\n,c", delimiter=",", strip=False)
        assert result == ["a\n", "b\n", "c"]

    def test_parse_with_tabs(self) -> None:
        """Test parsing with tabs in content."""
        result = StringTokenizer.parse("a\t,b\t,c", delimiter=",", strip=False)
        assert result == ["a\t", "b\t", "c"]

    def test_parse_with_mixed_whitespace(self) -> None:
        """Test parsing with mixed whitespace."""
        result = StringTokenizer.parse("a \t,b \t,c", delimiter=",", strip=False)
        assert result == ["a \t", "b \t", "c"]

    def test_parse_with_mixed_whitespace_stripped(self) -> None:
        """Test parsing with mixed whitespace, stripped."""
        result = StringTokenizer.parse("a \t,b \t,c", delimiter=",", strip=True)
        assert result == ["a", "b", "c"]

    def test_parses_with_mixed_content(self) -> None:
        """Test parsing multiple strings with mixed content."""
        content = ["a,b,c", "", "d,e,f", "   ", "g,h,i"]
        result = StringTokenizer.parses(content, delimiter=",", strip=False)
        expected = [["a", "b", "c"], [""], ["d", "e", "f"], ["   "], ["g", "h", "i"]]
        assert result == expected

    def test_parses_with_mixed_content_stripped(self) -> None:
        """Test parsing multiple strings with mixed content, stripped."""
        content = ["a,b,c", "", "d,e,f", "   ", "g,h,i"]
        result = StringTokenizer.parses(content, delimiter=",", strip=True)
        expected = [["a", "b", "c"], [], ["d", "e", "f"], [], ["g", "h", "i"]]
        assert result == expected
