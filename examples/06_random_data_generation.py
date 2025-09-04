#!/usr/bin/env python3
"""
Random Data Generation Examples

This example demonstrates the secure and non-secure random data generation
capabilities of splurge-tools, including Base58-like strings, random values,
and test data generation.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import contextlib
from datetime import date

from splurge_tools.random_helper import RandomHelper


def basic_random_generation_examples():
    """Demonstrate basic random value generation."""

    # Generate various types of random values


def string_generation_examples():
    """Demonstrate string generation capabilities."""

    # Basic string generation

    # Secure string generation

    # Custom character sets


def base58_like_generation_examples():
    """Demonstrate Base58-like string generation with guaranteed diversity."""

    # Basic Base58-like generation
    for _i in range(5):
        RandomHelper.as_base58_like(20)

    # Different lengths
    lengths = [8, 16, 32, 64]
    for length in lengths:
        RandomHelper.as_base58_like(length)

    # With custom symbols
    custom_symbols = "!@#$"
    for _i in range(3):
        RandomHelper.as_base58_like(24, symbols=custom_symbols)

    # Without symbols (alpha + digits only)
    for _i in range(3):
        RandomHelper.as_base58_like(20, symbols="")

    # Secure generation
    for _i in range(3):
        RandomHelper.as_base58_like(32, secure=True)

    # Demonstrate character diversity guarantee
    test_string = RandomHelper.as_base58_like(50)

    any(c in RandomHelper.BASE58_ALPHA for c in test_string)
    any(c in RandomHelper.BASE58_DIGITS for c in test_string)
    any(c in RandomHelper.SYMBOLS for c in test_string)


def date_generation_examples():
    """Demonstrate date and time generation."""

    # Date ranges using days from today
    for _i in range(5):
        # Generate dates between -365 days (past year) and +365 days (next year)
        RandomHelper.as_date(-365, 365)

    for _i in range(3):
        RandomHelper.as_date(-365, 365, secure=True)

    # Recent dates (last 30 days)
    for _i in range(5):
        # Generate dates between -30 and 0 days from today
        recent_date = RandomHelper.as_date(-30, 0)
        (date.today() - recent_date).days


def practical_use_cases():
    """Demonstrate practical use cases for random data generation."""

    # API Key generation
    api_keys = []
    for _i in range(3):
        api_key = RandomHelper.as_base58_like(32, secure=True)
        api_keys.append(api_key)

    # Session tokens
    for _i in range(3):
        RandomHelper.as_base58_like(24, symbols="", secure=True)

    # Test user IDs
    for _i in range(5):
        RandomHelper.as_int_range(100000, 999999)

    # Random test data
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

    for _i in range(5):
        {
            "id": RandomHelper.as_int_range(1000, 9999),
            "name": f"Employee_{RandomHelper.as_int_range(1, 1000)}",
            "department": departments[RandomHelper.as_int_range(0, len(departments) - 1)],
            "city": cities[RandomHelper.as_int_range(0, len(cities) - 1)],
            "salary": RandomHelper.as_int_range(40000, 120000),
            "active": RandomHelper.as_bool(),
            "start_date": RandomHelper.as_date(-1000, -100),  # Random date in past 1000-100 days
        }


def performance_and_security_examples():
    """Demonstrate performance considerations and security features."""

    # Performance comparison (conceptual - actual timing would vary)

    # Security features demonstration

    # Show that secure generation produces different results
    for _i in range(3):
        RandomHelper.as_base58_like(16, secure=False)
        RandomHelper.as_base58_like(16, secure=True)

    # Demonstrate symbol validation
    valid_symbols = "!@#$%"

    with contextlib.suppress(Exception):
        RandomHelper.as_base58_like(20, symbols=valid_symbols)

    # Note: The library should validate symbols, but let's show the concept


def batch_generation_examples():
    """Demonstrate batch generation for testing scenarios."""

    # Generate batch of test data

    # Generate multiple API keys
    api_keys = [RandomHelper.as_base58_like(32) for _ in range(10)]
    for _i, _key in enumerate(api_keys, 1):
        pass

    # Generate test dataset
    test_records = []
    for _i in range(20):
        record = {
            "id": RandomHelper.as_int_range(1, 10000),
            "score": round(RandomHelper.as_float_range(0.0, 100.0), 2),
            "category": chr(65 + RandomHelper.as_int_range(0, 25)),  # A-Z
            "active": RandomHelper.as_bool(),
            "token": RandomHelper.as_base58_like(12, symbols=""),
        }
        test_records.append(record)

    # Show summary statistics
    sum(1 for r in test_records if r["active"])
    sum(r["score"] for r in test_records) / len(test_records)
    len({r["category"] for r in test_records})

    # Show sample records
    for record in test_records[:5]:
        pass


def error_handling_examples():
    """Demonstrate error handling in random generation."""

    error_scenarios = [
        ("Zero length string", lambda: RandomHelper.as_string(0)),
        ("Negative length", lambda: RandomHelper.as_string(-5)),
        ("Invalid range (start > end)", lambda: RandomHelper.as_int_range(100, 50)),
        ("Zero-length Base58", lambda: RandomHelper.as_base58_like(0)),
        ("Base58 too short for diversity", lambda: RandomHelper.as_base58_like(2)),  # Might be too short
    ]

    for _scenario_name, test_func in error_scenarios:
        with contextlib.suppress(Exception):
            test_func()


if __name__ == "__main__":
    """Run all random data generation examples."""

    basic_random_generation_examples()
    string_generation_examples()
    base58_like_generation_examples()
    date_generation_examples()
    practical_use_cases()
    performance_and_security_examples()
    batch_generation_examples()
    error_handling_examples()
