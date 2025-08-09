#!/usr/bin/env python3
"""
Run All Examples Script

This script runs all the splurge-tools examples in sequence, providing
a comprehensive demonstration of the library's capabilities.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import sys
import time
import subprocess
from pathlib import Path


def run_example(example_file: Path) -> tuple[bool, str, float]:
    """
    Run a single example file and return the result.
    
    Args:
        example_file: Path to the example file to run
        
    Returns:
        Tuple of (success, output, execution_time)
    """
    print(f"Running {example_file.name}...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(example_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            return True, result.stdout, execution_time
        else:
            error_output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            return False, error_output, execution_time
            
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        return False, f"Example timed out after 5 minutes", execution_time
    except Exception as e:
        execution_time = time.time() - start_time
        return False, f"Error running example: {e}", execution_time


def main():
    """Run all examples and provide a summary report."""
    print("Splurge-Tools: Running All Examples")
    print("=" * 60)
    print()
    
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
    ]
    
    # Verify all example files exist
    missing_files = []
    for filename in example_files:
        if not (examples_dir / filename).exists():
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ Missing example files: {missing_files}")
        sys.exit(1)
    
    # Run all examples
    results = []
    total_start_time = time.time()
    
    for filename in example_files:
        example_file = examples_dir / filename
        success, output, exec_time = run_example(example_file)
        results.append((filename, success, output, exec_time))
        
        if success:
            print(f"  SUCCESS {filename} completed successfully ({exec_time:.2f}s)")
        else:
            print(f"  FAILED {filename} failed ({exec_time:.2f}s)")
            print(f"     Error details available in summary report")
        print()
    
    total_time = time.time() - total_start_time
    
    # Generate summary report
    print("=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)
    print()
    
    successful = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    
    print(f"Total Examples: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print()
    
    if successful:
        print("SUCCESSFUL EXAMPLES:")
        for filename, _, _, exec_time in successful:
            print(f"  • {filename} ({exec_time:.2f}s)")
        print()
    
    if failed:
        print("FAILED EXAMPLES:")
        for filename, _, _, exec_time in failed:
            print(f"  • {filename} ({exec_time:.2f}s)")
        print()
        
        print("ERROR DETAILS:")
        print("-" * 40)
        for filename, _, output, _ in failed:
            print(f"\n{filename}:")
            print("-" * len(filename))
            print(output[:1000])  # Limit output length
            if len(output) > 1000:
                print("... (output truncated)")
            print()
    
    # Performance summary
    if successful:
        exec_times = [r[3] for r in successful]
        avg_time = sum(exec_times) / len(exec_times)
        max_time = max(exec_times)
        min_time = min(exec_times)
        
        print("PERFORMANCE SUMMARY:")
        print(f"  Average execution time: {avg_time:.2f}s")
        print(f"  Fastest example: {min_time:.2f}s")
        print(f"  Slowest example: {max_time:.2f}s")
        print()
    
    # Feature coverage summary
    print("FEATURE COVERAGE:")
    features = [
        "Type inference and validation",
        "DSV parsing and profiling", 
        "Tabular data models (in-memory and streaming)",
        "Text processing and normalization",
        "Data validation and transformation",
        "Random data generation",
        "Comprehensive ETL workflows"
    ]
    
    for i, feature in enumerate(features):
        status = "OK" if i < len(successful) else "ERROR"
        print(f"  {status} {feature}")
    print()
    
    # Exit with appropriate code
    if failed:
        print(f"FAILED: {len(failed)} examples failed. Check error details above.")
        sys.exit(1)
    else:
        print("SUCCESS: All examples completed successfully!")
        print("\nNext Steps:")
        print("• Explore individual example files for detailed explanations")
        print("• Check the examples/README.md for comprehensive documentation")
        print("• Run specific examples individually for focused learning")
        print("• Modify examples to test your own data and use cases")
        sys.exit(0)


if __name__ == "__main__":
    main()
