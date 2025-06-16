"""
This module provides data transformation utilities for tabular data.

Copyright (c) 2024 Jim Schilling

Please keep the copyright notice in this file and in the source code files.

This module is licensed under the MIT License.
"""
from typing import Any, Callable, Dict, List, Optional, Union
from collections import defaultdict
from jpy_tools.tabular_data_model import TabularDataModel
from jpy_tools.typed_tabular_data_model import TypedTabularDataModel


class DataTransformer:
    """
    A utility class for transforming tabular data.
    
    This class provides methods for common data transformations such as:
    - Pivoting data
    - Melting data
    - Grouping and aggregating
    - Column transformations
    - Data normalization
    """
    
    def __init__(self, data_model: Union[TabularDataModel, TypedTabularDataModel]):
        """
        Initialize the transformer with a data model.
        
        Args:
            data_model: The tabular data model to transform
        """
        self._model = data_model
        
    def pivot(
        self,
        index_cols: List[str],
        columns_col: str,
        values_col: str,
        agg_func: Optional[Callable[[List[Any]], Any]] = None
    ) -> TabularDataModel:
        """
        Pivot the data model to create a cross-tabulation.
        
        Args:
            index_cols: List of column names to use as index
            columns_col: Column name to use as columns
            values_col: Column name to use as values
            agg_func: Optional aggregation function for duplicate values
            
        Returns:
            New TabularDataModel with pivoted data
            
        Raises:
            ValueError: If any column names are invalid
        """
        # Validate column names
        for col in index_cols + [columns_col, values_col]:
            if col not in self._model.column_names:
                raise ValueError(f"Column {col} not found in data model")
        
        # Group data by index columns
        grouped_data = defaultdict(list)
        for row in self._model.iter_rows():
            index_key = tuple(row[col] for col in index_cols)
            grouped_data[index_key].append((row[columns_col], row[values_col]))
        
        # Create new header and data
        unique_columns = sorted(set(col for group in grouped_data.values() 
                                 for col, _ in group))
        header = index_cols + list(unique_columns)
        
        # Create new data rows
        new_data = []
        for index_key, group in grouped_data.items():
            row_data = list(index_key)
            value_dict = dict(group)
            
            # Apply aggregation if needed
            if agg_func is not None:
                value_dict = {k: agg_func([v for _, v in group if _ == k])
                            for k in unique_columns}
            
            # Add values for each column
            for col in unique_columns:
                row_data.append(str(value_dict.get(col, '')))
            new_data.append(row_data)
        
        return TabularDataModel([header] + new_data)
    
    def melt(
        self,
        id_vars: List[str],
        value_vars: List[str],
        var_name: str = 'variable',
        value_name: str = 'value'
    ) -> TabularDataModel:
        """
        Melt the data model from wide to long format.
        
        Args:
            id_vars: List of column names to use as identifier variables
            value_vars: List of column names to melt into rows
            var_name: Name for the variable column
            value_name: Name for the value column
            
        Returns:
            New TabularDataModel with melted data
            
        Raises:
            ValueError: If any column names are invalid
        """
        # Validate column names
        for col in id_vars + value_vars:
            if col not in self._model.column_names:
                raise ValueError(f"Column {col} not found in data model")
        
        # Create new header
        header = id_vars + [var_name, value_name]
        
        # Create new data rows
        new_data = []
        for row in self._model.iter_rows():
            for var in value_vars:
                new_row = [row[col] for col in id_vars]
                new_row.extend([var, row[var]])
                new_data.append(new_row)
        
        return TabularDataModel([header] + new_data)
    
    def group_by(
        self,
        group_cols: List[str],
        agg_dict: Dict[str, Callable[[List[Any]], Any]]
    ) -> TabularDataModel:
        """
        Group data by specified columns and apply aggregation functions.
        
        Args:
            group_cols: List of column names to group by
            agg_dict: Dictionary mapping column names to aggregation functions
            
        Returns:
            New TabularDataModel with grouped and aggregated data
            
        Raises:
            ValueError: If any column names are invalid
        """
        # Validate column names
        for col in group_cols + list(agg_dict.keys()):
            if col not in self._model.column_names:
                raise ValueError(f"Column {col} not found in data model")
        
        # Group data
        grouped_data = defaultdict(lambda: defaultdict(list))
        for row in self._model.iter_rows():
            group_key = tuple(row[col] for col in group_cols)
            for col, agg_func in agg_dict.items():
                grouped_data[group_key][col].append(row[col])
        
        # Create new header
        header = group_cols + list(agg_dict.keys())
        
        # Create new data rows
        new_data = []
        for group_key, agg_values in grouped_data.items():
            row_data = list(group_key)
            for col in agg_dict.keys():
                row_data.append(str(agg_dict[col](agg_values[col])))
            new_data.append(row_data)
        
        return TabularDataModel([header] + new_data)
    
    def transform_column(
        self,
        column: str,
        transform_func: Callable[[Any], Any]
    ) -> TabularDataModel:
        """
        Transform values in a column using a transformation function.
        
        Args:
            column: Name of column to transform
            transform_func: Function to apply to each value
            
        Returns:
            New TabularDataModel with transformed column
            
        Raises:
            ValueError: If column name is invalid
        """
        if column not in self._model.column_names:
            raise ValueError(f"Column {column} not found in data model")
        
        # Create new data with transformed column
        new_data = []
        for row in self._model.iter_rows():
            new_row = row.copy()
            new_row[column] = str(transform_func(row[column]))
            new_data.append([new_row[col] for col in self._model.column_names])
        
        return TabularDataModel([self._model.column_names] + new_data)
    
    def normalize_column(
        self,
        column: str,
        method: str = 'min-max',
        target_min: float = 0.0,
        target_max: float = 1.0
    ) -> TabularDataModel:
        """
        Normalize values in a numeric column.
        
        Args:
            column: Name of column to normalize
            method: Normalization method ('min-max' or 'z-score')
            target_min: Target minimum value for min-max normalization
            target_max: Target maximum value for min-max normalization
            
        Returns:
            New TabularDataModel with normalized column
            
        Raises:
            ValueError: If column name is invalid or method is unsupported
        """
        if column not in self._model.column_names:
            raise ValueError(f"Column {column} not found in data model")
        
        # Get column values and convert to float
        values = [float(v) for v in self._model.column_values(column)
                 if v and v.strip()]
        
        if not values:
            raise ValueError(f"No numeric values found in column {column}")
        
        if method == 'min-max':
            min_val = min(values)
            max_val = max(values)
            if min_val == max_val:
                return TabularDataModel([self._model.column_names] + [list(row.values()) for row in self._model.iter_rows()])
            
            def normalize(x: float) -> float:
                return target_min + (x - min_val) * (target_max - target_min) / (max_val - min_val)
                
        elif method == 'z-score':
            mean = sum(values) / len(values)
            std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
            if std == 0:
                return self._model
                
            def normalize(x: float) -> float:
                return (x - mean) / std
                
        else:
            raise ValueError(f"Unsupported normalization method: {method}")
        
        # Create new data with normalized column
        new_data = []
        for row in self._model.iter_rows():
            new_row = row.copy()
            value = row[column]
            if value and value.strip():
                new_row[column] = str(normalize(float(value)))
            new_data.append(list(new_row.values()))
        
        return TabularDataModel([self._model.column_names] + new_data) 