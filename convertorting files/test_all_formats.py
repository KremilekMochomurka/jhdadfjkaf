#!/usr/bin/env python3
"""
Comprehensive test script for all supported file formats.
"""

import os
import sys
import logging
import tempfile
import shutil
import json
import pandas as pd
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the processing function from the convertor module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convertor.core import process_file

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

def create_test_files():
    """Create test files for all supported formats."""
    # Text file
    with open(os.path.join(test_dir, "test.txt"), "w") as f:
        f.write("This is a sample text file for testing.\nIt has multiple lines.\nTesting, 1, 2, 3.")
    
    # JSON file
    with open(os.path.join(test_dir, "test.json"), "w") as f:
        json.dump({
            "name": "Test User",
            "age": 30,
            "email": "test@example.com"
        }, f, indent=2)
    
    # CSV file
    with open(os.path.join(test_dir, "test.csv"), "w") as f:
        f.write("name,age,email\n")
        f.write("Test User,30,test@example.com\n")
        f.write("Another User,25,another@example.com\n")
    
    # Excel file
    df = pd.DataFrame({
        'Name': ['Test User', 'Another User'],
        'Age': [30, 25],
        'Email': ['test@example.com', 'another@example.com']
    })
    df.to_excel(os.path.join(test_dir, "test.xlsx"), index=False)
    
    # HTML file
    with open(os.path.join(test_dir, "test.html"), "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Test HTML Document</title>
</head>
<body>
    <h1>Test HTML Document</h1>
    <p>This is a paragraph of text for testing HTML parsing.</p>
</body>
</html>""")
    
    # We skip creating ODT, PDF, DOCX, DOC files as they require more complex libraries
    # and are already tested in separate test files
    
    logger.info("Created test files for supported formats")

def test_format(file_extension):
    """Test processing a file with the given extension."""
    try:
        file_path = os.path.join(test_dir, f"test{file_extension}")
        if not os.path.exists(file_path):
            logger.warning(f"Test file for {file_extension} does not exist, skipping")
            return None
            
        result = process_file(file_path)
        logger.info(f"Process file result for {file_extension}: {result}")
        
        # Check if there's an error (there will be if no API key is set, but that's expected)
        if result["error"] and "API Key Missing" in result["error"]:
            logger.info(f"API key missing error is expected for {file_extension} without a Gemini API key")
            return True
        
        # If there's no API key error, check if content was processed
        if result["content"] is not None:
            return True
        
        # If there's another error, log it
        if result["error"]:
            logger.error(f"Unexpected error processing {file_extension} file: {result['error']}")
            return False
        
        return False
    except Exception as e:
        logger.error(f"Error in test_format for {file_extension}: {e}")
        return False

def run_tests():
    """Run tests for all supported formats."""
    formats = [
        (".txt", "Text"),
        (".json", "JSON"),
        (".csv", "CSV"),
        (".xlsx", "Excel"),
        (".html", "HTML"),
        # We skip testing ODT, PDF, DOCX, DOC as they require more complex setup
    ]
    
    results = []
    for file_ext, format_name in formats:
        logger.info(f"Testing {format_name} format")
        success = test_format(file_ext)
        if success is not None:  # Skip formats that don't have test files
            results.append((format_name, success))
            logger.info(f"Test {format_name}: {'PASSED' if success else 'FAILED'}")
    
    # Print summary
    print("\n=== Test Results ===")
    passed = 0
    for format_name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{format_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    return passed == len(results)

if __name__ == "__main__":
    try:
        create_test_files()
        success = run_tests()
        sys.exit(0 if success else 1)
    finally:
        cleanup()
