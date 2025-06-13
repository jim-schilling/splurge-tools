import unittest
from jpy_tools.case_helper import CaseHelper

class TestCaseHelper(unittest.TestCase):
    """Test cases for CaseHelper class."""

    def test_to_train(self):
        """Test train case conversion."""
        test_cases = [
            ("hello world", "Hello-World"),
            ("HELLO WORLD", "Hello-World"),
            ("hello-world", "Hello-World"),
            ("hello_world", "Hello-World"),
            ("", ""),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(CaseHelper.to_train(input_str), expected)

    def test_to_sentence(self):
        """Test sentence case conversion."""
        test_cases = [
            ("hello world", "Hello world"),
            ("HELLO WORLD", "Hello world"),
            ("hello-world", "Hello world"),
            ("hello_world", "Hello world"),
            ("", ""),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(CaseHelper.to_sentence(input_str), expected)

    def test_to_camel(self):
        """Test camel case conversion."""
        test_cases = [
            ("hello world", "helloWorld"),
            ("HELLO WORLD", "helloWorld"),
            ("hello-world", "helloWorld"),
            ("hello_world", "helloWorld"),
            ("", ""),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(CaseHelper.to_camel(input_str), expected)

    def test_to_snake(self):
        """Test snake case conversion."""
        test_cases = [
            ("hello world", "hello_world"),
            ("HELLO WORLD", "hello_world"),
            ("hello-world", "hello_world"),
            ("HelloWorld", "helloworld"),
            ("", ""),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(CaseHelper.to_snake(input_str), expected)

    def test_to_kebab(self):
        """Test kebab case conversion."""
        test_cases = [
            ("hello world", "hello-world"),
            ("HELLO WORLD", "hello-world"),
            ("hello_world", "hello-world"),
            ("HelloWorld", "helloworld"),
            ("", ""),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(CaseHelper.to_kebab(input_str), expected)

    def test_to_pascal(self):
        """Test pascal case conversion."""
        test_cases = [
            ("hello world", "HelloWorld"),
            ("HELLO WORLD", "HelloWorld"),
            ("hello-world", "HelloWorld"),
            ("hello_world", "HelloWorld"),
            ("", ""),
        ]
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(CaseHelper.to_pascal(input_str), expected)

if __name__ == '__main__':
    unittest.main()