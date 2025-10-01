import pytest

from splurge_tools.case_helper import CaseHelper


class TestCaseHelper:
    """Test cases for CaseHelper class."""

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello world", "Hello-World"),
            ("HELLO WORLD", "Hello-World"),
            ("hello-world", "Hello-World"),
            ("hello_world", "Hello-World"),
            ("", ""),
        ],
        ids=["row_0", "row_1", "row_2", "row_3", "row_4"],
    )
    def test_to_train(self, input_str: str, expected: str):
        """Test train case conversion."""
        assert CaseHelper.to_train(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello world", "Hello world"),
            ("HELLO WORLD", "Hello world"),
            ("hello-world", "Hello world"),
            ("hello_world", "Hello world"),
            ("", ""),
        ],
        ids=["row_0", "row_1", "row_2", "row_3", "row_4"],
    )
    def test_to_sentence(self, input_str: str, expected: str):
        """Test sentence case conversion."""
        assert CaseHelper.to_sentence(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello world", "helloWorld"),
            ("HELLO WORLD", "helloWorld"),
            ("hello-world", "helloWorld"),
            ("hello_world", "helloWorld"),
            ("", ""),
        ],
        ids=["row_0", "row_1", "row_2", "row_3", "row_4"],
    )
    def test_to_camel(self, input_str: str, expected: str):
        """Test camel case conversion."""
        assert CaseHelper.to_camel(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello world", "hello_world"),
            ("HELLO WORLD", "hello_world"),
            ("hello-world", "hello_world"),
            ("HelloWorld", "helloworld"),
            ("", ""),
        ],
        ids=["row_0", "row_1", "row_2", "row_3", "row_4"],
    )
    def test_to_snake(self, input_str: str, expected: str):
        """Test snake case conversion."""
        assert CaseHelper.to_snake(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello world", "hello-world"),
            ("HELLO WORLD", "hello-world"),
            ("hello_world", "hello-world"),
            ("HelloWorld", "helloworld"),
            ("", ""),
        ],
        ids=["row_0", "row_1", "row_2", "row_3", "row_4"],
    )
    def test_to_kebab(self, input_str: str, expected: str):
        """Test kebab case conversion."""
        assert CaseHelper.to_kebab(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello world", "HelloWorld"),
            ("HELLO WORLD", "HelloWorld"),
            ("hello-world", "HelloWorld"),
            ("hello_world", "HelloWorld"),
            ("", ""),
        ],
        ids=["row_0", "row_1", "row_2", "row_3", "row_4"],
    )
    def test_to_pascal(self, input_str: str, expected: str):
        """Test pascal case conversion."""
        assert CaseHelper.to_pascal(input_str) == expected

    def test_handle_empty_values(self):
        """Test that empty values are handled correctly by the decorator."""
        # Test None values
        assert CaseHelper.to_train(None) == ""
        assert CaseHelper.to_sentence(None) == ""
        assert CaseHelper.to_camel(None) == ""
        assert CaseHelper.to_snake(None) == ""
        assert CaseHelper.to_kebab(None) == ""
        assert CaseHelper.to_pascal(None) == ""

        # Test empty strings
        assert CaseHelper.to_train("") == ""
        assert CaseHelper.to_sentence("") == ""
        assert CaseHelper.to_camel("") == ""
        assert CaseHelper.to_snake("") == ""
        assert CaseHelper.to_kebab("") == ""
        assert CaseHelper.to_pascal("") == ""

        # Test whitespace-only strings (should not be considered empty)
        assert CaseHelper.to_train("   ") == "---"
        assert CaseHelper.to_sentence("   ") == "   "
