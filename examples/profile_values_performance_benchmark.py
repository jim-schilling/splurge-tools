#!/usr/bin/env python3
"""
Performance benchmark for profile_values function.

This example demonstrates the performance improvements achieved by the optimized
profile_values function compared to the original implementation.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import time
import gc
from typing import List, Tuple
from splurge_tools.type_helper import profile_values, DataType, _INCREMENTAL_TYPECHECK_THRESHOLD


# Module-level constants for performance benchmarking
_MICROSECOND_THRESHOLD = 0.001  # Threshold for microsecond formatting
_MILLISECOND_MULTIPLIER = 1000  # Multiplier for millisecond conversion
_MICROSECOND_MULTIPLIER = 1_000_000  # Multiplier for microsecond conversion
_PERCENTAGE_MULTIPLIER = 100  # Multiplier for percentage calculation
_DATASET_SIZES = [5_000, 25_000, 100_000, 250_000]  # Dataset sizes to test


def generate_test_data(
    data_type: str,
    size: int,
    *,
    include_empty: bool = True,
    empty_ratio: float = 0.1
) -> List[str]:
    """
    Generate test data of specified type and size.
    
    Args:
        data_type: Type of data to generate ('boolean', 'string', 'integer', 'float', 'mixed')
        size: Number of items to generate
        include_empty: Whether to include empty values
        empty_ratio: Ratio of empty values to include (0.0 to 1.0)
    
    Returns:
        List of test data
    """
    empty_count = int(size * empty_ratio) if include_empty else 0
    data_count = size - empty_count
    
    if data_type == 'boolean':
        data = ['true'] * (data_count // 2) + ['false'] * (data_count - data_count // 2)
    elif data_type == 'string':
        data = [f'string_{i}' for i in range(data_count)]
    elif data_type == 'integer':
        data = [str(i) for i in range(data_count)]
    elif data_type == 'float':
        data = [f'{i}.5' for i in range(data_count)]
    elif data_type == 'mixed':
        # Mix of types that would require full analysis
        data = []
        for i in range(data_count):
            if i % 4 == 0:
                data.append(str(i))  # integer
            elif i % 4 == 1:
                data.append(f'{i}.5')  # float
            elif i % 4 == 2:
                data.append(f'string_{i}')  # string
            else:
                data.append('true' if i % 2 == 0 else 'false')  # boolean
    else:
        raise ValueError(f"Unknown data type: {data_type}")
    
    # Add empty values
    if include_empty:
        data.extend([''] * empty_count)
    
    return data


def benchmark_profile_values(
    data: List[str],
    *,
    use_incremental: bool = True,
    iterations: int = 3
) -> Tuple[float, DataType]:
    """
    Benchmark profile_values function performance.
    
    Args:
        data: Test data to profile
        use_incremental: Whether to use incremental type checking
        iterations: Number of iterations to run for averaging
    
    Returns:
        Tuple of (average_time_seconds, result_type)
    """
    # Force garbage collection before measurement
    gc.collect()
    
    # Time the function
    times = []
    result_type = None
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        result_type = profile_values(data, use_incremental_typecheck=use_incremental)
        end_time = time.perf_counter()
        times.append(end_time - start_time)
    
    # Calculate average time
    avg_time = sum(times) / len(times)
    
    return avg_time, result_type


def format_time(seconds: float) -> str:
    """Format time in a human-readable format."""
    if seconds < _MICROSECOND_THRESHOLD:
        return f"{seconds * _MICROSECOND_MULTIPLIER:.2f} μs"
    elif seconds < 1:
        return f"{seconds * _MILLISECOND_MULTIPLIER:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def run_benchmark() -> None:
    """Run the complete performance benchmark."""
    print("=" * 80)
    print("PROFILE_VALUES PERFORMANCE BENCHMARK")
    print("=" * 80)
    print()
    print(f"Note: Incremental type checking is only enabled for lists larger than {_INCREMENTAL_TYPECHECK_THRESHOLD} items.")
    print()
    
    # Test configurations
    dataset_sizes = _DATASET_SIZES
    data_types = ['boolean', 'string', 'integer', 'float', 'mixed']
    
    # Results storage
    results = {}
    
    for data_type in data_types:
        print(f"Testing {data_type.upper()} data:")
        print("-" * 40)
        
        for size in dataset_sizes:
            print(f"  Dataset size: {size:,}")
            if size <= _INCREMENTAL_TYPECHECK_THRESHOLD:
                print(f"    (Incremental type checking is DISABLED for size <= {_INCREMENTAL_TYPECHECK_THRESHOLD})")
            else:
                print(f"    (Incremental type checking is ENABLED for size > {_INCREMENTAL_TYPECHECK_THRESHOLD})")
            
            # Generate test data
            data = generate_test_data(data_type, size)
            
            # Benchmark with incremental checking (optimized)
            time_optimized, result_optimized = benchmark_profile_values(
                data, use_incremental=True
            )
            
            # Benchmark without incremental checking (original)
            time_original, result_original = benchmark_profile_values(
                data, use_incremental=False
            )
            
            # Calculate improvement
            time_improvement = ((time_original - time_optimized) / time_original) * _PERCENTAGE_MULTIPLIER
            
            # Store results
            results[(data_type, size)] = {
                'optimized_time': time_optimized,
                'original_time': time_original,
                'time_improvement': time_improvement,
                'result_type': result_optimized
            }
            
            # Print results
            print(f"    Optimized:   {format_time(time_optimized)}")
            print(f"    Original:    {format_time(time_original)}")
            print(f"    Improvement: {time_improvement:+.1f}%")
            print(f"    Result:      {result_optimized.value}")
            print()
    
    # Summary table
    print("=" * 80)
    print("SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Data Type':<12} {'Size':<10} {'Optimized':<12} {'Original':<12} {'Improvement':<12} {'Result':<10}")
    print("-" * 80)
    
    for data_type in data_types:
        for size in dataset_sizes:
            result = results[(data_type, size)]
            print(f"{data_type:<12} {size:<10,} {format_time(result['optimized_time']):<12} "
                  f"{format_time(result['original_time']):<12} {result['time_improvement']:+6.1f}%{'':<6} "
                  f"{result['result_type'].value:<10}")
    
    print()
    
    # Overall statistics
    print("=" * 80)
    print("OVERALL STATISTICS")
    print("=" * 80)
    
    all_time_improvements = [r['time_improvement'] for r in results.values()]
    
    print(f"Average time improvement: {sum(all_time_improvements) / len(all_time_improvements):+.1f}%")
    print(f"Best time improvement: {max(all_time_improvements):+.1f}%")
    print(f"Worst time improvement: {min(all_time_improvements):+.1f}%")
    
    # Performance insights
    print()
    print("=" * 80)
    print("PERFORMANCE INSIGHTS")
    print("=" * 80)
    
    # Find best and worst cases
    best_case = max(results.items(), key=lambda x: x[1]['time_improvement'])
    worst_case = min(results.items(), key=lambda x: x[1]['time_improvement'])
    
    print(f"Best optimization case: {best_case[0][0]} data, {best_case[0][1]:,} items")
    print(f"  Time improvement: {best_case[1]['time_improvement']:+.1f}%")
    print(f"  Result type: {best_case[1]['result_type'].value}")
    
    print(f"Worst optimization case: {worst_case[0][0]} data, {worst_case[0][1]:,} items")
    print(f"  Time improvement: {worst_case[1]['time_improvement']:+.1f}%")
    print(f"  Result type: {worst_case[1]['result_type'].value}")
    
    print()
    print(f"Note: Early termination is only enabled for lists larger than {_INCREMENTAL_TYPECHECK_THRESHOLD} items.")
    print("- Boolean data (can terminate at 25% check point)")
    print("- String data (can terminate at 25% check point)")
    print("- Empty/None data (can terminate immediately)")
    print("- Mixed data with clear patterns (can terminate early)")
    print()
    print("Complex cases (mixed int/float, all-digit strings) require full analysis")
    print("but still benefit from the optimized implementation.")


if __name__ == "__main__":
    try:
        run_benchmark()
    except Exception as e:
        print(f"Error running benchmark: {e}")
        import traceback
        traceback.print_exc() 