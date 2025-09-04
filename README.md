# splurge-tools

A comprehensive Python library providing robust tools for data processing, validation, and transformation with streaming support for large datasets.

## ✨ Key Features

- **🔄 Streaming Processing**: Handle datasets larger than available RAM with configurable chunk sizes
- **🎯 Type Inference**: Automatic detection and conversion of data types (dates, numbers, booleans, etc.)
- **📊 Data Models**: In-memory and streaming tabular data models with type safety
- **🔧 Data Validation**: Comprehensive validation framework with custom rules
- **📝 Text Processing**: Advanced text manipulation, tokenization, and case conversion
- **🎲 Random Generation**: Secure random data generation for testing
- **⚡ Performance**: Optimized algorithms for large-scale data processing
- **🛡️ Type Safety**: Full type annotations throughout the codebase

## 📦 Installation

```bash
pip install splurge-tools
```

## 🚀 Quick Start

### Process Large CSV Files

```python
from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel

# Stream process large files without loading into memory
stream = DsvHelper.parse_stream("large_dataset.csv", delimiter=",")
model = StreamingTabularDataModel(stream, header_rows=1, chunk_size=1000)

for row_dict in model.iter_rows():
    # Process each row efficiently
    print(row_dict["column_name"])
```

### Type-Safe Data Processing

```python
from splurge_tools.type_helper import String, DataType
from splurge_tools.tabular_data_model import TabularDataModel

# Automatic type inference
data_type = String.infer_type("2023-12-25")  # DataType.DATE
data_type = String.infer_type("123.45")      # DataType.FLOAT

# Safe type conversion
date_val = String.to_date("2023-12-25")
float_val = String.to_float("123.45", default=0.0)
```

## 📚 Documentation

- **[📖 Detailed Documentation](docs/README-details.md)** - Complete API reference, usage patterns, and best practices
- **[📋 Changelog](CHANGELOG.md)** - Version history and release notes
- **[🔧 Development](docs/README-details.md#contributing)** - Setup, testing, and contribution guidelines

## 🏗️ Architecture Overview

### Core Modules

| Module | Purpose |
|--------|---------|
| `type_helper` | Type inference, validation, and conversion |
| `dsv_helper` | Delimited value parsing and profiling |
| `tabular_data_model` | In-memory tabular data structures |
| `streaming_tabular_data_model` | Memory-efficient streaming data processing |
| `data_validator` | Data validation framework |
| `data_transformer` | Data transformation utilities |
| `text_*` modules | Text processing and manipulation |
| `decorators` | Common decorators for error handling |

### Design Principles

- **Composition over Inheritance**: Flexible component architecture
- **Protocol-Based Design**: Type-safe interfaces using Python protocols
- **Fail Fast**: Early validation with clear error messages
- **Memory Efficient**: Streaming support for large datasets
- **Type Safe**: Comprehensive type annotations and runtime validation

## 📖 More Examples

Explore comprehensive examples and use cases in the **[detailed documentation](docs/README-details.md#usage-patterns)** including:

- Complete ETL pipeline examples
- Advanced data validation patterns
- Performance optimization techniques
- Error handling best practices

## 🧪 Development & Testing

```bash
# Clone repository
git clone https://github.com/jim-schilling/splurge-tools.git
cd splurge-tools

# Setup development environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ --cov=splurge_tools

# Code quality checks
ruff check . --fix && ruff format .
mypy splurge_tools/
```

## 📈 Project Status

- **Version**: 2025.5.1 (CalVer)
- **Python**: 3.10+
- **License**: MIT
- **Status**: Active Development
- **Coverage**: 94%+
- **Documentation**: Comprehensive

## 🤝 Contributing

We welcome contributions! See our **[contributing guide](docs/README-details.md#contributing)** for:

- Development setup instructions
- Code standards and guidelines
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the **[LICENSE](LICENSE)** file for details.

## 👤 Author

**Jim Schilling** - [GitHub](https://github.com/jim-schilling)

---

⭐ **Star this repository** if you find splurge-tools useful!
