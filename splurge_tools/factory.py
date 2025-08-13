"""
Simplified constructors for tabular data models.

Backwards-incompatible change: factories and heuristics removed in favor of
explicit constructors.
"""

from typing import Iterator

from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel


def create_in_memory_model(
    data: list[list[str]],
    *,
    header_rows: int = 1,
    skip_empty_rows: bool = True
) -> TabularDataModel:
    return TabularDataModel(
        data,
        header_rows=header_rows,
        skip_empty_rows=skip_empty_rows
    )


def create_streaming_model(
    stream: Iterator[list[list[str]]],
    *,
    header_rows: int = 1,
    skip_empty_rows: bool = True,
    chunk_size: int = 1000
) -> StreamingTabularDataModel:
    return StreamingTabularDataModel(
        stream,
        header_rows=header_rows,
        skip_empty_rows=skip_empty_rows,
        chunk_size=chunk_size
    )
