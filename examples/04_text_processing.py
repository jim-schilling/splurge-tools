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
from splurge_tools.text_normalizer import TextNormalizer
from splurge_tools.case_helper import CaseHelper
from splurge_tools.string_tokenizer import StringTokenizer
from splurge_tools.text_file_helper import TextFileHelper


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
    csv_text = '''Name,Age,"City, State",Salary
John Doe,30,"New York, NY",75000
Jane Smith,25,"Los Angeles, CA",65000
"Bob Johnson, Jr.",45,"Chicago, IL",85000'''
    
    # Create files
    files = {}
    files['messy'] = temp_dir / "messy_text.txt"
    files['large'] = temp_dir / "large_text.txt"
    files['csv'] = temp_dir / "sample_data.csv"
    
    files['messy'].write_text(messy_text)
    files['large'].write_text(large_text)
    files['csv'].write_text(csv_text)
    
    return temp_dir, files


def text_normalization_examples():
    """Demonstrate text normalization capabilities."""
    print("=== Text Normalization Examples ===\n")
    
    # Various text normalization scenarios
    test_texts = {
        "Accents": "café résumé naïve piñata",
        "Whitespace": "  hello    world  \n\n  extra   spaces  ",
        "Special chars": "hello@world#test$value%",
        "Control chars": "hello\x00world\x01test\x02",
        "Smart quotes": '"Hello" \'world\' — with dashes',
        "Line endings": "line1\r\nline2\rline3\n",
        "Unicode spaces": "hello\u00a0world test",
    }
    
    for category, text in test_texts.items():
        print(f"{category}:")
        print(f"  Original: '{text}'")
        
        # Apply various normalizations
        no_accents = TextNormalizer.remove_accents(text)
        normalized_ws = TextNormalizer.normalize_whitespace(text)
        no_special = TextNormalizer.remove_special_chars(text)
        normalized_quotes = TextNormalizer.normalize_quotes(text)
        normalized_spaces = TextNormalizer.normalize_spaces(text)
        
        print(f"  No accents: '{no_accents}'")
        print(f"  Normalized whitespace: '{normalized_ws}'")
        print(f"  No special chars: '{no_special}'")
        print(f"  Normalized quotes: '{normalized_quotes}'")
        print(f"  Normalized spaces: '{normalized_spaces}'")
        print()


def case_conversion_examples():
    """Demonstrate case conversion capabilities."""
    print("=== Case Conversion Examples ===\n")
    
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
    
    print("String".ljust(20) + "Snake".ljust(15) + "Camel".ljust(15) + "Pascal".ljust(15) + "Kebab".ljust(15) + "Train")
    print("-" * 95)
    
    for text in test_strings:
        snake = CaseHelper.to_snake(text)
        camel = CaseHelper.to_camel(text)
        pascal = CaseHelper.to_pascal(text)
        kebab = CaseHelper.to_kebab(text)
        train = CaseHelper.to_train(text)
        
        print(f"{text.ljust(20)}{snake.ljust(15)}{camel.ljust(15)}{pascal.ljust(15)}{kebab.ljust(15)}{train}")
    
    print()
    
    # Special case conversions
    print("Special Case Conversions:")
    special_cases = [
        ("API_KEY_VALUE", "API key handling"),
        ("XMLHttpRequest", "Acronym handling"),
        ("iPhone_iOS_App", "Mixed acronyms"),
        ("user-profile-settings", "Kebab to others"),
    ]
    
    for text, description in special_cases:
        print(f"  {description}: '{text}'")
        print(f"    Snake: '{CaseHelper.to_snake(text)}'")
        print(f"    Camel: '{CaseHelper.to_camel(text)}'")
        print(f"    Sentence: '{CaseHelper.to_sentence(text)}'")
        print()


def string_tokenization_examples():
    """Demonstrate string tokenization capabilities."""
    print("=== String Tokenization Examples ===\n")
    
    # Basic tokenization
    test_data = [
        ("Simple CSV", "apple,banana,cherry", ","),
        ("With spaces", "apple, banana, cherry", ","),
        ("Tab separated", "apple\tbanana\tcherry", "\t"),
        ("Pipe separated", "apple|banana|cherry", "|"),
        ("Semicolon", "apple;banana;cherry", ";"),
    ]
    
    print("Tokenization Examples:")
    for description, text, delimiter in test_data:
        tokens = StringTokenizer.parse(text, delimiter=delimiter)
        tokens_no_strip = StringTokenizer.parse(text, delimiter=delimiter, strip=False)
        
        print(f"  {description}: '{text}'")
        print(f"    Tokens (stripped): {tokens}")
        print(f"    Tokens (not stripped): {tokens_no_strip}")
        print()
    
    # Advanced tokenization with bookends
    print("Advanced Tokenization with Bookends:")
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
        
        print(f"  Text: '{text}'")
        print(f"    Raw tokens: {tokens}")
        print(f"    After bookend removal: {tokens_with_bookend}")
        print()
    
    # Multi-line tokenization
    print("Multi-line Tokenization:")
    multi_line_text = """line1,field1,value1
line2,field2,value2
line3,field3,value3"""
    
    lines = multi_line_text.split('\n')
    parsed_lines = []
    for line in lines:
        parsed_lines.append(StringTokenizer.parse(line, delimiter=","))
    
    print("  Multi-line text:")
    for i, line in enumerate(lines):
        print(f"    Line {i}: '{line}' -> {parsed_lines[i]}")
    print()


def text_file_processing_examples(files):
    """Demonstrate text file processing capabilities."""
    print("=== Text File Processing Examples ===\n")
    
    # Basic file reading
    print(f"Reading file: {files['messy']}")
    content = TextFileHelper.read(files['messy'])
    print(f"Lines read: {len(content)}")
    print("First 3 lines:")
    for i, line in enumerate(content[:3]):
        print(f"  {i}: '{line}'")
    print()
    
    # File preview
    print("File Preview:")
    preview = TextFileHelper.preview(files['messy'], max_lines=5)
    print(f"Preview (5 lines): {preview}")
    print()
    
    # Reading with header/footer skipping
    print(f"Large file processing: {files['large']}")
    content_no_headers = TextFileHelper.read(
        files['large'], 
        skip_header_rows=2,
        skip_footer_rows=2
    )
    print(f"Total lines: {len(content_no_headers)} (after skipping 2 header + 2 footer)")
    print(f"First line: '{content_no_headers[0]}'")
    print(f"Last line: '{content_no_headers[-1]}'")
    print()
    
    # Streaming file processing
    print("Streaming File Processing:")
    chunk_count = 0
    total_lines = 0
    
    for chunk in TextFileHelper.read_as_stream(
        files['large'], 
        chunk_size=100,
        skip_header_rows=2,
        skip_footer_rows=2
    ):
        chunk_count += 1
        lines_in_chunk = len(chunk)
        total_lines += lines_in_chunk
        
        print(f"  Chunk {chunk_count}: {lines_in_chunk} lines")
        
        if chunk_count >= 5:  # Show first 5 chunks
            break
    
    print(f"Processed {chunk_count} chunks with {total_lines} total lines")
    print("Note: Streaming enables processing of very large files")
    print()
    
    # File writing
    print("File Writing:")
    output_file = files['messy'].parent / "processed_output.txt"
    
    # Process the messy text and write clean version
    processed_lines = []
    for line in content:
        # Apply multiple normalizations
        clean_line = TextNormalizer.normalize_whitespace(line)
        clean_line = TextNormalizer.remove_accents(clean_line)
        clean_line = TextNormalizer.normalize_quotes(clean_line)
        clean_line = TextNormalizer.remove_control_chars(clean_line)
        processed_lines.append(clean_line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in processed_lines:
            f.write(line + '\n')
    print(f"Processed text written to: {output_file}")
    
    # Verify the written file
    written_content = TextFileHelper.read(output_file)
    print(f"Verification: {len(written_content)} lines written successfully")
    print()


def comprehensive_text_processing_workflow():
    """Demonstrate a comprehensive text processing workflow."""
    print("=== Comprehensive Text Processing Workflow ===\n")
    
    # Simulate processing a messy dataset
    raw_data = [
        "  John DOE  ,  30  , New York, NY , Software Engineer ",
        "jane_smith,25,Los Angeles,CA,Product Manager",
        "Bob-Johnson,45,\"Chicago, IL\",\"Senior Developer\"",
        "  ALICE  BROWN  , 35 ,Houston,TX,Data Scientist",
        "charlie.wilson,28,Phoenix,AZ,UX Designer"
    ]
    
    print("Raw Data Processing Workflow:")
    print("Step 1: Original messy data")
    for i, line in enumerate(raw_data):
        print(f"  {i}: '{line}'")
    print()
    
    print("Step 2: Text normalization")
    normalized_data = []
    for line in raw_data:
        # Normalize whitespace and remove extra spaces
        clean_line = TextNormalizer.normalize_whitespace(line)
        clean_line = TextNormalizer.normalize_spaces(clean_line)
        normalized_data.append(clean_line)
        print(f"  '{line}' -> '{clean_line}'")
    print()
    
    print("Step 3: Tokenization")
    tokenized_data = []
    for line in normalized_data:
        tokens = StringTokenizer.parse(line, delimiter=",", strip=True)
        # Remove bookends if present
        clean_tokens = []
        for token in tokens:
            clean_token = StringTokenizer.remove_bookends(token, bookend='"', strip=True)
            clean_tokens.append(clean_token)
        tokenized_data.append(clean_tokens)
        print(f"  '{line}' -> {clean_tokens}")
    print()
    
    print("Step 4: Case normalization")
    final_data = []
    for tokens in tokenized_data:
        processed_tokens = []
        for i, token in enumerate(tokens):
            if i == 0:  # Name field - convert to title case
                processed_token = CaseHelper.to_sentence(token.replace('.', ' ').replace('_', ' ').replace('-', ' '))
                processed_tokens.append(processed_token)
            elif i == 4:  # Job title - convert to title case
                processed_token = CaseHelper.to_sentence(token.replace('_', ' ').replace('-', ' '))
                processed_tokens.append(processed_token)
            else:  # Other fields - normalize case
                processed_tokens.append(token.title())
        
        final_data.append(processed_tokens)
        print(f"  {tokens} -> {processed_tokens}")
    print()
    
    print("Step 5: Final structured data")
    headers = ["Name", "Age", "City", "State", "Job Title"]
    print(f"  Headers: {headers}")
    for i, row in enumerate(final_data):
        print(f"  Row {i}: {dict(zip(headers, row))}")
    print()
    
    print("Workflow Summary:")
    print("• Applied whitespace normalization")
    print("• Tokenized delimited data with bookend handling")
    print("• Applied appropriate case conversions per field")
    print("• Structured data into consistent format")
    print()


def cleanup_temp_files(temp_dir):
    """Clean up temporary files."""
    import shutil
    shutil.rmtree(temp_dir)
    print(f"Cleaned up temporary files in: {temp_dir}")


if __name__ == "__main__":
    """Run all text processing examples."""
    print("Splurge-Tools: Text Processing Examples")
    print("=" * 60)
    print()
    
    # Create sample files
    temp_dir, files = create_sample_text_files()
    print(f"Created sample files in: {temp_dir}")
    print()
    
    try:
        text_normalization_examples()
        case_conversion_examples()
        string_tokenization_examples()
        text_file_processing_examples(files)
        comprehensive_text_processing_workflow()
        
        print("Examples completed successfully!")
        print("\nKey Takeaways:")
        print("• TextNormalizer provides comprehensive text cleaning operations")
        print("• CaseHelper supports all major case conversion patterns")
        print("• StringTokenizer handles delimited data with bookend support")
        print("• TextFileHelper enables both in-memory and streaming file processing")
        print("• All modules work together for complete text processing workflows")
        print("• Built-in support for Unicode, special characters, and edge cases")
        
    finally:
        cleanup_temp_files(temp_dir)
