# jpy-tools

A Python package providing tools for data type handling, validation, and text processing.

## Description

jpy-tools is a collection of Python utilities focused on:
- Data type handling and validation
- Text file processing and manipulation
- String tokenization and parsing
- Text case transformations
- Delimited separated value parsing
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

## Development

### Requirements

- Python 3.10 or higher
- setuptools
- wheel

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jpy-tools.git
cd jpy-tools
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e .
```

### Testing

Run tests using pytest:
```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Jim Schilling
