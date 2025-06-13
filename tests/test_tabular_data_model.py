"""Unit tests for DSVHelper class."""
import unittest
from jpy_tools.tabular_data_model import TabularDataModel

class TestTabularDataModel(unittest.TestCase):
    """Test cases for TabularDataModel class."""

    def setUp(self):
        """Set up test data."""
        self.sample_data = [
            ["Name", "Age", "City"],  # Header
            ["John", "30", "New York"],
            ["Jane", "25", "Boston"],
            ["Bob", "35", "Chicago"]
        ]

    def test_basic_initialization(self):
        """Test basic model initialization."""
        model = TabularDataModel(self.sample_data)
        self.assertEqual(model.column_names, ["Name", "Age", "City"])
        self.assertEqual(model.row_count, 3)
        self.assertEqual(model.column_count, 3)

    def test_column_index_map(self):
        """Test column index mapping."""
        model = TabularDataModel(self.sample_data)
        self.assertEqual(model.column_index_map, {"Name": 0, "Age": 1, "City": 2})
        self.assertEqual(model.column_index("Name"), 0)
        self.assertEqual(model.column_index("Age"), 1)
        self.assertEqual(model.column_index("City"), 2)

    def test_row_access(self):
        """Test row access methods."""
        model = TabularDataModel(self.sample_data)
        
        # Test row as dictionary
        row_dict = model.row(0)
        self.assertEqual(row_dict, {"Name": "John", "Age": "30", "City": "New York"})
        
        # Test row as list
        row_list = model.row_as_list(1)
        self.assertEqual(row_list, ["Jane", "25", "Boston"])
        
        # Test row as tuple
        row_tuple = model.row_as_tuple(2)
        self.assertEqual(row_tuple, ("Bob", "35", "Chicago"))

    def test_iteration(self):
        """Test model iteration."""
        model = TabularDataModel(self.sample_data)
        rows = list(model)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], ["John", "30", "New York"])

    def test_data_normalization(self):
        """Test data normalization with uneven rows."""
        data = [
            ["Name", "Age", "City"],
            ["John", "30"],
            ["Jane", "25", "Boston", "Extra"],
            ["Bob"]
        ]
        model = TabularDataModel(data)
        self.assertEqual(model.column_count, 4)
        self.assertEqual(model.row(0), {"Name": "John", "Age": "30", "City": "", "column_3": ""})
        self.assertEqual(model.row(1), {"Name": "Jane", "Age": "25", "City": "Boston", "column_3": "Extra"})
        self.assertEqual(model.row(2), {"Name": "Bob", "Age": "", "City": "", "column_3": ""})

    def test_skip_empty_rows(self):
        """Test skipping empty rows."""
        data = [
            ["Name", "Age", "City"],
            ["John", "30", "New York"],
            ["", "", ""],
            ["Jane", "25", "Boston"]
        ]
        model = TabularDataModel(data, skip_empty_rows=True)
        self.assertEqual(model.row_count, 2)
        
        model = TabularDataModel(data, skip_empty_rows=False)
        self.assertEqual(model.row_count, 3)

    def test_no_header(self):
        """Test model without header."""
        data = [
            ["John", "30", "New York"],
            ["Jane", "25", "Boston"]
        ]
        model = TabularDataModel(data, header_rows=0)
        self.assertEqual(model.column_names, ["column_0", "column_1", "column_2"])
        self.assertEqual(model.row_count, 2)
        self.assertEqual(model.row(0), {"column_0": "John", "column_1": "30", "column_2": "New York"})
        self.assertEqual(model.row(1), {"column_0": "Jane", "column_1": "25", "column_2": "Boston"})

    def test_invalid_initialization(self):
        """Test invalid initialization parameters."""
        with self.assertRaises(ValueError):
            TabularDataModel(None)
        
        with self.assertRaises(ValueError):
            TabularDataModel([])
        
        with self.assertRaises(ValueError):
            TabularDataModel(self.sample_data, header_rows=-1)  
        
        with self.assertRaises(ValueError):
            TabularDataModel(self.sample_data, header_rows=1, column_names_span=2)

if __name__ == '__main__':
    unittest.main()