# Splurge-Tools Examples

This directory contains comprehensive examples demonstrating the major features and capabilities of the splurge-tools library. Each example is self-contained and includes detailed explanations, sample data, and best practices.

## 📁 Example Files

### Core Features

1. **[01_type_inference_and_validation.py](01_type_inference_and_validation.py)**
   - Automatic type inference for strings, numbers, dates, times, booleans
   - Type validation methods (`is_*_like`)
   - Safe type conversion with defaults
   - Collection type profiling
   - Performance considerations for large datasets

2. **[02_dsv_parsing_and_profiling.py](02_dsv_parsing_and_profiling.py)**
   - DSV (Delimited Separated Values) parsing
   - File and stream processing
   - Bookend handling for quoted fields
   - Data profiling and column analysis
   - Error handling and malformed data

3. **[03_tabular_data_models.py](03_tabular_data_models.py)**
   - In-memory TabularDataModel for full data access
   - StreamingTabularDataModel for large datasets
   - TabularDataModel.to_typed() for typed access with schema validation
   - Multi-row header processing
   - Different iteration methods (list, dict, tuple)

4. **[04_text_processing.py](04_text_processing.py)**
   - Text normalization and cleaning
   - Case conversion (snake, camel, pascal, kebab, train)
   - String tokenization with delimiter support
   - File processing with streaming capabilities
   - Comprehensive text processing workflows

5. **[05_validation_and_transformation.py](05_validation_and_transformation.py)**
   - Custom data validation rules
   - Data transformation operations (pivot, melt, group-by)
   - Factory pattern for component creation
   - Validation utilities and error handling
   - Business rule validation

6. **[06_random_data_generation.py](06_random_data_generation.py)**
   - Secure and non-secure random value generation
   - Base58-like strings with guaranteed character diversity
   - API key and session token generation
   - Test data generation for development
   - Performance and security considerations

### Advanced Workflows

7. **[07_comprehensive_workflows.py](07_comprehensive_workflows.py)**
   - End-to-end data processing pipelines
   - ETL (Extract, Transform, Load) workflows
   - Real-time data processing simulation
   - Data cleaning and validation workflows
   - Streaming analytics for large datasets

## 🚀 Quick Start

### Running Individual Examples

Each example can be run independently:

```bash
# Run a specific example
python examples/01_type_inference_and_validation.py

# Run with Python module syntax
python -m examples.02_dsv_parsing_and_profiling

# Run all examples
python examples/run_all_examples.py
```

### Prerequisites

Make sure you have splurge-tools installed:

```bash
pip install splurge-tools
```

Or if you're working with the development version:

```bash
pip install -e .
```

## 📊 Example Categories

### Data Processing
- **Type Inference**: Automatic detection of data types in text
- **DSV Parsing**: Reading and processing delimited files
- **Data Models**: Structured access to tabular data
- **Streaming**: Memory-efficient processing of large datasets

### Text Processing
- **Normalization**: Cleaning and standardizing text
- **Case Conversion**: Converting between different naming conventions
- **Tokenization**: Parsing delimited and structured text
- **File Operations**: Reading and writing text files

### Data Quality
- **Validation**: Custom rules and business logic validation
- **Transformation**: Reshaping and aggregating data
- **Error Handling**: Robust error detection and recovery
- **Type Safety**: Schema validation and type enforcement

### Utilities
- **Random Generation**: Secure random data for testing and keys
- **Factory Patterns**: Consistent component creation
- **Protocol Compliance**: Type-safe interfaces
- **Performance**: Optimized operations for large datasets

## 💡 Key Features Demonstrated

### Memory Efficiency
- Streaming models for datasets larger than RAM
- Configurable chunk sizes for optimal performance
- Generator-based iteration for minimal memory usage

### Type Safety
- Comprehensive type inference and validation
- Protocol-based architecture for consistent interfaces
- Runtime validation with meaningful error messages

### Text Processing
- Unicode-aware text normalization
- Multiple case conversion patterns
- Robust parsing with error recovery

### Data Quality
- Custom validation rules with business logic
- Data profiling and quality assessment
- Error tracking and reporting

### Performance
- Optimized algorithms for large datasets
- Incremental processing for better responsiveness
- Parallel processing capabilities where applicable

## 🔧 Best Practices Shown

### Error Handling
- Comprehensive exception handling at all levels
- Graceful degradation for malformed data
- Detailed error messages for debugging

### Code Organization
- Factory pattern for consistent component creation
- Protocol-based interfaces for type safety
- Modular design for reusability

### Data Processing
- Validation before transformation
- Streaming for memory efficiency
- Type inference for automatic schema detection

### Testing
- Random data generation for comprehensive testing
- Edge case handling and validation
- Performance testing with large datasets

## 📈 Performance Considerations

The examples demonstrate various performance optimizations:

- **Streaming Processing**: Handle files larger than available RAM
- **Incremental Type Checking**: Optimize type inference for large datasets
- **Chunk-based Processing**: Balance memory usage and performance
- **Generator Patterns**: Minimize memory allocation

## 🛡️ Security Features

Security-conscious features are demonstrated throughout:

- **Secure Random Generation**: Cryptographically secure random values
- **Input Validation**: Comprehensive validation before processing
- **Base58 Encoding**: Secure string generation for keys and tokens
- **Error Boundaries**: Prevent data leakage through error messages

## 🤝 Contributing

When adding new examples:

1. Follow the existing naming convention (`##_feature_name.py`)
2. Include comprehensive docstrings and comments
3. Demonstrate both basic and advanced usage
4. Include error handling examples
5. Add cleanup for any temporary files
6. Update this README with new example descriptions

## 📝 Notes

- All examples create temporary files that are automatically cleaned up
- Examples are designed to be educational and self-contained
- Error scenarios are included to demonstrate proper error handling
- Performance examples use realistic dataset sizes while remaining runnable

## 📚 Further Reading

- [Main README](../README.md) - Library overview and installation
- [API Documentation](../splurge_tools/) - Detailed module documentation
- [Test Suite](../tests/) - Comprehensive test examples
- [Changelog](../README.md#changelog) - Version history and updates
