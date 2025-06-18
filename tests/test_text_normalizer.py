"""Unit tests for text_normalizer.py"""

import unittest
from jpy_tools.text_normalizer import TextNormalizer

class TestTextNormalizer(unittest.TestCase):
    def test_remove_accents(self):
        self.assertEqual(TextNormalizer.remove_accents("café"), "cafe")
        self.assertEqual(TextNormalizer.remove_accents("résumé"), "resume")
        self.assertEqual(TextNormalizer.remove_accents(""), "")
        self.assertEqual(TextNormalizer.remove_accents(None), "")

    def test_normalize_whitespace(self):
        # Test without preserving newlines
        self.assertEqual(TextNormalizer.normalize_whitespace("hello   world"), "hello world")
        self.assertEqual(TextNormalizer.normalize_whitespace("hello\n\nworld"), "hello world")
        self.assertEqual(TextNormalizer.normalize_whitespace("  hello  world  "), "hello world")
        
        # Test with preserving newlines
        self.assertEqual(
            TextNormalizer.normalize_whitespace("hello\n\nworld", preserve_newlines=True),
            "hello\n\nworld"
        )
        self.assertEqual(
            TextNormalizer.normalize_whitespace("hello   world\n\n  today", preserve_newlines=True),
            "hello world\n\ntoday"
        )

    def test_remove_special_chars(self):
        self.assertEqual(TextNormalizer.remove_special_chars("hello@world!"), "helloworld")
        self.assertEqual(TextNormalizer.remove_special_chars("hello@world!", keep_chars="@"), "hello@world")
        self.assertEqual(TextNormalizer.remove_special_chars(""), "")
        self.assertEqual(TextNormalizer.remove_special_chars(None), "")

    def test_normalize_line_endings(self):
        self.assertEqual(TextNormalizer.normalize_line_endings("hello\r\nworld"), "hello\nworld")
        self.assertEqual(TextNormalizer.normalize_line_endings("hello\rworld"), "hello\nworld")
        self.assertEqual(TextNormalizer.normalize_line_endings("hello\nworld", line_ending="\r\n"), "hello\r\nworld")

    def test_to_ascii(self):
        self.assertEqual(TextNormalizer.to_ascii("café"), "cafe")
        self.assertEqual(TextNormalizer.to_ascii("résumé"), "resume")
        self.assertEqual(TextNormalizer.to_ascii("café", replacement="x"), "cafe")

    def test_remove_control_chars(self):
        self.assertEqual(TextNormalizer.remove_control_chars("hello\x00world"), "helloworld")
        self.assertEqual(TextNormalizer.remove_control_chars("hello\x1fworld"), "helloworld")

    def test_normalize_quotes(self):
        # Test with double quotes
        self.assertEqual(TextNormalizer.normalize_quotes('hello "world"'), 'hello "world"')
        # Test with single quotes
        self.assertEqual(TextNormalizer.normalize_quotes("hello 'world'"), 'hello "world"')
        # Test with mixed quotes
        self.assertEqual(TextNormalizer.normalize_quotes('hello "world\'s"'), 'hello "world\'s"')
        # Test with custom quote character
        self.assertEqual(TextNormalizer.normalize_quotes("hello 'world'", quote_char="'"), "hello 'world'")
        # Test with empty string
        self.assertEqual(TextNormalizer.normalize_quotes(""), "")
        # Test with None
        self.assertEqual(TextNormalizer.normalize_quotes(None), "")
        # Test with apostrophes
        self.assertEqual(TextNormalizer.normalize_quotes("it's a 'test'"), 'it\'s a "test"')

    def test_normalize_dashes(self):
        self.assertEqual(TextNormalizer.normalize_dashes("hello–world"), "hello-world")
        self.assertEqual(TextNormalizer.normalize_dashes("hello—world"), "hello-world")
        # Test with existing dash
        self.assertEqual(TextNormalizer.normalize_dashes("hello-world"), "hello-world")
        # Test with custom dash character
        self.assertEqual(TextNormalizer.normalize_dashes("hello–world", dash_char="_"), "hello_world")

    def test_normalize_spaces(self):
        self.assertEqual(TextNormalizer.normalize_spaces("hello\u00A0world"), "hello world")
        self.assertEqual(TextNormalizer.normalize_spaces("hello  world"), "hello world")

    def test_normalize_case(self):
        self.assertEqual(TextNormalizer.normalize_case("Hello World", case="lower"), "hello world")
        self.assertEqual(TextNormalizer.normalize_case("hello world", case="upper"), "HELLO WORLD")
        self.assertEqual(TextNormalizer.normalize_case("hello world", case="title"), "Hello World")
        self.assertEqual(TextNormalizer.normalize_case("hello world", case="sentence"), "Hello world")

    def test_remove_duplicate_chars(self):
        # Test default behavior (spaces and dashes)
        self.assertEqual(TextNormalizer.remove_duplicate_chars("hello   world"), "hello world")
        self.assertEqual(TextNormalizer.remove_duplicate_chars("hello--world"), "hello-world")
        
        # Test with periods
        self.assertEqual(TextNormalizer.remove_duplicate_chars("hello...world"), "hello.world")
        
        # Test with custom characters
        self.assertEqual(TextNormalizer.remove_duplicate_chars("hello...world---today", chars='.-'), "hello.world-today")
        
        # Test with no duplicates
        self.assertEqual(TextNormalizer.remove_duplicate_chars("hello world"), "hello world")
        

if __name__ == '__main__':
    unittest.main()