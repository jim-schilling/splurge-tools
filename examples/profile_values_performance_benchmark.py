#!/usr/bin/env python3
"""
Performance benchmark for profile_values function.

This example demonstrates the performance improvements achieved by the optimized
profile_values function compared to the original implementation.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import gc
import time

from splurge_tools.type_helper import _INCREMENTAL_TYPECHECK_THRESHOLD, DataType, profile_values

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
    empty_ratio: float = 0.1,
) -> list[str]:
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

    if data_type == "boolean":
        data = ["true"] * (data_count // 2) + ["false"] * (data_count - data_count // 2)
    elif data_type == "string":
        data = [f"string_{i}" for i in range(data_count)]
    elif data_type == "integer":
        data = [str(i) for i in range(data_count)]
    elif data_type == "float":
        data = [f"{i}.5" for i in range(data_count)]
    elif data_type == "mixed":
        # Mix of types that would require full analysis
        data = []
        for i in range(data_count):
            if i % 4 == 0:
                data.append(str(i))  # integer
            elif i % 4 == 1:
                data.append(f"{i}.5")  # float
            elif i % 4 == 2:
                data.append(f"string_{i}")  # string
            else:
                data.append("true" if i % 2 == 0 else "false")  # boolean
    else:
        msg = f"Unknown data type: {data_type}"
        raise ValueError(msg)

    # Add empty values
    if include_empty:
        data.extend([""] * empty_count)

    return data


def benchmark_profile_values(
    data: list[str],
    *,
    use_incremental: bool = True,
    iterations: int = 3,
) -> tuple[float, DataType]:
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
    if seconds < 1:
        return f"{seconds * _MILLISECOND_MULTIPLIER:.2f} ms"
    return f"{seconds:.2f} s"


def run_benchmark() -> None:
    """Run the complete performance benchmark."""

    # Test configurations
    dataset_sizes = _DATASET_SIZES
    data_types = ["boolean", "string", "integer", "float", "mixed"]

    # Results storage
    results = {}

    for data_type in data_types:
        for size in dataset_sizes:
            if size <= _INCREMENTAL_TYPECHECK_THRESHOLD:
                pass
            else:
                pass

            # Generate test data
            data = generate_test_data(data_type, size)

            # Benchmark with incremental checking (optimized)
            time_optimized, result_optimized = benchmark_profile_values(
                data,
                use_incremental=True,
            )

            # Benchmark without incremental checking (original)
            time_original, result_original = benchmark_profile_values(
                data,
                use_incremental=False,
            )

            # Calculate improvement
            time_improvement = ((time_original - time_optimized) / time_original) * _PERCENTAGE_MULTIPLIER

            # Store results
            results[(data_type, size)] = {
                "optimized_time": time_optimized,
                "original_time": time_original,
                "time_improvement": time_improvement,
                "result_type": result_optimized,
            }

            # Print results

    # Summary table

    for data_type in data_types:
        for size in dataset_sizes:
            results[(data_type, size)]

    # Overall statistics

    [r["time_improvement"] for r in results.values()]

    # Performance insights

    # Find best and worst cases
    max(results.items(), key=lambda x: x[1]["time_improvement"])
    min(results.items(), key=lambda x: x[1]["time_improvement"])


if __name__ == "__main__":
    try:
        run_benchmark()
    except Exception:
        import traceback

        traceback.print_exc()
