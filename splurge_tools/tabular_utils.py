"""
Shared utilities for tabular data processing.

This module centralizes header processing, row normalization, and helpers used
by in-memory and streaming tabular data models.
"""

from __future__ import annotations

import re
from typing import Iterable, Iterator, List


def process_headers(
    header_data: list[list[str]],
    *,
    header_rows: int
) -> tuple[list[list[str]], list[str]]:
    """Process header rows and return processed header data and column names.

    Args:
        header_data: Raw header data rows.
        header_rows: Number of header rows to merge.

    Returns:
        Tuple of (processed_header_data, column_names).
    """
    processed_header_data = header_data.copy()

    if header_rows > 1:
        merged_headers: list[str] = []
        for row in header_data:
            while len(merged_headers) < len(row):
                merged_headers.append("")
            for j, name in enumerate(row):
                if merged_headers[j]:
                    merged_headers[j] = f"{merged_headers[j]}_{name}"
                else:
                    merged_headers[j] = name
        processed_header_data = [merged_headers]

    if processed_header_data and processed_header_data[0]:
        raw_names = processed_header_data[0]
        column_names = [
            re.sub(r"\s+", " ", name).strip() if name and re.sub(r"\s+", " ", name).strip() else f"column_{i}"
            for i, name in enumerate(raw_names)
        ]
    else:
        column_names = []

    column_count = max((len(row) for row in header_data), default=0)
    while len(column_names) < column_count:
        column_names.append(f"column_{len(column_names)}")

    return processed_header_data, column_names


def normalize_rows(
    rows: list[list[str]],
    *,
    skip_empty_rows: bool
) -> list[list[str]]:
    """Normalize rows to equal length and optionally drop empty rows."""
    if not rows:
        return []

    max_columns = max(len(row) for row in rows)
    normalized: list[list[str]] = []
    for row in rows:
        if len(row) < max_columns:
            row = row + [""] * (max_columns - len(row))
        normalized.append(row)

    if skip_empty_rows:
        normalized = [row for row in normalized if not should_skip_row(row)]

    return normalized


def should_skip_row(row: list[str]) -> bool:
    """Return True if row is considered empty."""
    return all(cell.strip() == "" for cell in row)


def auto_column_names(count: int) -> list[str]:
    """Generate default column names column_0..column_{count-1}."""
    return [f"column_{i}" for i in range(count)]


