#!/usr/bin/env python3
"""
Test script for Excel file conversion functionality.
"""

import os
import sys
import logging
import tempfile
import shutil
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the parsing functions from the convertor module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convertor.core import parse_xlsx_file

# Create a temporary directory for test files
test_dir = tempfile.mkdtemp()
logger.info(f"Created temporary test directory: {test_dir}")

def cleanup():
    """Clean up temporary test files."""
    try:
        shutil.rmtree(test_dir)
        logger.info(f"Removed temporary test directory: {test_dir}")
    except Exception as e:
        logger.error(f"Error cleaning up test directory: {e}")

def create_test_excel_files():
    """Create test Excel files."""
    # Single sheet Excel file
    df1 = pd.DataFrame({
        'Name': ['Test User', 'Another User', 'Third User'],
        'Age': [30, 25, 40],
        'Email': ['test@example.com', 'another@example.com', 'third@example.com']
    })
    df1.to_excel(os.path.join(test_dir, "single_sheet.xlsx"), index=False)
    
    # Multi-sheet Excel file
    with pd.ExcelWriter(os.path.join(test_dir, "multi_sheet.xlsx")) as writer:
        df1.to_excel(writer, sheet_name='Users', index=False)
        
        df2 = pd.DataFrame({
            'Product': ['Product A', 'Product B', 'Product C'],
            'Price': [10.99, 20.50, 5.99],
            'Stock': [100, 50, 200]
        })
        df2.to_excel(writer, sheet_name='Products', index=False)
        
        df3 = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=5),
            'Value': [100, 120, 90, 110, 130]
        })
        df3.to_excel(writer, sheet_name='TimeSeries', index=False)
    
    # Empty Excel file
    pd.DataFrame().to_excel(os.path.join(test_dir, "empty.xlsx"), index=False)
    
    logger.info("Created test Excel files")

def test_single_sheet_excel():
    """Test parsing a single sheet Excel file."""
    try:
        file_path = os.path.join(test_dir, "single_sheet.xlsx")
        content = parse_xlsx_file(file_path)
        logger.info(f"Successfully parsed single sheet Excel file. Content length: {len(content)}")
        assert "Test User" in content, "Excel content not found"
        assert "Another User" in content, "Excel content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing single sheet Excel file: {e}")
        return False

def test_multi_sheet_excel():
    """Test parsing a multi-sheet Excel file."""
    try:
        file_path = os.path.join(test_dir, "multi_sheet.xlsx")
        content = parse_xlsx_file(file_path)
        logger.info(f"Successfully parsed multi-sheet Excel file. Content length: {len(content)}")
        assert "Users" in content, "Sheet name not found"
        assert "Products" in content, "Sheet name not found"
        assert "TimeSeries" in content, "Sheet name not found"
        assert "Test User" in content, "Excel content not found"
        assert "Product A" in content, "Excel content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing multi-sheet Excel file: {e}")
        return False

def test_empty_excel():
    """Test parsing an empty Excel file."""
    try:
        file_path = os.path.join(test_dir, "empty.xlsx")
        content = parse_xlsx_file(file_path)
        logger.info(f"Successfully parsed empty Excel file. Content: {content}")
        assert "Empty Excel file" in content, "Empty file message not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing empty Excel file: {e}")
        return False

def run_tests():
    """Run all tests."""
    tests = [
        ("Single Sheet Excel", test_single_sheet_excel),
        ("Multi-Sheet Excel", test_multi_sheet_excel),
        ("Empty Excel", test_empty_excel),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"Running test: {test_name}")
        success = test_func()
        results.append((test_name, success))
        logger.info(f"Test {test_name}: {'PASSED' if success else 'FAILED'}")
    
    # Print summary
    print("\n=== Test Results ===")
    passed = 0
    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    return passed == len(results)

if __name__ == "__main__":
    try:
        create_test_excel_files()
        success = run_tests()
        sys.exit(0 if success else 1)
    finally:
        cleanup()
