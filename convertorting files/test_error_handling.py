#!/usr/bin/env python3
"""
Test script for error handling in file conversion.
"""

import os
import sys
import logging
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the parsing functions from the convertor module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convertor.core import (
    parse_text_file,
    parse_json_file,
    parse_csv_file,
    parse_xlsx_file,
    process_file
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

def create_invalid_files():
    """Create invalid test files."""
    # Invalid JSON file
    with open(os.path.join(test_dir, "invalid.json"), "w") as f:
        f.write('{"name": "Test User", "age": 30, "email": "test@example.com"')  # Missing closing brace
    
    # Invalid CSV file (inconsistent columns)
    with open(os.path.join(test_dir, "invalid.csv"), "w") as f:
        f.write("name,age,email\n")
        f.write("Test User,30\n")  # Missing email column
        f.write("Another User,25,another@example.com,extra\n")  # Extra column
    
    # Empty file
    with open(os.path.join(test_dir, "empty.txt"), "w") as f:
        f.write("")
    
    # Non-existent file path
    global nonexistent_path
    nonexistent_path = os.path.join(test_dir, "nonexistent.txt")
    
    # Unsupported file type
    with open(os.path.join(test_dir, "unsupported.xyz"), "w") as f:
        f.write("Some content")
    
    logger.info("Created invalid test files")

def test_invalid_json():
    """Test parsing an invalid JSON file."""
    try:
        file_path = os.path.join(test_dir, "invalid.json")
        parse_json_file(file_path)
        logger.error("Test failed: Expected exception for invalid JSON file")
        return False
    except ValueError as e:
        logger.info(f"Correctly caught ValueError for invalid JSON: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected exception type for invalid JSON: {e}")
        return False

def test_empty_file():
    """Test parsing an empty file."""
    try:
        file_path = os.path.join(test_dir, "empty.txt")
        content = parse_text_file(file_path)
        logger.info(f"Successfully parsed empty text file. Content: '{content}'")
        assert content == "", "Empty file should return empty string"
        return True
    except Exception as e:
        logger.error(f"Error parsing empty file: {e}")
        return False

def test_nonexistent_file():
    """Test parsing a non-existent file."""
    try:
        parse_text_file(nonexistent_path)
        logger.error("Test failed: Expected exception for non-existent file")
        return False
    except FileNotFoundError as e:
        logger.info(f"Correctly caught FileNotFoundError: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected exception type for non-existent file: {e}")
        return False

def test_unsupported_file_type():
    """Test processing an unsupported file type."""
    try:
        file_path = os.path.join(test_dir, "unsupported.xyz")
        result = process_file(file_path)
        logger.info(f"Process file result for unsupported type: {result}")
        assert result["error"] is not None, "Expected error for unsupported file type"
        assert "Unsupported file type" in result["error"], "Expected 'Unsupported file type' error message"
        return True
    except Exception as e:
        logger.error(f"Unexpected exception for unsupported file type: {e}")
        return False

def run_tests():
    """Run all tests."""
    tests = [
        ("Invalid JSON", test_invalid_json),
        ("Empty File", test_empty_file),
        ("Non-existent File", test_nonexistent_file),
        ("Unsupported File Type", test_unsupported_file_type),
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
        create_invalid_files()
        success = run_tests()
        sys.exit(0 if success else 1)
    finally:
        cleanup()
