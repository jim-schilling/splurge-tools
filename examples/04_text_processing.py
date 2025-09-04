#!/usr/bin/env python3
"""
Text Processing Examples

This example demonstrates the comprehensive text processing capabilities of splurge-tools,
including text normalization, case conversion, string tokenization, and file processing.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import tempfile
from pathlib import Path

from splurge_tools.case_helper import CaseHelper
from splurge_tools.string_tokenizer import StringTokenizer
from splurge_tools.text_file_helper import TextFileHelper
from splurge_tools.text_normalizer import TextNormalizer


def create_sample_text_files():
    """Create sample text files for demonstration."""
    temp_dir = Path(tempfile.mkdtemp())

    # Sample text with various issues
    messy_text = """  This is a sample text file with various issues...

It contains extra   whitespace,
    inconsistent indentation,
and multiple accents.

It also has "smart quotes" and regular dashes.
Some lines have trailing spaces.

There are also MIXED case issues and
inconsistent-formatting_styles.

Final line with some special chars.
"""

    # Large text file for streaming
    large_text = "Header Line 1\nHeader Line 2\n"
    for i in range(1000):
        large_text += f"Data line {i}: This is content for line number {i}\n"
    large_text += "Footer Line 1\nFooter Line 2\n"

    # CSV-like text for tokenization
    csv_text = """Name,Age,"City, State",Salary
John Doe,30,"New York, NY",75000
Jane Smith,25,"Los Angeles, CA",65000
"Bob Johnson, Jr.",45,"Chicago, IL",85000"""

    # Create files
    files = {}
    files["messy"] = temp_dir / "messy_text.txt"
    files["large"] = temp_dir / "large_text.txt"
    files["csv"] = temp_dir / "sample_data.csv"

    files["messy"].write_text(messy_text)
    files["large"].write_text(large_text)
    files["csv"].write_text(csv_text)

    return temp_dir, files


def text_normalization_examples():
    """Demonstrate text normalization capabilities."""

    # Various text normalization scenarios
    test_texts = {
        "Accents": "café résumé naïve piñata",
        "Whitespace": "  hello    world  \n\n  extra   spaces  ",
        "Special chars": "hello@world#test$value%",
        "Control chars": "hello\x00world\x01test\x02",
        "Smart quotes": "\"Hello\" 'world' — with dashes",
        "Line endings": "line1\r\nline2\rline3\n",
        "Unicode spaces": "hello\u00a0world test",
    }

    for text in test_texts.values():
        # Apply various normalizations
        TextNormalizer.remove_accents(text)
        TextNormalizer.normalize_whitespace(text)
        TextNormalizer.remove_special_chars(text)
        TextNormalizer.normalize_quotes(text)
        TextNormalizer.normalize_spaces(text)


def case_conversion_examples():
    """Demonstrate case conversion capabilities."""

    # Various case conversion scenarios
    test_strings = [
        "hello world",
        "hello_world",
        "hello-world",
        "HelloWorld",
        "helloWorld",
        "HELLO WORLD",
        "mixed_Case-Example",
    ]

    for text in test_strings:
        CaseHelper.to_snake(text)
        CaseHelper.to_camel(text)
        CaseHelper.to_pascal(text)
        CaseHelper.to_kebab(text)
        CaseHelper.to_train(text)

    # Special case conversions
    special_cases = [
        ("API_KEY_VALUE", "API key handling"),
        ("XMLHttpRequest", "Acronym handling"),
        ("iPhone_iOS_App", "Mixed acronyms"),
        ("user-profile-settings", "Kebab to others"),
    ]

    for text, _description in special_cases:
        pass


def string_tokenization_examples():
    """Demonstrate string tokenization capabilities."""

    # Basic tokenization
    test_data = [
        ("Simple CSV", "apple,banana,cherry", ","),
        ("With spaces", "apple, banana, cherry", ","),
        ("Tab separated", "apple\tbanana\tcherry", "\t"),
        ("Pipe separated", "apple|banana|cherry", "|"),
        ("Semicolon", "apple;banana;cherry", ";"),
    ]

    for _description, text, delimiter in test_data:
        tokens = StringTokenizer.parse(text, delimiter=delimiter)
        StringTokenizer.parse(text, delimiter=delimiter, strip=False)

    # Advanced tokenization with bookends
    quoted_examples = [
        ('"apple","banana","cherry"', '"'),
        ("'apple','banana','cherry'", "'"),
        ('"apple, inc","banana corp","cherry llc"', '"'),
        ('"say ""hello""","world"', '"'),  # Escaped quotes
    ]

    for text, bookend in quoted_examples:
        tokens = StringTokenizer.parse(text, delimiter=",")
        tokens_with_bookend = []
        for token in tokens:
            clean_token = StringTokenizer.remove_bookends(token, bookend=bookend)
            tokens_with_bookend.append(clean_token)

    # Multi-line tokenization
    multi_line_text = """line1,field1,value1
line2,field2,value2
line3,field3,value3"""

    lines = multi_line_text.split("\n")
    parsed_lines = []
    for line in lines:
        parsed_lines.append(StringTokenizer.parse(line, delimiter=","))

    for _i, line in enumerate(lines):
        pass


def text_file_processing_examples(files):
    """Demonstrate text file processing capabilities."""

    # Basic file reading
    content = TextFileHelper.read(files["messy"])
    for _i, line in enumerate(content[:3]):
        pass

    # File preview
    TextFileHelper.preview(files["messy"], max_lines=5)

    # Reading with header/footer skipping
    TextFileHelper.read(
        files["large"],
        skip_header_rows=2,
        skip_footer_rows=2,
    )

    # Streaming file processing
    chunk_count = 0
    total_lines = 0

    for chunk in TextFileHelper.read_as_stream(
        files["large"],
        chunk_size=100,
        skip_header_rows=2,
        skip_footer_rows=2,
    ):
        chunk_count += 1
        lines_in_chunk = len(chunk)
        total_lines += lines_in_chunk

        if chunk_count >= 5:  # Show first 5 chunks
            break

    # File writing
    output_file = files["messy"].parent / "processed_output.txt"

    # Process the messy text and write clean version
    processed_lines = []
    for line in content:
        # Apply multiple normalizations
        clean_line = TextNormalizer.normalize_whitespace(line)
        clean_line = TextNormalizer.remove_accents(clean_line)
        clean_line = TextNormalizer.normalize_quotes(clean_line)
        clean_line = TextNormalizer.remove_control_chars(clean_line)
        processed_lines.append(clean_line)

    with open(output_file, "w", encoding="utf-8") as f:
        for line in processed_lines:
            f.write(line + "\n")

    # Verify the written file
    TextFileHelper.read(output_file)


def comprehensive_text_processing_workflow():
    """Demonstrate a comprehensive text processing workflow."""

    # Simulate processing a messy dataset
    raw_data = [
        "  John DOE  ,  30  , New York, NY , Software Engineer ",
        "jane_smith,25,Los Angeles,CA,Product Manager",
        'Bob-Johnson,45,"Chicago, IL","Senior Developer"',
        "  ALICE  BROWN  , 35 ,Houston,TX,Data Scientist",
        "charlie.wilson,28,Phoenix,AZ,UX Designer",
    ]

    for i, line in enumerate(raw_data):
        pass

    normalized_data = []
    for line in raw_data:
        # Normalize whitespace and remove extra spaces
        clean_line = TextNormalizer.normalize_whitespace(line)
        clean_line = TextNormalizer.normalize_spaces(clean_line)
        normalized_data.append(clean_line)

    tokenized_data = []
    for line in normalized_data:
        tokens = StringTokenizer.parse(line, delimiter=",", strip=True)
        # Remove bookends if present
        clean_tokens = []
        for token in tokens:
            clean_token = StringTokenizer.remove_bookends(token, bookend='"', strip=True)
            clean_tokens.append(clean_token)
        tokenized_data.append(clean_tokens)

    final_data = []
    for tokens in tokenized_data:
        processed_tokens = []
        for i, token in enumerate(tokens):
            if i == 0:  # Name field - convert to title case
                processed_token = CaseHelper.to_sentence(token.replace(".", " ").replace("_", " ").replace("-", " "))
                processed_tokens.append(processed_token)
            elif i == 4:  # Job title - convert to title case
                processed_token = CaseHelper.to_sentence(token.replace("_", " ").replace("-", " "))
                processed_tokens.append(processed_token)
            else:  # Other fields - normalize case
                processed_tokens.append(token.title())

        final_data.append(processed_tokens)

    for i, _row in enumerate(final_data):
        pass


def cleanup_temp_files(temp_dir):
    """Clean up temporary files."""
    import shutil

    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    """Run all text processing examples."""

    # Create sample files
    temp_dir, files = create_sample_text_files()

    try:
        text_normalization_examples()
        case_conversion_examples()
        string_tokenization_examples()
        text_file_processing_examples(files)
        comprehensive_text_processing_workflow()

    finally:
        cleanup_temp_files(temp_dir)
