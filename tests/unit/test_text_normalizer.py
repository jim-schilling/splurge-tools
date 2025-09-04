"""Unit tests for text_normalizer.py"""

import unittest

from splurge_tools.text_normalizer import TextNormalizer


class TestTextNormalizer(unittest.TestCase):
    def test_remove_accents(self):
        assert TextNormalizer.remove_accents("café") == "cafe"
        assert TextNormalizer.remove_accents("résumé") == "resume"
        assert TextNormalizer.remove_accents("") == ""
        assert TextNormalizer.remove_accents(None) == ""

    def test_normalize_whitespace(self):
        # Test without preserving newlines
        assert TextNormalizer.normalize_whitespace("hello   world") == "hello world"
        assert TextNormalizer.normalize_whitespace("hello\n\nworld") == "hello world"
        assert TextNormalizer.normalize_whitespace("  hello  world  ") == "hello world"

        # Test with preserving newlines
        assert TextNormalizer.normalize_whitespace("hello\n\nworld", preserve_newlines=True) == "hello\n\nworld"
        assert (
            TextNormalizer.normalize_whitespace("hello   world\n\n  today", preserve_newlines=True)
            == "hello world\n\ntoday"
        )

    def test_remove_special_chars(self):
        assert TextNormalizer.remove_special_chars("hello@world!") == "helloworld"
        assert TextNormalizer.remove_special_chars("hello@world!", keep_chars="@") == "hello@world"
        assert TextNormalizer.remove_special_chars("") == ""
        assert TextNormalizer.remove_special_chars(None) == ""

    def test_normalize_line_endings(self):
        assert TextNormalizer.normalize_line_endings("hello\r\nworld") == "hello\nworld"
        assert TextNormalizer.normalize_line_endings("hello\rworld") == "hello\nworld"
        assert TextNormalizer.normalize_line_endings("hello\nworld", line_ending="\r\n") == "hello\r\nworld"

    def test_to_ascii(self):
        assert TextNormalizer.to_ascii("café") == "cafe"
        assert TextNormalizer.to_ascii("résumé") == "resume"
        assert TextNormalizer.to_ascii("café", replacement="x") == "cafe"

    def test_remove_control_chars(self):
        assert TextNormalizer.remove_control_chars("hello\x00world") == "helloworld"
        assert TextNormalizer.remove_control_chars("hello\x1fworld") == "helloworld"

    def test_normalize_quotes(self):
        # Test with double quotes
        assert TextNormalizer.normalize_quotes('hello "world"') == 'hello "world"'
        # Test with single quotes
        assert TextNormalizer.normalize_quotes("hello 'world'") == 'hello "world"'
        # Test with mixed quotes
        assert TextNormalizer.normalize_quotes('hello "world\'s"') == 'hello "world\'s"'
        # Test with custom quote character
        assert TextNormalizer.normalize_quotes("hello 'world'", quote_char="'") == "hello 'world'"
        # Test with empty string
        assert TextNormalizer.normalize_quotes("") == ""
        # Test with None
        assert TextNormalizer.normalize_quotes(None) == ""
        # Test with apostrophes
        assert TextNormalizer.normalize_quotes("it's a 'test'") == 'it\'s a "test"'

    def test_normalize_dashes(self):
        assert TextNormalizer.normalize_dashes("hello–world") == "hello-world"
        assert TextNormalizer.normalize_dashes("hello—world") == "hello-world"
        # Test with existing dash
        assert TextNormalizer.normalize_dashes("hello-world") == "hello-world"
        # Test with custom dash character
        assert TextNormalizer.normalize_dashes("hello–world", dash_char="_") == "hello_world"

    def test_normalize_spaces(self):
        assert TextNormalizer.normalize_spaces("hello\xa0world") == "hello world"
        assert TextNormalizer.normalize_spaces("hello  world") == "hello world"

    def test_normalize_case(self):
        assert TextNormalizer.normalize_case("Hello World", case="lower") == "hello world"
        assert TextNormalizer.normalize_case("hello world", case="upper") == "HELLO WORLD"
        assert TextNormalizer.normalize_case("hello world", case="title") == "Hello World"
        assert TextNormalizer.normalize_case("hello world", case="sentence") == "Hello world"

    def test_remove_duplicate_chars(self):
        # Test default behavior (spaces and dashes)
        assert TextNormalizer.remove_duplicate_chars("hello   world") == "hello world"
        assert TextNormalizer.remove_duplicate_chars("hello--world") == "hello-world"

        # Test with periods
        assert TextNormalizer.remove_duplicate_chars("hello...world") == "hello.world"

        # Test with custom characters
        assert TextNormalizer.remove_duplicate_chars("hello...world---today", chars=".-") == "hello.world-today"

        # Test with no duplicates
        assert TextNormalizer.remove_duplicate_chars("hello world") == "hello world"


if __name__ == "__main__":
    unittest.main()
