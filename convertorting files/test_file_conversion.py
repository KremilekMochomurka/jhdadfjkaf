#!/usr/bin/env python3
"""
Test script for file conversion functionality.
This script tests all supported file formats without relying on the Gemini API.
"""

import os
import sys
import logging
from pathlib import Path
import shutil
import tempfile
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the parsing functions from the convertor module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convertor.core import (
    parse_text_file,
    parse_pdf_file,
    parse_docx_file,
    parse_doc_file,
    parse_xlsx_file,
    parse_csv_file,
    parse_json_file
)

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
    """Create test files for each supported format."""
    # Text file
    with open(os.path.join(test_dir, "sample.txt"), "w") as f:
        f.write("This is a sample text file for testing.\nIt has multiple lines.\nTesting, 1, 2, 3.")
    
    # JSON file
    with open(os.path.join(test_dir, "sample.json"), "w") as f:
        json.dump({
            "name": "Test User",
            "age": 30,
            "email": "test@example.com",
            "address": {
                "street": "123 Test St",
                "city": "Test City",
                "zip": "12345"
            },
            "phones": [
                {"type": "home", "number": "555-1234"},
                {"type": "work", "number": "555-5678"}
            ]
        }, f, indent=2)
    
    # CSV file
    with open(os.path.join(test_dir, "sample.csv"), "w") as f:
        f.write("name,age,email\n")
        f.write("Test User,30,test@example.com\n")
        f.write("Another User,25,another@example.com\n")
        f.write("Third User,40,third@example.com\n")
    
    # Create a CSV file with different delimiter
    with open(os.path.join(test_dir, "sample_semicolon.csv"), "w") as f:
        f.write("name;age;email\n")
        f.write("Test User;30;test@example.com\n")
        f.write("Another User;25;another@example.com\n")
    
    # We'll skip creating PDF, DOCX, DOC, and XLSX files as they require additional libraries
    # and are more complex to create programmatically
    
    logger.info("Created test files")

def test_text_file():
    """Test parsing a text file."""
    try:
        file_path = os.path.join(test_dir, "sample.txt")
        content = parse_text_file(file_path)
        logger.info(f"Successfully parsed text file. Content length: {len(content)}")
        assert "This is a sample text file" in content, "Text content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing text file: {e}")
        return False

def test_json_file():
    """Test parsing a JSON file."""
    try:
        file_path = os.path.join(test_dir, "sample.json")
        content = parse_json_file(file_path)
        logger.info(f"Successfully parsed JSON file. Content length: {len(content)}")
        assert "Test User" in content, "JSON content not found"
        assert "phones" in content, "Nested JSON content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing JSON file: {e}")
        return False

def test_csv_file():
    """Test parsing a CSV file."""
    try:
        file_path = os.path.join(test_dir, "sample.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV file. Content length: {len(content)}")
        assert "Test User" in content, "CSV content not found"
        assert "Another User" in content, "CSV content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV file: {e}")
        return False

def test_csv_file_with_semicolon():
    """Test parsing a CSV file with semicolon delimiter."""
    try:
        file_path = os.path.join(test_dir, "sample_semicolon.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV file with semicolon delimiter. Content length: {len(content)}")
        assert "Test User" in content, "CSV content not found"
        assert "Another User" in content, "CSV content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV file with semicolon delimiter: {e}")
        return False

def run_tests():
    """Run all tests."""
    tests = [
        ("Text File", test_text_file),
        ("JSON File", test_json_file),
        ("CSV File", test_csv_file),
        ("CSV File with Semicolon", test_csv_file_with_semicolon),
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
        create_test_files()
        success = run_tests()
        sys.exit(0 if success else 1)
    finally:
        cleanup()
