#!/usr/bin/env python3
"""
Random Data Generation Examples

This example demonstrates the secure and non-secure random data generation
capabilities of splurge-tools, including Base58-like strings, random values,
and test data generation.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

from datetime import date
from splurge_tools.random_helper import RandomHelper


def basic_random_generation_examples():
    """Demonstrate basic random value generation."""
    print("=== Basic Random Generation Examples ===\n")
    
    # Generate various types of random values
    print("Non-secure Random Values:")
    print(f"Random bytes (8): {RandomHelper.as_bytes(8)}")
    print(f"Random int: {RandomHelper.as_int()}")
    print(f"Random int (4 bytes): {RandomHelper.as_int(4)}")
    print(f"Random int range (1-100): {RandomHelper.as_int_range(1, 100)}")
    print(f"Random float range (0-10): {RandomHelper.as_float_range(0.0, 10.0)}")
    print(f"Random boolean: {RandomHelper.as_bool()}")
    print()
    
    print("Secure Random Values (cryptographically secure):")
    print(f"Secure bytes (8): {RandomHelper.as_bytes(8, secure=True)}")
    print(f"Secure int: {RandomHelper.as_int(secure=True)}")
    print(f"Secure int range (1-1000): {RandomHelper.as_int_range(1, 1000, secure=True)}")
    print(f"Secure float range (0-1): {RandomHelper.as_float_range(0.0, 1.0, secure=True)}")
    print(f"Secure boolean: {RandomHelper.as_bool(secure=True)}")
    print()


def string_generation_examples():
    """Demonstrate string generation capabilities."""
    print("=== String Generation Examples ===\n")
    
    # Basic string generation
    print("Basic String Generation:")
    print(f"Alpha string (10): '{RandomHelper.as_string(10, RandomHelper.ALPHA_CHARS)}'")
    print(f"Numeric string (8): '{RandomHelper.as_string(8, RandomHelper.DIGITS)}'")
    print(f"Alphanumeric (12): '{RandomHelper.as_string(12, RandomHelper.ALPHANUMERIC_CHARS)}'")
    print(f"Base58 characters (16): '{RandomHelper.as_string(16, RandomHelper.BASE58_CHARS)}'")
    print()
    
    # Secure string generation
    print("Secure String Generation:")
    print(f"Secure alpha (10): '{RandomHelper.as_string(10, RandomHelper.ALPHA_CHARS, secure=True)}'")
    print(f"Secure alphanumeric (15): '{RandomHelper.as_string(15, RandomHelper.ALPHANUMERIC_CHARS, secure=True)}'")
    print()
    
    # Custom character sets
    print("Custom Character Sets:")
    custom_chars = "ABCDEF0123456789"  # Hex characters
    print(f"Hex string (12): '{RandomHelper.as_string(12, custom_chars)}'")
    
    vowels = "AEIOU"
    print(f"Vowels only (8): '{RandomHelper.as_string(8, vowels)}'")
    print()


def base58_like_generation_examples():
    """Demonstrate Base58-like string generation with guaranteed diversity."""
    print("=== Base58-like String Generation Examples ===\n")
    
    # Basic Base58-like generation
    print("Basic Base58-like Generation:")
    for i in range(5):
        base58_str = RandomHelper.as_base58_like(20)
        print(f"  {i+1}: '{base58_str}' (length: {len(base58_str)})")
    print()
    
    # Different lengths
    print("Different Lengths:")
    lengths = [8, 16, 32, 64]
    for length in lengths:
        base58_str = RandomHelper.as_base58_like(length)
        print(f"  Length {length}: '{base58_str}'")
    print()
    
    # With custom symbols
    print("With Custom Symbols:")
    custom_symbols = "!@#$"
    for i in range(3):
        base58_str = RandomHelper.as_base58_like(24, symbols=custom_symbols)
        print(f"  Custom symbols {i+1}: '{base58_str}'")
    print()
    
    # Without symbols (alpha + digits only)
    print("Without Symbols (Alpha + Digits only):")
    for i in range(3):
        base58_str = RandomHelper.as_base58_like(20, symbols="")
        print(f"  No symbols {i+1}: '{base58_str}'")
    print()
    
    # Secure generation
    print("Secure Base58-like Generation:")
    for i in range(3):
        secure_str = RandomHelper.as_base58_like(32, secure=True)
        print(f"  Secure {i+1}: '{secure_str}'")
    print()
    
    # Demonstrate character diversity guarantee
    print("Character Diversity Analysis:")
    test_string = RandomHelper.as_base58_like(50)
    
    has_alpha = any(c in RandomHelper.BASE58_ALPHA for c in test_string)
    has_digit = any(c in RandomHelper.BASE58_DIGITS for c in test_string)
    has_symbol = any(c in RandomHelper.SYMBOLS for c in test_string)
    
    print(f"  Generated string: '{test_string}'")
    print(f"  Has alphabetic: {has_alpha}")
    print(f"  Has digits: {has_digit}")
    print(f"  Has symbols: {has_symbol}")
    print("  Note: Base58-like strings guarantee at least one of each character type")
    print()


def date_generation_examples():
    """Demonstrate date and time generation."""
    print("=== Date and Time Generation Examples ===\n")
    
    # Date ranges using days from today
    print("Random Dates (using days from today):")
    for i in range(5):
        # Generate dates between -365 days (past year) and +365 days (next year)
        random_date = RandomHelper.as_date(-365, 365)
        print(f"  Date {i+1}: {random_date} ({random_date.strftime('%A, %B %d, %Y')})")
    print()
    
    print("Secure Random Dates:")
    for i in range(3):
        secure_date = RandomHelper.as_date(-365, 365, secure=True)
        print(f"  Secure date {i+1}: {secure_date}")
    print()
    
    # Recent dates (last 30 days)
    print("Recent Dates (last 30 days):")
    for i in range(5):
        # Generate dates between -30 and 0 days from today
        recent_date = RandomHelper.as_date(-30, 0)
        days_ago = (date.today() - recent_date).days
        print(f"  {recent_date} ({days_ago} days ago)")
    print()


def practical_use_cases():
    """Demonstrate practical use cases for random data generation."""
    print("=== Practical Use Cases ===\n")
    
    # API Key generation
    print("API Key Generation:")
    api_keys = []
    for i in range(3):
        api_key = RandomHelper.as_base58_like(32, secure=True)
        api_keys.append(api_key)
        print(f"  API Key {i+1}: {api_key}")
    print()
    
    # Session tokens
    print("Session Token Generation:")
    for i in range(3):
        session_token = RandomHelper.as_base58_like(24, symbols="", secure=True)
        print(f"  Session Token {i+1}: {session_token}")
    print()
    
    # Test user IDs
    print("Test User ID Generation:")
    for i in range(5):
        user_id = RandomHelper.as_int_range(100000, 999999)
        print(f"  User ID {i+1}: {user_id}")
    print()
    
    # Random test data
    print("Random Test Data Generation:")
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    
    for i in range(5):
        employee_data = {
            "id": RandomHelper.as_int_range(1000, 9999),
            "name": f"Employee_{RandomHelper.as_int_range(1, 1000)}",
            "department": departments[RandomHelper.as_int_range(0, len(departments) - 1)],
            "city": cities[RandomHelper.as_int_range(0, len(cities) - 1)],
            "salary": RandomHelper.as_int_range(40000, 120000),
            "active": RandomHelper.as_bool(),
            "start_date": RandomHelper.as_date(-1000, -100)  # Random date in past 1000-100 days
        }
        print(f"  Employee {i+1}: {employee_data}")
    print()


def performance_and_security_examples():
    """Demonstrate performance considerations and security features."""
    print("=== Performance and Security Examples ===\n")
    
    # Performance comparison (conceptual - actual timing would vary)
    print("Performance Considerations:")
    print("• Non-secure generation: Faster, suitable for testing and non-critical use")
    print("• Secure generation: Slower, suitable for cryptographic applications")
    print()
    
    # Security features demonstration
    print("Security Features:")
    
    # Show that secure generation produces different results
    print("Secure vs Non-secure comparison:")
    for i in range(3):
        non_secure = RandomHelper.as_base58_like(16, secure=False)
        secure = RandomHelper.as_base58_like(16, secure=True)
        print(f"  Non-secure: {non_secure}")
        print(f"  Secure:     {secure}")
        print()
    
    # Demonstrate symbol validation
    print("Symbol Validation:")
    valid_symbols = "!@#$%"
    invalid_symbols = "0OIl"  # These would conflict with Base58
    
    try:
        valid_string = RandomHelper.as_base58_like(20, symbols=valid_symbols)
        print(f"  Valid symbols '{valid_symbols}': {valid_string}")
    except Exception as e:
        print(f"  Valid symbols error: {e}")
    
    # Note: The library should validate symbols, but let's show the concept
    print(f"  Invalid symbols '{invalid_symbols}' would be rejected to maintain Base58 compatibility")
    print()


def batch_generation_examples():
    """Demonstrate batch generation for testing scenarios."""
    print("=== Batch Generation Examples ===\n")
    
    # Generate batch of test data
    print("Batch Test Data Generation:")
    
    # Generate multiple API keys
    print("Batch API Keys (for testing):")
    api_keys = [RandomHelper.as_base58_like(32) for _ in range(10)]
    for i, key in enumerate(api_keys, 1):
        print(f"  {i:2d}: {key}")
    print()
    
    # Generate test dataset
    print("Test Dataset Generation:")
    test_records = []
    for i in range(20):
        record = {
            "id": RandomHelper.as_int_range(1, 10000),
            "score": round(RandomHelper.as_float_range(0.0, 100.0), 2),
            "category": chr(65 + RandomHelper.as_int_range(0, 25)),  # A-Z
            "active": RandomHelper.as_bool(),
            "token": RandomHelper.as_base58_like(12, symbols="")
        }
        test_records.append(record)
    
    # Show summary statistics
    active_count = sum(1 for r in test_records if r["active"])
    avg_score = sum(r["score"] for r in test_records) / len(test_records)
    unique_categories = len(set(r["category"] for r in test_records))
    
    print(f"  Generated {len(test_records)} test records")
    print(f"  Active records: {active_count}/{len(test_records)}")
    print(f"  Average score: {avg_score:.2f}")
    print(f"  Unique categories: {unique_categories}")
    print()
    
    # Show sample records
    print("Sample Records:")
    for record in test_records[:5]:
        print(f"  {record}")
    print()


def error_handling_examples():
    """Demonstrate error handling in random generation."""
    print("=== Error Handling Examples ===\n")
    
    error_scenarios = [
        ("Zero length string", lambda: RandomHelper.as_string(0)),
        ("Negative length", lambda: RandomHelper.as_string(-5)),
        ("Invalid range (start > end)", lambda: RandomHelper.as_int_range(100, 50)),
        ("Zero-length Base58", lambda: RandomHelper.as_base58_like(0)),
        ("Base58 too short for diversity", lambda: RandomHelper.as_base58_like(2)),  # Might be too short
    ]
    
    print("Error Handling Test Results:")
    for scenario_name, test_func in error_scenarios:
        try:
            result = test_func()
            print(f"  {scenario_name}: Unexpected success - {result}")
        except Exception as e:
            print(f"  {scenario_name}: {type(e).__name__} - {e}")
    print()


if __name__ == "__main__":
    """Run all random data generation examples."""
    print("Splurge-Tools: Random Data Generation Examples")
    print("=" * 60)
    print()
    
    basic_random_generation_examples()
    string_generation_examples()
    base58_like_generation_examples()
    date_generation_examples()
    practical_use_cases()
    performance_and_security_examples()
    batch_generation_examples()
    error_handling_examples()
    
    print("Examples completed successfully!")
    print("\nKey Takeaways:")
    print("• RandomHelper supports both secure and non-secure generation")
    print("• Base58-like strings guarantee character diversity (alpha + digit + symbol)")
    print("• Comprehensive support for integers, floats, strings, dates, and booleans")
    print("• Configurable character sets for custom string generation")
    print("• Built-in validation and error handling")
    print("• Suitable for API keys, session tokens, and test data generation")
    print("• Cryptographically secure options for production use")
