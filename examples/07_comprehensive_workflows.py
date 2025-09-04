#!/usr/bin/env python3
"""
Comprehensive Workflow Examples

This example demonstrates end-to-end workflows that combine multiple features
of splurge-tools to solve real-world data processing challenges.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import tempfile
from datetime import date, timedelta
from pathlib import Path

from splurge_tools.case_helper import CaseHelper
from splurge_tools.data_transformer import DataTransformer
from splurge_tools.data_validator import DataValidator
from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.random_helper import RandomHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel
from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.text_normalizer import TextNormalizer

# from splurge_tools.factory import ComponentFactory, DataModelFactory


def create_messy_dataset():
    """Create a realistic messy dataset for processing."""
    temp_dir = Path(tempfile.mkdtemp())

    # Messy employee data with various issues
    messy_csv = """  Name  , Age,  "Department, Division", Salary  , Email, Start Date,Active
"  John DOE  ",30,"Engineering, Software",75000.50,john@company.com,2023-01-15,TRUE
jane_smith,25,"Marketing, Digital",65000,jane.smith@company.com,03/20/2023,Yes
"Bob Johnson, Jr.",45,"Sales, Enterprise",$85000,bob@company.com,11/10/2022,1
  Alice Brown  ,35,"Engineering, Data",72000.25,alice@company.com,2023-05-05,true
CHARLIE WILSON,28,"Marketing, Content",68000,charlie.wilson@company.com,2023-02-14,Y
"",30,"HR, Operations",55000,missing@company.com,2023-03-01,false
David Jones,17,"Engineering, Intern",35000,david@company.com,2023-06-01,true
Sarah Davis,45,"Finance, Accounting",invalid_salary,sarah@company.com,2023-01-20,true
Mike Wilson,35,"Sales, Regional",95000,mike@invalid-domain.com,2022-12-15,true
Lisa Garcia,29,"Engineering, Frontend",78000,lisa@company.com,2023-04-10,active"""

    # Large dataset for streaming
    large_csv_header = "ID,Product,Category,Price,Quantity,Date,Customer_ID\n"
    large_csv_content = large_csv_header

    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    products = ["Widget", "Gadget", "Tool", "Device", "Item"]

    for i in range(5000):
        product = f"{products[i % len(products)]}_{i}"
        category = categories[i % len(categories)]
        price = round(RandomHelper.as_float_range(10.0, 500.0), 2)
        quantity = RandomHelper.as_int_range(1, 10)
        days_ago = RandomHelper.as_int_range(0, 365)
        order_date = date.today() - timedelta(days=days_ago)
        customer_id = RandomHelper.as_int_range(1000, 9999)

        large_csv_content += f"{i},{product},{category},{price},{quantity},{order_date},{customer_id}\n"

    # Write files
    files = {}
    files["messy"] = temp_dir / "messy_employees.csv"
    files["large"] = temp_dir / "large_orders.csv"

    files["messy"].write_text(messy_csv)
    files["large"].write_text(large_csv_content)

    return temp_dir, files


def workflow_1_data_cleaning_and_validation(files):
    """Comprehensive data cleaning and validation workflow."""

    raw_data = DsvHelper.parse_file(files["messy"], delimiter=",", bookend='"')

    cleaned_data = [raw_data[0]]  # Keep header

    for row in raw_data[1:]:
        cleaned_row = []
        for i, cell in enumerate(row):
            # Apply comprehensive text cleaning
            clean_cell = TextNormalizer.normalize_whitespace(cell)
            clean_cell = TextNormalizer.normalize_spaces(clean_cell)
            clean_cell = TextNormalizer.remove_control_chars(clean_cell)

            # Special handling for specific columns
            if i == 0:  # Name column
                clean_cell = CaseHelper.to_sentence(clean_cell.replace("_", " "))
            elif i == 2:  # Department column
                clean_cell = clean_cell.replace('"', "")  # Remove embedded quotes
            elif i == 3:  # Salary column
                clean_cell = clean_cell.replace("$", "").replace(",", "")
            elif i == 4:  # Email column
                clean_cell = clean_cell.lower()

            cleaned_row.append(clean_cell)

        cleaned_data.append(cleaned_row)

    model = TabularDataModel(cleaned_data, header_rows=1)

    type_info = {}
    for col_name in model.column_names:
        # col_values = model.column_values(col_name)  # Unused variable
        col_type = model.column_type(col_name)
        type_info[col_name] = col_type

    validator = DataValidator()

    # Add business validation rules
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Age", lambda x: x.isdigit() and 18 <= int(x) <= 65)
    validator.add_validator("Email", lambda x: "@company.com" in x and "." in x)
    validator.add_validator("Salary", lambda x: x.replace(".", "").isdigit() and float(x) >= 30000)
    validator.add_validator(
        "Active", lambda x: x.lower() in ["true", "false", "yes", "no", "1", "0", "y", "n", "active"],
    )

    valid_rows = []
    invalid_rows = []

    for i in range(model.row_count):
        row_dict = model.row(i)
        if validator.validate(row_dict):
            valid_rows.append((i, row_dict))
        else:
            invalid_rows.append((i, row_dict, validator.get_errors().copy()))
        validator.clear_errors()

    # Show invalid records
    if invalid_rows:
        for i, record, _errors in invalid_rows[:3]:  # Show first 3
            pass

    if valid_rows:
        clean_headers = model.column_names
        clean_data_final = [clean_headers]

        for _, record in valid_rows:
            clean_row = [record[col] for col in clean_headers]
            clean_data_final.append(clean_row)

        clean_model = TabularDataModel(clean_data_final, header_rows=1)

        # Show sample of clean data
        for i in range(min(3, clean_model.row_count)):
            pass

    return clean_model if valid_rows else None


def workflow_2_streaming_data_analysis(files):
    """Large dataset streaming analysis workflow."""

    # Create streaming model
    stream = DsvHelper.parse_stream(files["large"], delimiter=",", chunk_size=1000)
    streaming_model = StreamingTabularDataModel(stream, header_rows=1, chunk_size=2000)

    # Initialize counters
    total_records = 0
    category_counts = {}
    total_revenue = 0.0
    price_sum = 0.0
    quantity_sum = 0
    customer_ids = set()

    # Process data in streaming fashion
    chunk_count = 0
    for row in streaming_model:
        total_records += 1

        try:
            # Extract values (assuming row is a list)
            if len(row) >= 7:
                # product = row[1]  # Unused variable
                category = row[2]
                price = float(row[3])
                quantity = int(row[4])
                customer_id = row[6]

                # Update statistics
                category_counts[category] = category_counts.get(category, 0) + 1
                revenue = price * quantity
                total_revenue += revenue
                price_sum += price
                quantity_sum += quantity
                customer_ids.add(customer_id)

        except (ValueError, IndexError):
            # Skip malformed rows
            continue

        # Report progress
        if total_records % 1000 == 0:
            chunk_count += 1

            if chunk_count >= 5:  # Limit for demonstration
                break

    if total_records > 0:
        price_sum / total_records
        quantity_sum / total_records
        total_revenue / total_records

        for category, count in sorted(category_counts.items()):
            (count / total_records) * 100


def workflow_3_data_transformation_pipeline():
    """Data transformation and reshaping workflow."""

    # Create sample sales data
    sales_data = [
        ["Date", "Salesperson", "Product", "Region", "Units", "Revenue"],
        ["2023-01-01", "Alice", "Widget A", "North", "100", "10000"],
        ["2023-01-01", "Bob", "Widget A", "South", "80", "8000"],
        ["2023-01-01", "Alice", "Gadget B", "North", "50", "7500"],
        ["2023-01-02", "Bob", "Widget A", "South", "90", "9000"],
        ["2023-01-02", "Charlie", "Gadget B", "East", "60", "9000"],
        ["2023-01-02", "Alice", "Tool C", "North", "40", "6000"],
        ["2023-01-03", "Bob", "Widget A", "South", "85", "8500"],
        ["2023-01-03", "Charlie", "Gadget B", "East", "55", "8250"],
    ]

    model = TabularDataModel(sales_data, header_rows=1)

    # Show sample data
    for i in range(min(3, model.row_count)):
        pass

    transformer = DataTransformer(model)

    # Pivot by salesperson and product
    try:
        pivoted = transformer.pivot(
            index_cols=["Salesperson"],
            columns_col="Product",
            values_col="Revenue",
            agg_func=lambda values: str(sum(float(v) for v in values)),
        )

        for i in range(pivoted.row_count):
            pass
    except Exception:
        pass

    # Group by region
    try:
        grouped = transformer.group_by(
            group_cols=["Region"],
            agg_dict={
                "Units": lambda values: str(sum(int(v) for v in values)),
                "Revenue": lambda values: str(sum(float(v) for v in values)),
            },
        )

        for i in range(grouped.row_count):
            pass
    except Exception:
        pass

    try:
        # Add calculated column (profit margin)
        def calculate_profit_margin(revenue_str):
            try:
                revenue = float(revenue_str)
                # Assume 30% profit margin
                return str(round(revenue * 0.30, 2))
            except (ValueError, TypeError):
                return "0"

        transformed = transformer.transform_column(
            column="Revenue",
            transform_func=calculate_profit_margin,
        )

        for i in range(min(3, transformed.row_count)):
            transformed.row(i)
    except Exception:
        pass


def workflow_4_comprehensive_etl_pipeline(files):
    """Complete ETL (Extract, Transform, Load) pipeline."""

    # Extract from messy CSV
    employee_data = DsvHelper.parse_file(files["messy"], delimiter=",", bookend='"')

    # Generate additional data source (simulated API data)
    dept_data = [
        ["Department", "Manager", "Budget", "Location"],
        ["Engineering", "Tech Lead", "500000", "Building A"],
        ["Marketing", "Marketing Dir", "200000", "Building B"],
        ["Sales", "Sales VP", "300000", "Building C"],
        ["HR", "HR Manager", "150000", "Building B"],
        ["Finance", "CFO", "250000", "Building A"],
    ]

    # Clean employee data
    cleaned_employee_data = []
    for i, row in enumerate(employee_data):
        if i == 0:  # Header
            cleaned_employee_data.append(
                [
                    "Name",
                    "Age",
                    "Department",
                    "Salary",
                    "Email",
                    "Start_Date",
                    "Active",
                ],
            )
            continue

        cleaned_row = []
        for j, cell in enumerate(row):
            clean_cell = TextNormalizer.normalize_whitespace(cell)
            clean_cell = TextNormalizer.normalize_spaces(clean_cell)

            if j == 0:  # Name
                clean_cell = CaseHelper.to_sentence(clean_cell.replace("_", " "))
            elif j == 2:  # Department
                # Extract main department (before comma)
                clean_cell = clean_cell.split(",")[0].strip().replace('"', "")
            elif j == 3:  # Salary
                clean_cell = clean_cell.replace("$", "").replace(",", "")
            elif j == 4:  # Email
                clean_cell = clean_cell.lower()
            elif j == 6:  # Active
                # Normalize boolean values
                clean_cell = clean_cell.lower()
                clean_cell = "true" if clean_cell in ["true", "yes", "1", "y", "active"] else "false"

            cleaned_row.append(clean_cell)

        cleaned_employee_data.append(cleaned_row)

    # Create models
    employee_model = TabularDataModel(cleaned_employee_data, header_rows=1)
    dept_model = TabularDataModel(dept_data, header_rows=1)

    # Validate employee data
    validator = DataValidator()
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Age", lambda x: x.isdigit() and 18 <= int(x) <= 65)
    validator.add_validator("Email", lambda x: "@" in x)
    validator.add_validator("Salary", lambda x: x.replace(".", "").isdigit())

    valid_employees = []
    for i in range(employee_model.row_count):
        row_dict = employee_model.row(i)
        if validator.validate(row_dict):
            valid_employees.append(row_dict)
        validator.clear_errors()

    # Enrich employee data with department information
    dept_lookup = {}
    for i in range(dept_model.row_count):
        dept_dict = dept_model.row(i)
        dept_lookup[dept_dict["Department"]] = dept_dict

    enriched_employees = []
    for emp in valid_employees:
        enriched_emp = emp.copy()
        dept_info = dept_lookup.get(emp["Department"], {})

        enriched_emp["Manager"] = dept_info.get("Manager", "Unknown")
        enriched_emp["Budget"] = dept_info.get("Budget", "0")
        enriched_emp["Location"] = dept_info.get("Location", "Unknown")

        enriched_employees.append(enriched_emp)

    # Calculate department statistics
    dept_stats = {}
    for emp in enriched_employees:
        dept = emp["Department"]
        if dept not in dept_stats:
            dept_stats[dept] = {
                "count": 0,
                "total_salary": 0,
                "active_count": 0,
                "employees": [],
            }

        dept_stats[dept]["count"] += 1
        dept_stats[dept]["total_salary"] += float(emp["Salary"])
        if emp["Active"] == "true":
            dept_stats[dept]["active_count"] += 1
        dept_stats[dept]["employees"].append(emp["Name"])

    for dept, stats in dept_stats.items():
        stats["total_salary"] / stats["count"]
        (stats["active_count"] / stats["count"]) * 100

    # Create final enriched dataset
    final_headers = [
        "Name",
        "Age",
        "Department",
        "Salary",
        "Email",
        "Start_Date",
        "Active",
        "Manager",
        "Budget",
        "Location",
    ]

    final_data = [final_headers]
    for emp in enriched_employees:
        final_row = [emp[col] for col in final_headers]
        final_data.append(final_row)

    final_model = TabularDataModel(final_data, header_rows=1)

    for i in range(min(3, final_model.row_count)):
        pass

    return final_model


def workflow_5_real_time_data_processing():
    """Simulate real-time data processing workflow."""

    # Simulate real-time data generation
    def generate_real_time_record():
        """Generate a simulated real-time record."""
        return {
            "timestamp": date.today().isoformat(),
            "user_id": RandomHelper.as_int_range(1000, 9999),
            "action": ["login", "logout", "purchase", "view", "search"][RandomHelper.as_int_range(0, 4)],
            "value": round(RandomHelper.as_float_range(0.0, 1000.0), 2),
            "session_id": RandomHelper.as_base58_like(16, symbols=""),
            "success": RandomHelper.as_bool(),
        }

    # Generate batch of records
    incoming_records = [generate_real_time_record() for _ in range(100)]

    # Set up real-time validator
    validator = DataValidator()
    validator.add_validator("user_id", lambda x: 1000 <= int(x) <= 9999)
    validator.add_validator("action", lambda x: x in ["login", "logout", "purchase", "view", "search"])
    validator.add_validator("value", lambda x: 0.0 <= float(x) <= 1000.0)

    valid_records = []
    invalid_count = 0

    for record in incoming_records:
        if validator.validate(record):
            valid_records.append(record)
        else:
            invalid_count += 1
        validator.clear_errors()

    # Calculate real-time metrics
    action_counts = {}
    total_value = 0.0
    success_count = 0
    unique_users = set()
    unique_sessions = set()

    for record in valid_records:
        action = record["action"]
        action_counts[action] = action_counts.get(action, 0) + 1
        total_value += record["value"]
        if record["success"]:
            success_count += 1
        unique_users.add(record["user_id"])
        unique_sessions.add(record["session_id"])

    for action, count in sorted(action_counts.items()):
        (count / len(valid_records)) * 100

    # Implement basic alerting logic
    alerts = []

    # High-value transaction alert
    high_value_threshold = 800.0
    high_value_records = [r for r in valid_records if r["value"] > high_value_threshold]
    if high_value_records:
        alerts.append(f"High-value transactions: {len(high_value_records)} transactions > ${high_value_threshold}")

    # Low success rate alert
    success_rate = (success_count / len(valid_records)) * 100
    if success_rate < 70:
        alerts.append(f"Low success rate: {success_rate:.1f}% (threshold: 70%)")

    # High error rate alert
    error_rate = (invalid_count / len(incoming_records)) * 100
    if error_rate > 10:
        alerts.append(f"High error rate: {error_rate:.1f}% (threshold: 10%)")

    if alerts:
        for _alert in alerts:
            pass
    else:
        pass


def cleanup_temp_files(temp_dir):
    """Clean up temporary files."""
    import shutil

    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    """Run all comprehensive workflow examples."""

    # Create sample datasets
    temp_dir, files = create_messy_dataset()

    try:
        # Run all workflows
        clean_model = workflow_1_data_cleaning_and_validation(files)
        workflow_2_streaming_data_analysis(files)
        workflow_3_data_transformation_pipeline()
        final_model = workflow_4_comprehensive_etl_pipeline(files)
        workflow_5_real_time_data_processing()

    finally:
        cleanup_temp_files(temp_dir)
