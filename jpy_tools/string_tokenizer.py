"""
string_tokenizer.py

A utility module for string tokenization operations.
Provides methods to split strings into tokens and manipulate string boundaries.

Copyright (c) 2025 Jim Schilling
All rights reserved.

Please preserve this header and all related material when sharing!

This software is licensed under the MIT License.
"""

class StringTokenizer:
    """
    A utility class for string tokenization operations.
    
    This class provides methods to:
    - Split strings into tokens based on delimiters
    - Process multiple strings into token lists
    - Remove matching characters from string boundaries
    """
    
    @staticmethod
    def parse(content: str, delimiter: str, strip: bool = True) -> list[str]:
        """
        Split a string into tokens based on a delimiter.
        
        Args:
            content (str): The input string to tokenize
            delimiter (str): The character(s) to split the string on
            strip (bool, optional): Whether to strip whitespace from tokens. Defaults to True.
            
        Returns:
            list[str]: List of tokens, with empty tokens removed if strip is True
            
        Example:
            >>> StringTokenizer.parse("a,b,c", ",")
            ['a', 'b', 'c']
        """
        result: list[str] = content.split(delimiter)
        if strip:
            result = [token.strip() for token in result if len(token.strip()) > 0]
        return result

    @staticmethod
    def parses(content: list[str], delimiter: str, strip: bool = True) -> list[list[str]]:
        """
        Process multiple strings into lists of tokens.
        
        Args:
            content (list[str]): List of strings to tokenize
            delimiter (str): The character(s) to split each string on
            strip (bool, optional): Whether to strip whitespace from tokens. Defaults to True.
            
        Returns:
            list[list[str]]: List of token lists, one for each input string
            
        Example:
            >>> StringTokenizer.parses(["a,b", "c,d"], ",")
            [['a', 'b'], ['c', 'd']]
        """
        return [StringTokenizer.parse(text, delimiter, strip) for text in content]

    @staticmethod
    def remove_bookends(content: str, bookend: str, strip: bool = True) -> str:
        """
        Remove matching characters from both ends of a string.
        
        Args:
            content (str): The input string to process
            bookend (str): The character(s) to remove from both ends
            strip (bool, optional): Whether to strip whitespace first. Defaults to True.
            
        Returns:
            str: The string with matching bookends removed
            
        Example:
            >>> StringTokenizer.remove_bookends("'hello'", "'")
            'hello'
        """
        value = content.strip() if strip else content
        if value.startswith(bookend) and value.endswith(bookend) and len(value) > 1:
            return value[1:-1]
        return value