# splurge-tools - Detailed Project Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture & Design](#architecture--design)
3. [Core Components](#core-components)
4. [API Reference](#api-reference)
5. [Usage Patterns](#usage-patterns)
6. [Performance Considerations](#performance-considerations)
7. [Best Practices](#best-practices)
8. [Migration Guide](#migration-guide)
9. [Contributing](#contributing)

## Overview

### Mission Statement

splurge-tools is a comprehensive Python library designed to provide robust, efficient, and type-safe utilities for data processing, validation, and transformation. The library emphasizes:

- **Memory Efficiency**: Streaming capabilities for datasets larger than available RAM
- **Type Safety**: Comprehensive type annotations and runtime validation
- **Performance**: Optimized algorithms for large-scale data processing
- **Reliability**: Comprehensive error handling and edge case coverage
- **Maintainability**: Clean architecture with clear separation of concerns

### Design Philosophy

The library follows several key design principles:

1. **Fail Fast**: Validate inputs early and provide clear error messages
2. **Composition over Inheritance**: Prefer composition and protocols over deep inheritance hierarchies
3. **Streaming First**: Design for memory efficiency and streaming workflows
4. **Type Safety**: Leverage Python's type system for better reliability
5. **Backward Compatibility**: Maintain API stability while improving internals

### Versioning Strategy

The project uses [Calendar Versioning (CalVer)](https://calver.org/) with the format `YYYY.MINOR.MICRO`:

- `YYYY`: Year of release
- `MINOR`: Feature release within the year
- `MICRO`: Bug fix or patch release

This versioning scheme provides clear temporal context and avoids version number inflation.

## Architecture & Design

### Module Organization

```
splurge_tools/
├── __init__.py              # Package initialization
├── base58.py               # Base58 encoding/decoding utilities
├── case_helper.py          # Text case transformation utilities
├── common_utils.py         # Common utility functions
├── data_transformer.py     # Data transformation operations
├── data_validator.py       # Data validation framework
├── decorators.py           # Common decorators
├── dsv_helper.py           # Delimited value parsing
├── exceptions.py           # Custom exception classes
├── factory.py              # Factory functions for data models
├── path_validator.py       # File path validation utilities
├── protocols.py            # Protocol definitions
├── random_helper.py        # Random data generation
├── resource_manager.py     # Resource management utilities
├── streaming_tabular_data_model.py  # Streaming data models
├── string_tokenizer.py     # String tokenization utilities
├── tabular_data_model.py   # In-memory tabular data models
├── tabular_utils.py        # Shared tabular processing utilities
├── text_file_helper.py     # Text file processing utilities
├── text_normalizer.py      # Text normalization utilities
├── type_helper.py          # Type inference and conversion
└── utility_helper.py       # Additional utility functions
```

### Core Design Patterns

#### Protocol-Based Architecture

The library extensively uses Python protocols for type-safe interfaces:

```python
from typing import Protocol, Iterator, Any
from splurge_tools.protocols import TabularDataProtocol

class StreamingTabularDataProtocol(Protocol):
    """Protocol for streaming tabular data operations."""

    @property
    def column_names(self) -> list[str]: ...

    @property
    def column_count(self) -> int: ...

    def __iter__(self) -> Iterator[list[str]]: ...

    def iter_rows_as_dicts(self) -> Iterator[dict[str, str]]: ...
```

#### Factory Pattern

Factory functions provide consistent object creation:

```python
from splurge_tools.factory import create_in_memory_model, create_streaming_model

# Explicit factory functions replace generic constructors
model = create_in_memory_model(data, header_rows=1)
stream_model = create_streaming_model(file_stream, chunk_size=1000)
```

#### Decorator Pattern

Common decorators handle cross-cutting concerns:

```python
from splurge_tools.decorators import handle_empty_value

@handle_empty_value
def process_text(text: str) -> str:
    """Process text safely, returning empty string for None/empty inputs."""
    return text.upper()
```

### Error Handling Strategy

#### Custom Exception Hierarchy

```
SplurgeError (base exception)
├── SplurgeParameterError (parameter validation)
├── SplurgeValidationError (data validation)
├── SplurgeFormatError (format validation)
├── SplurgeRangeError (range/bounds validation)
├── SplurgeFileError (file operation errors)
├── SplurgeTypeError (type conversion errors)
└── SplurgeValueError (value validation errors)
```

#### Error Context

All exceptions include detailed context information:

```python
raise SplurgeParameterError(
    message="Invalid parameter value",
    parameter_name="chunk_size",
    parameter_value=value,
    expected_type=int,
    details={"minimum": 100, "maximum": 10000}
)
```

## Core Components

### Data Processing Pipeline

#### Type Inference and Conversion

The `type_helper` module provides comprehensive type handling:

```python
from splurge_tools.type_helper import String, DataType

# Automatic type inference
assert String.infer_type("2023-12-25") == DataType.DATE
assert String.infer_type("123.45") == DataType.FLOAT
assert String.infer_type("true") == DataType.BOOLEAN

# Safe type conversion with defaults
date_val = String.to_date("2023-12-25")
float_val = String.to_float("invalid", default=0.0)
```

#### Delimited Value Processing

The `dsv_helper` module handles CSV, TSV, and custom delimited formats:

```python
from splurge_tools.dsv_helper import DsvHelper

# Parse with automatic delimiter detection
data = DsvHelper.parse("data.csv", delimiter=",")

# Profile columns for data analysis
profile = DsvHelper.profile_columns(data)
# Returns: {"column_name": {"datatype": DataType.STRING, "count": 1000}}

# Streaming for large files
stream = DsvHelper.parse_stream("large_file.csv", delimiter=",")
```

### Data Models

#### In-Memory Model

```python
from splurge_tools.tabular_data_model import TabularDataModel

# Create from data
model = TabularDataModel(
    data=[["Name", "Age"], ["Alice", "25"], ["Bob", "30"]],
    header_rows=1
)

# Access data
print(model.row_count)  # 2
print(model.column_names)  # ["Name", "Age"]
print(model.row(0))  # ["Alice", "25"]
```

#### Streaming Model

```python
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel

# Process large datasets efficiently
model = StreamingTabularDataModel(
    stream=dsv_stream,
    header_rows=1,
    chunk_size=1000
)

# Memory-efficient iteration
for row_dict in model.iter_rows():
    process_row(row_dict)
```

#### Typed Views

```python
# Create typed view for type-safe access
typed_model = model.to_typed({
    "Age": int,
    "Salary": float
})

for row in typed_model:
    # Type-safe access with automatic conversion
    age: int = row["Age"]
    salary: float = row["Salary"]
```

### Text Processing

#### String Tokenization

```python
from splurge_tools.string_tokenizer import StringTokenizer

tokenizer = StringTokenizer(delimiter=",")

# Parse delimited strings
result = tokenizer.parse("Name,Age,City")
# ["Name", "Age", "City"]

# Handle quoted values
result = tokenizer.parse('"John Doe","25","New York"')
# ["John Doe", "25", "New York"]
```

#### Case Conversion

```python
from splurge_tools.case_helper import CaseHelper

# Convert between case styles
snake_case = CaseHelper.to_snake_case("CamelCase")      # "camel_case"
camel_case = CaseHelper.to_camel_case("kebab-case")      # "kebabCase"
pascal_case = CaseHelper.to_pascal_case("snake_case")    # "SnakeCase"
```

### Validation Framework

#### Data Validation

```python
from splurge_tools.data_validator import DataValidator

validator = DataValidator()

# Validate data against rules
is_valid = validator.validate(data, rules)

if not is_valid:
    errors = validator.get_errors()
    for error in errors:
        print(f"Validation error: {error}")
```

### Random Data Generation

#### Secure Random Generation

```python
from splurge_tools.random_helper import RandomHelper

# Generate secure random strings
api_key = RandomHelper.as_base58_like(length=32)
# Guaranteed to contain alpha, digit, and symbol

# Generate secure floats
random_float = RandomHelper.as_float_range(
    start=0.0,
    end=100.0,
    secure=True  # Uses secrets module
)
```

## API Reference

### Type Helper Module

#### String Class

```python
class String:
    # Type inference
    @staticmethod
    def infer_type(value: str) -> DataType: ...

    # Type conversion methods
    @staticmethod
    def to_bool(value: str, *, default: bool | None = None) -> bool: ...
    @staticmethod
    def to_int(value: str, *, default: int | None = None) -> int: ...
    @staticmethod
    def to_float(value: str, *, default: float | None = None) -> float: ...
    @staticmethod
    def to_date(value: str, *, default: date | None = None) -> date: ...
    @staticmethod
    def to_time(value: str, *, default: time | None = None) -> time: ...
    @staticmethod
    def to_datetime(value: str, *, default: datetime | None = None) -> datetime: ...

    # Validation methods
    @staticmethod
    def is_bool_like(value: str) -> bool: ...
    @staticmethod
    def is_int_like(value: str) -> bool: ...
    @staticmethod
    def is_float_like(value: str) -> bool: ...
    @staticmethod
    def is_date_like(value: str) -> bool: ...
    @staticmethod
    def is_time_like(value: str) -> bool: ...
    @staticmethod
    def is_datetime_like(value: str) -> bool: ...
```

### Data Model Classes

#### TabularDataModel

```python
class TabularDataModel:
    def __init__(
        self,
        data: list[list[str]],
        *,
        header_rows: int = 1,
        skip_empty_rows: bool = True
    ) -> None: ...

    @property
    def row_count(self) -> int: ...
    @property
    def column_count(self) -> int: ...
    @property
    def column_names(self) -> list[str]: ...

    def row(self, index: int) -> list[str]: ...
    def row_as_list(self, index: int) -> list[str]: ...
    def row_as_tuple(self, index: int) -> tuple[str, ...]: ...
    def column_values(self, column_name: str) -> list[str]: ...
    def cell_value(self, row_index: int, column_name: str) -> str: ...
    def to_typed(self, type_configs: dict[str, Any] | None = None) -> TypedTabularDataModel: ...
```

#### StreamingTabularDataModel

```python
class StreamingTabularDataModel:
    def __init__(
        self,
        stream: Iterator[list[str]],
        *,
        header_rows: int = 1,
        chunk_size: int = 1000,
        skip_empty_rows: bool = True
    ) -> None: ...

    @property
    def column_names(self) -> list[str]: ...
    @property
    def column_count(self) -> int: ...

    def __iter__(self) -> Iterator[list[str]]: ...
    def iter_rows_as_dicts(self) -> Iterator[dict[str, str]]: ...
    def iter_rows_as_tuples(self) -> Iterator[tuple[str, ...]]: ...
    def reset_stream(self) -> None: ...
```

## Usage Patterns

### Processing Large CSV Files

```python
from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel
from splurge_tools.factory import create_streaming_model

# Method 1: Direct streaming
with open("large_dataset.csv", "r") as f:
    stream = DsvHelper.parse_stream(f, delimiter=",")
    model = StreamingTabularDataModel(stream, header_rows=1, chunk_size=5000)

    total_rows = 0
    for row in model:
        process_row(row)
        total_rows += 1

# Method 2: Factory pattern
with open("large_dataset.csv", "r") as f:
    model = create_streaming_model(f, header_rows=1, chunk_size=5000)

    for row_dict in model.iter_rows_as_dicts():
        process_row_dict(row_dict)
```

### Type-Safe Data Processing

```python
from splurge_tools.type_helper import String, DataType
from splurge_tools.tabular_data_model import TabularDataModel

# Load and type data
data = [
    ["Name", "Age", "Salary", "IsActive"],
    ["Alice", "25", "50000", "true"],
    ["Bob", "30", "60000", "false"],
    ["Charlie", "35", "70000", "true"]
]

model = TabularDataModel(data, header_rows=1)

# Create typed view
typed_model = model.to_typed({
    "Age": int,
    "Salary": float,
    "IsActive": bool
})

# Process with type safety
for row in typed_model:
    name: str = row["Name"]
    age: int = row["Age"]
    salary: float = row["Salary"]
    is_active: bool = row["IsActive"]

    # Type-safe operations
    if is_active and age > 25:
        bonus = salary * 0.1
        print(f"{name}: ${bonus:.2f} bonus")
```

### ETL Pipeline Example

```python
from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.data_transformer import DataTransformer
from splurge_tools.data_validator import DataValidator

def etl_pipeline(input_file: str, output_file: str):
    """Complete ETL pipeline example."""

    # Extract: Load data
    data = DsvHelper.parse(input_file, delimiter=",")

    # Transform: Clean and reshape data
    transformer = DataTransformer(data)

    # Remove duplicates
    deduplicated = transformer.drop_duplicates()

    # Fill missing values
    cleaned = transformer.fill_missing("Unknown")

    # Pivot data
    pivoted = transformer.pivot(
        index_cols=["category"],
        columns_col="month",
        values_col="sales"
    )

    # Validate: Check data quality
    validator = DataValidator()

    rules = {
        "sales": lambda x: float(x) >= 0,
        "category": lambda x: len(x.strip()) > 0
    }

    if not validator.validate(pivoted, rules):
        errors = validator.get_errors()
        raise ValueError(f"Validation failed: {errors}")

    # Load: Save results
    DsvHelper.write(cleaned, output_file, delimiter=",")
```

## Performance Considerations

### Memory Management

#### Streaming vs In-Memory

**Use StreamingTabularDataModel when:**
- Dataset size > 100MB
- Memory is limited
- Processing large files sequentially
- Only need to iterate once through the data

**Use TabularDataModel when:**
- Dataset fits in memory
- Need random access to rows
- Require multiple iterations
- Need to perform complex queries

#### Chunk Size Optimization

```python
# Optimal chunk sizes
small_files = StreamingTabularDataModel(stream, chunk_size=1000)   # < 10MB files
medium_files = StreamingTabularDataModel(stream, chunk_size=5000)  # 10-100MB files
large_files = StreamingTabularDataModel(stream, chunk_size=10000)  # > 100MB files
```

### Performance Benchmarks

#### Type Inference Optimization

The `profile_values()` function includes incremental type checking optimization:

- **25% checkpoint**: Early termination for uniform data
- **50% checkpoint**: Pattern recognition for mixed types
- **75% checkpoint**: Statistical confidence for type determination

```python
from splurge_tools.type_helper import profile_values

# Performance optimized for large datasets
profile = profile_values(large_dataset, use_incremental_typecheck=True)
# 2-3x faster for datasets > 10,000 items
```

### I/O Optimization

#### Text File Processing

```python
from splurge_tools.text_file_helper import TextFileHelper

# Efficient streaming with footer handling
with TextFileHelper.load_as_stream(
    "large_file.txt",
    chunk_size=8192,
    skip_header_rows=1,
    skip_footer_rows=2
) as stream:
    for chunk in stream:
        process_chunk(chunk)
```

## Best Practices

### Error Handling

#### Defensive Programming

```python
from splurge_tools.exceptions import SplurgeError

def process_data_safely(data: list[str]) -> dict[str, Any]:
    """Process data with comprehensive error handling."""
    try:
        # Validate inputs
        if not data:
            raise SplurgeParameterError("Data cannot be empty")

        # Process with error recovery
        result = process_data(data)

        # Validate outputs
        if not result:
            raise SplurgeValidationError("Processing produced no results")

        return result

    except SplurgeError:
        # Re-raise splurge-tools exceptions
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise SplurgeError(f"Unexpected error: {e}") from e
```

### Type Safety

#### Type Hints and Validation

```python
from typing import assert_type
from splurge_tools.type_helper import String

def process_user_data(name: str, age: str, email: str) -> dict[str, Any]:
    """Process user data with type safety."""

    # Validate and convert types
    validated_name = String.to_string(name).strip()
    validated_age = String.to_int(age, default=0)
    validated_email = String.to_string(email).lower()

    # Additional validation
    if not validated_name:
        raise SplurgeValidationError("Name cannot be empty")
    if not (13 <= validated_age <= 120):
        raise SplurgeRangeError("Age must be between 13 and 120")

    return {
        "name": validated_name,
        "age": validated_age,
        "email": validated_email
    }
```

### Memory Management

#### Resource Cleanup

```python
from contextlib import contextmanager
from splurge_tools.resource_manager import safe_file_operation

@contextmanager
def process_large_file(file_path: str):
    """Context manager for safe file processing."""
    try:
        with safe_file_operation(file_path, "read") as file:
            # Process file
            yield file
    except Exception:
        # Cleanup on error
        raise
    finally:
        # Additional cleanup if needed
        pass
```

### Testing

#### Test Organization

```python
import pytest
from splurge_tools.factory import create_in_memory_model

class TestDataProcessing:
    """Test data processing functionality."""

    @pytest.fixture
    def sample_data(self):
        """Provide sample data for tests."""
        return [
            ["Name", "Age", "City"],
            ["Alice", "25", "NYC"],
            ["Bob", "30", "LA"]
        ]

    def test_data_model_creation(self, sample_data):
        """Test basic data model creation."""
        model = create_in_memory_model(sample_data, header_rows=1)

        assert model.row_count == 2
        assert model.column_count == 3
        assert model.column_names == ["Name", "Age", "City"]

    def test_data_validation(self, sample_data):
        """Test data validation rules."""
        from splurge_tools.data_validator import DataValidator

        validator = DataValidator()
        rules = {"Age": lambda x: int(x) > 0}

        assert validator.validate(sample_data[1:], rules)
```

## Migration Guide

### From Version 0.3.x to 2025.x

#### Breaking Changes

1. **Factory Pattern Changes**
   ```python
   # Old (removed)
   from splurge_tools.factory import DataModelFactory
   model = DataModelFactory.create_model(data)

   # New
   from splurge_tools.factory import create_in_memory_model
   model = create_in_memory_model(data)
   ```

2. **TypedTabularDataModel Removal**
   ```python
   # Old (removed)
   typed_model = TypedTabularDataModel(data, type_configs)

   # New
   model = TabularDataModel(data)
   typed_model = model.to_typed(type_configs)
   ```

3. **Validation API Changes**
   ```python
   # Old (removed)
   is_valid = validator.validate(data)
   errors = validator.errors

   # New
   is_valid = validator.validate(data, rules)
   if not is_valid:
       errors = validator.get_errors()
   ```

#### Migration Steps

1. **Update Imports**
   ```python
   # Replace factory imports
   - from splurge_tools.factory import DataModelFactory
   + from splurge_tools.factory import create_in_memory_model, create_streaming_model

   # Replace validation imports
   - from splurge_tools.validation_utils import Validator
   + from splurge_tools.data_validator import DataValidator
   ```

2. **Update Data Model Creation**
   ```python
   # Replace generic factory calls
   - model = DataModelFactory.create_model(data)
   + model = create_in_memory_model(data, header_rows=1)

   # Replace streaming model creation
   - stream_model = StreamingTabularDataModel(data_stream)
   + stream_model = create_streaming_model(data_stream, header_rows=1, chunk_size=1000)
   ```

3. **Update Validation Code**
   ```python
   # Replace validation patterns
   - validator = Validator()
   - is_valid = validator.validate_non_empty_string(value)
   + validator = DataValidator()
   + is_valid = validator.validate([value], {"value": lambda x: len(x.strip()) > 0})
   ```

### Compatibility Matrix

| Feature | 0.3.x | 2025.x | Migration Required |
|---------|-------|--------|-------------------|
| Factory Pattern | Generic | Explicit | Yes |
| Typed Models | TypedTabularDataModel | .to_typed() | Yes |
| Validation | Centralized | Inline | Yes |
| Error Handling | Basic | Detailed | No |
| Streaming | Limited | Enhanced | No |
| Type Safety | Partial | Full | No |

## Contributing

### Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/jim-schilling/splurge-tools.git
   cd splurge-tools
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run Quality Checks**
   ```bash
   # Type checking
   mypy splurge_tools/

   # Linting and formatting
   ruff check . --fix
   ruff format .

   # Testing
   pytest tests/ --cov=splurge_tools --cov-report=html
   ```

### Code Standards

#### Type Annotations

```python
# ✅ Good: Explicit types
def process_data(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Process data with clear type annotations."""
    pass

# ❌ Bad: Missing type annotations
def process_data(data):
    pass
```

#### Method Signatures

```python
# ✅ Good: Keyword-only defaults
def process_data(
    self,
    data: list[str],
    *,
    validate: bool = True,
    chunk_size: int = 1000
) -> None:
    """Process data with keyword-only defaults."""
    pass

# ❌ Bad: Positional defaults
def process_data(self, data: list[str], validate: bool = True) -> None:
    pass
```

#### Error Handling

```python
# ✅ Good: Specific exceptions with context
def validate_age(age_str: str) -> int:
    """Validate and convert age string."""
    try:
        age = int(age_str)
    except ValueError as e:
        raise SplurgeTypeError(
            f"Invalid age format: {age_str}",
            expected_type=int,
            actual_value=age_str
        ) from e

    if not (0 <= age <= 150):
        raise SplurgeRangeError(
            f"Age out of range: {age}",
            value=age,
            min_value=0,
            max_value=150
        )

    return age

# ❌ Bad: Generic exceptions
def validate_age(age_str: str) -> int:
    """Validate and convert age string."""
    age = int(age_str)
    if age < 0 or age > 150:
        raise ValueError("Invalid age")
    return age
```

### Testing Guidelines

#### Test Structure

```python
import pytest
from splurge_tools.factory import create_in_memory_model

class TestDataModel:
    """Test cases for data model functionality."""

    @pytest.fixture
    def sample_model(self):
        """Provide sample data model for tests."""
        data = [
            ["Name", "Age"],
            ["Alice", "25"],
            ["Bob", "30"]
        ]
        return create_in_memory_model(data, header_rows=1)

    def test_row_count(self, sample_model):
        """Test row count calculation."""
        assert sample_model.row_count == 2

    def test_column_access(self, sample_model):
        """Test column access methods."""
        assert sample_model.column_names == ["Name", "Age"]
        assert sample_model.column_count == 2

    @pytest.mark.parametrize("row_index,expected", [
        (0, ["Alice", "25"]),
        (1, ["Bob", "30"])
    ])
    def test_row_access(self, sample_model, row_index, expected):
        """Test row access with parametrization."""
        assert sample_model.row(row_index) == expected
```

#### Coverage Requirements

- **Minimum Coverage**: 85% overall
- **Core Modules**: 95%+ coverage required
- **New Features**: 100% coverage required
- **Edge Cases**: Comprehensive error condition testing

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Write Tests First** (TDD approach)
   ```bash
   # Write failing tests
   pytest tests/test_new_feature.py -v

   # Implement feature
   # Tests should pass
   pytest tests/test_new_feature.py -v
   ```

3. **Quality Checks**
   ```bash
   # Run all quality checks
   mypy splurge_tools/
   ruff check . --fix
   ruff format .
   pytest tests/ --cov=splurge_tools
   ```

4. **Update Documentation**
   - Update docstrings
   - Update examples if needed
   - Update CHANGELOG.md

5. **Submit Pull Request**
   - Clear description of changes
   - Link to related issues
   - Request review from maintainers

### Release Process

1. **Version Bump**: Update version in `pyproject.toml`
2. **Changelog**: Update CHANGELOG.md with new version
3. **Tag Release**: Create git tag with version
4. **Build Distribution**: `python build_sdist.py`
5. **Publish**: Upload to PyPI

---

This detailed documentation provides comprehensive guidance for using, understanding, and contributing to the splurge-tools library. For additional support or questions, please refer to the main README.md or open an issue on GitHub.
