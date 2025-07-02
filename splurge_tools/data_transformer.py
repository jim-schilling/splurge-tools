"""
Data transformation utilities for tabular data models.

Provides pivot, melt, group-by, and column transformation operations for TabularDataModel and TypedTabularDataModel.

Copyright (c) 2024 Jim Schilling

This module is licensed under the MIT License.
"""

from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Union

from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.typed_tabular_data_model import TypedTabularDataModel


class DataTransformer:
    """
    Utility for transforming tabular data models.

    Supports pivot, melt, group-by, and column transformation operations.
    """

    def __init__(
        self,
        data_model: Union[TabularDataModel, TypedTabularDataModel]
    ) -> None:
        """
        Initialize the DataTransformer.

        Args:
            data_model (TabularDataModel | TypedTabularDataModel): The data model to transform.
        """
        self._model = data_model

    def pivot(
        self,
        index_cols: List[str],
        columns_col: str,
        values_col: str,
        *,
        agg_func: Optional[Callable[[List[Any]], Any]] = None
    ) -> TabularDataModel:
        """
        Pivot the data model to create a cross-tabulation.

        Args:
            index_cols (List[str]): Columns to use as row indices.
            columns_col (str): Column to use as new columns.
            values_col (str): Column to use as values.
            agg_func (Optional[Callable[[List[Any]], Any]]): Aggregation function for duplicates.

        Returns:
            TabularDataModel: Pivoted data model.

        Raises:
            ValueError: If columns are invalid or duplicates exist without agg_func.
        """
        for col in index_cols + [columns_col, values_col]:
            if col not in self._model.column_names:
                raise ValueError(f"Column {col} not found in data model")

        grouped_data: defaultdict[Any, list[Any]] = defaultdict(list)
        duplicate_keys: set[Any] = set()

        for row in self._model.iter_rows():
            index_key = tuple(row[col] for col in index_cols)
            col_value = row[columns_col]
            val_value = row[values_col]
            if any(existing_col == col_value for existing_col, _ in grouped_data[index_key]):
                duplicate_keys.add(index_key)
            grouped_data[index_key].append((col_value, val_value))

        if duplicate_keys and not agg_func:
            duplicate_examples = list(duplicate_keys)[:3]
            raise ValueError(
                f"Duplicate values found for index keys: {duplicate_examples}. "
                "Please provide an aggregation function to handle duplicates."
            )

        unique_columns = sorted(
            {col for group in grouped_data.values() for col, _ in group}
        )
        header = index_cols + list(unique_columns)

        new_data: list[list[Any]] = []
        for index_key, group in grouped_data.items():
            row_data = list(index_key)
            value_dict = dict(group)
            if agg_func is not None:
                value_dict = {
                    k: agg_func([v for c, v in group if c == k]) for k in unique_columns
                }
            for col in unique_columns:
                row_data.append(str(value_dict.get(col, "")))
            new_data.append(row_data)

        return TabularDataModel([header] + new_data)

    def melt(
        self,
        id_vars: List[str],
        value_vars: List[str],
        *,
        var_name: str = "variable",
        value_name: str = "value"
    ) -> TabularDataModel:
        """
        Unpivot columns into rows (wide to long format).

        Args:
            id_vars (List[str]): Columns to use as identifier variables.
            value_vars (List[str]): Columns to unpivot.
            var_name (str): Name for the variable column.
            value_name (str): Name for the value column.

        Returns:
            TabularDataModel: Melted data model.

        Raises:
            ValueError: If columns are invalid.
        """
        for col in id_vars + value_vars:
            if col not in self._model.column_names:
                raise ValueError(f"Column {col} not found in data model")

        header = id_vars + [var_name, value_name]
        new_data: list[list[Any]] = [
            [*(row[col] for col in id_vars), var, row[var]]
            for row in self._model.iter_rows() for var in value_vars
        ]
        return TabularDataModel([header] + new_data)

    def group_by(
        self,
        group_cols: List[str],
        agg_dict: Dict[str, Callable[[List[Any]], Any]]
    ) -> TabularDataModel:
        """
        Group data by columns and aggregate.

        Args:
            group_cols (List[str]): Columns to group by.
            agg_dict (Dict[str, Callable[[List[Any]], Any]]): Aggregation functions per column.

        Returns:
            TabularDataModel: Grouped and aggregated data model.

        Raises:
            ValueError: If columns are invalid.
        """
        for col in group_cols + list(agg_dict.keys()):
            if col not in self._model.column_names:
                raise ValueError(f"Column {col} not found in data model")

        grouped_data: defaultdict[Any, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))
        for row in self._model.iter_rows():
            group_key = tuple(row[col] for col in group_cols)
            for col in agg_dict.keys():
                grouped_data[group_key][col].append(row[col])

        header = group_cols + list(agg_dict.keys())
        new_data: list[list[Any]] = [
            list(group_key) + [str(agg_dict[col](agg_values[col])) for col in agg_dict.keys()]
            for group_key, agg_values in grouped_data.items()
        ]
        return TabularDataModel([header] + new_data)

    def transform_column(
        self,
        column: str,
        transform_func: Callable[[Any], Any]
    ) -> TabularDataModel:
        """
        Transform a column using a function.

        Args:
            column (str): Name of column to transform.
            transform_func (Callable[[Any], Any]): Function to apply to each value.

        Returns:
            TabularDataModel: Data model with transformed column.

        Raises:
            ValueError: If column is invalid.
        """
        if column not in self._model.column_names:
            raise ValueError(f"Column {column} not found in data model")

        new_data: list[list[Any]] = [
            [str(transform_func(row[column])) if col == column else row[col] for col in self._model.column_names]
            for row in self._model.iter_rows()
        ]
        return TabularDataModel([self._model.column_names] + new_data)
