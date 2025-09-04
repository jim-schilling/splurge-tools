# Test Directory Structure

This directory contains the test suite for splurge-tools, organized according to testing best practices.

## Directory Structure

```
tests/
├── README.md                    # This file
├── unit/                       # Unit tests
├── integration/               # Integration tests
├── e2e/                       # End-to-end tests
└── __pycache__/               # Python cache files
```

## Test Categories

### Unit Tests (`unit/`)
Tests that verify individual components in isolation. These tests:
- Focus on single functions, classes, or modules
- Use mocks/stubs for external dependencies
- Run quickly and provide fast feedback
- Help identify regressions in core functionality

**Files**: 15 test files covering core utilities, type inference, data validation, etc.

### Integration Tests (`integration/`)
Tests that verify component interactions and data flow. These tests:
- Test multiple components working together
- Include file I/O and external dependencies
- Validate data processing pipelines
- Ensure API contracts between modules

**Files**: 6 test files covering data models, streaming, file operations, etc.

### End-to-End Tests (`e2e/`)
Tests that verify complete workflows from start to finish. These tests:
- Test complete user scenarios
- Include complex data processing workflows
- Validate system behavior under various conditions
- May be slower and more resource-intensive

**Files**: 2 test files covering complex streaming scenarios and typed data models.

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/

# Run tests with specific markers
pytest -m unit
pytest -m integration
pytest -m e2e
```

### Run with Coverage
```bash
pytest --cov=splurge_tools --cov-report=html
```

### Run Specific Test Files
```bash
pytest tests/unit/test_type_helper.py
pytest tests/integration/test_dsv_helper.py
```

## Test Organization Guidelines

### Naming Conventions
- Files: `test_<module_name>.py`
- Classes: `Test<FeatureName>`
- Methods: `test_<descriptive_name>`

### Test Structure
```python
import pytest
from splurge_tools.module import ClassName

class TestClassName:
    """Test cases for ClassName functionality."""

    def test_feature_works_correctly(self):
        """Test that feature works as expected."""
        # Arrange
        obj = ClassName()

        # Act
        result = obj.method()

        # Assert
        assert result == expected_value

    def test_edge_case_handling(self):
        """Test edge case scenarios."""
        # Test error conditions, boundary values, etc.
        pass
```

### Markers
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow-running tests

## Coverage Requirements

- **Overall Coverage**: ≥85%
- **Core Modules**: ≥95%
- **New Features**: 100% coverage required
- **Critical Paths**: 100% coverage required

## Best Practices

### Unit Tests
- Test one thing at a time
- Use descriptive test names
- Avoid external dependencies
- Mock external services
- Test both success and failure paths

### Integration Tests
- Test realistic scenarios
- Include necessary setup/teardown
- Validate data flow between components
- Test error propagation
- Use temporary files/databases when needed

### E2E Tests
- Test complete user workflows
- Include realistic data sets
- Validate end-to-end data integrity
- Test performance under load (when applicable)
- Clean up resources properly

## CI/CD Integration

Tests are automatically run in CI/CD pipelines with:
- Unit tests run on every commit
- Integration tests run on pull requests
- E2E tests run on releases
- Coverage reports generated and tracked

## Debugging Tests

### Run with Debug Output
```bash
pytest -v -s tests/unit/test_specific.py
```

### Run Failed Tests Only
```bash
pytest --lf
```

### Run with PDB on Failure
```bash
pytest --pdb
```

## Contributing

When adding new tests:
1. Place in appropriate category directory
2. Follow naming conventions
3. Include docstrings
4. Add appropriate markers
5. Ensure adequate coverage
6. Test both success and failure scenarios

## Performance Testing

For performance-critical components:
- Use `pytest-benchmark` for micro-benchmarks
- Include performance assertions in tests
- Track performance regressions
- Document performance expectations
