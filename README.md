# jpy-tools

A Python package providing tools for data type handling, validation, and text processing.

## Description

jpy-tools is a collection of Python utilities focused on:
- Data type handling and validation
- Text file processing and manipulation
- String tokenization and parsing
- Text case transformations
- Delimited separated value parsing
- Tabular data model class
- Typed tabular data model class
- Data validator class
- Random data class
- Data transformation class
- Text normalizer class
- Python 3.10+ compatibility

## Installation

```bash
pip install jpy-tools
```

## Features

- `type_helper.py`: Comprehensive type validation and conversion utilities
- `text_file_helper.py`: Text file processing and manipulation tools
- `string_tokenizer.py`: String parsing and tokenization utilities
- `case_helper.py`: Text case transformation utilities
- `dsv_helper.py`: Delimited separated value utilities
- `tabular_data_model.py`: Data model for tabular datasets
- `typed_tabular_data_model.py`: Type data model based on tabular data model
- `data_validator.py`: Data validator class
- `random_helper.py`: Random data class and methods for generating data
- `data_transformer.py`: Data transformation utility class
- `text_normalizer.py`: Text normalization utility class

## Development

### Requirements

- Python 3.10 or higher
- setuptools
- wheel

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jim-schilling/jpy-tools.git
cd jpy-tools
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Testing

Run tests using pytest:
```bash
python -m pytest tests/
```

### Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing with coverage

Run all quality checks:
```bash
black .
isort .
flake8 jpy_tools/ tests/ --max-line-length=88
mypy jpy_tools/
python -m pytest tests/ --cov=jpy_tools
```

### Build

Build distribution:
```bash
python -m build
```

## Changelog

### [0.1.11] - 2025-06-29

#### Added
- Added `String.is_time_like()` and `String.to_time()` for time value detection and conversion in `type_helper.py`
- `DataType.TIME` is now fully supported in type inference and profiling
- Added tests for time detection, conversion, and inference
- Enhanced `pyproject.toml` configuration following Python best practices
- Added comprehensive development dependencies (pytest, black, isort, flake8, mypy, pre-commit)
- Added project URLs for better discoverability
- Added keywords and improved classifiers for PyPI
- Added `py.typed` marker for type checking support
- Added tool configurations for Black, isort, mypy, pytest, and coverage
- Added optional dependency groups (dev, test, build)

#### Changed
- Updated development workflow to use modern Python packaging standards
- Improved test configuration with coverage reporting
- Enhanced code formatting and import organization

#### Fixed
- Code formatting issues across all modules
- Import sorting and organization

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Jim Schilling
