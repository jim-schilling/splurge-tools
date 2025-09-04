#!/usr/bin/env python3
"""
Run All Examples Script

This script runs all the splurge-tools examples in sequence, providing
a comprehensive demonstration of the library's capabilities.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_example(example_file: Path) -> tuple[bool, str, float]:
    """
    Run a single example file and return the result.

    Args:
        example_file: Path to the example file to run

    Returns:
        Tuple of (success, output, execution_time)
    """
    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(example_file)],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        execution_time = time.time() - start_time

        if result.returncode == 0:
            return True, result.stdout, execution_time
        error_output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        return False, error_output, execution_time

    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return False, "Example timed out after 5 minutes", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, f"Error running example: {e}", execution_time


def main():
    """Run all examples and provide a summary report."""

    # Get the examples directory
    examples_dir = Path(__file__).parent

    # Define the example files in order
    example_files = [
        "01_type_inference_and_validation.py",
        "02_dsv_parsing_and_profiling.py",
        "03_tabular_data_models.py",
        "04_text_processing.py",
        "05_validation_and_transformation.py",
        "06_random_data_generation.py",
        "07_comprehensive_workflows.py",
        "08_decorator_examples.py",
    ]

    # Verify all example files exist
    missing_files = []
    for filename in example_files:
        if not (examples_dir / filename).exists():
            missing_files.append(filename)

    if missing_files:
        sys.exit(1)

    # Run all examples
    results = []
    total_start_time = time.time()

    for filename in example_files:
        example_file = examples_dir / filename
        success, output, exec_time = run_example(example_file)
        results.append((filename, success, output, exec_time))

        if success:
            pass
        else:
            pass

    time.time() - total_start_time

    # Generate summary report

    successful = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    if successful:
        for filename, _, _, exec_time in successful:
            pass

    if failed:
        for filename, _, _, exec_time in failed:
            pass

        for filename, _, output, _ in failed:
            if len(output) > 1000:
                pass

    # Performance summary
    if successful:
        exec_times = [r[3] for r in successful]
        sum(exec_times) / len(exec_times)
        max(exec_times)
        min(exec_times)

    # Feature coverage summary
    features = [
        "Type inference and validation",
        "DSV parsing and profiling",
        "Tabular data models (in-memory and streaming)",
        "Text processing and normalization",
        "Data validation and transformation",
        "Random data generation",
        "Comprehensive ETL workflows",
        "Decorator examples",
    ]

    for i, _feature in enumerate(features):
        "OK" if i < len(successful) else "ERROR"

    # Exit with appropriate code
    if failed:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
