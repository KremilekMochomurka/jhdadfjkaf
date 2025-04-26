#!/usr/bin/env python3
"""
Advanced test script for JSON file conversion with different structures.
"""

import os
import sys
import logging
import tempfile
import shutil
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the parsing functions from the convertor module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convertor.core import parse_json_file

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

def create_test_json_files():
    """Create test JSON files with different structures."""
    # Simple object
    simple_object = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "is_active": True,
        "balance": 1234.56
    }
    with open(os.path.join(test_dir, "simple_object.json"), "w") as f:
        json.dump(simple_object, f, indent=2)
    
    # Nested object
    nested_object = {
        "name": "John Doe",
        "age": 30,
        "contact": {
            "email": "john@example.com",
            "phone": "555-1234",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345"
            }
        },
        "preferences": {
            "theme": "dark",
            "notifications": True
        }
    }
    with open(os.path.join(test_dir, "nested_object.json"), "w") as f:
        json.dump(nested_object, f, indent=2)
    
    # Array of simple values
    simple_array = [1, 2, 3, 4, 5, "six", "seven", True, False, None]
    with open(os.path.join(test_dir, "simple_array.json"), "w") as f:
        json.dump(simple_array, f, indent=2)
    
    # Array of objects
    array_of_objects = [
        {"id": 1, "name": "John", "role": "admin"},
        {"id": 2, "name": "Jane", "role": "user"},
        {"id": 3, "name": "Bob", "role": "user"},
        {"id": 4, "name": "Alice", "role": "manager"}
    ]
    with open(os.path.join(test_dir, "array_of_objects.json"), "w") as f:
        json.dump(array_of_objects, f, indent=2)
    
    # Complex nested structure
    complex_structure = {
        "company": "ACME Inc.",
        "founded": 1985,
        "active": True,
        "departments": [
            {
                "name": "Engineering",
                "employees": [
                    {"id": 1, "name": "John", "skills": ["Python", "JavaScript"]},
                    {"id": 2, "name": "Jane", "skills": ["Java", "C++"]}
                ]
            },
            {
                "name": "Marketing",
                "employees": [
                    {"id": 3, "name": "Bob", "skills": ["SEO", "Content"]},
                    {"id": 4, "name": "Alice", "skills": ["Social Media", "Analytics"]}
                ]
            }
        ],
        "locations": {
            "headquarters": {"city": "San Francisco", "state": "CA"},
            "branches": [
                {"city": "New York", "state": "NY"},
                {"city": "Austin", "state": "TX"}
            ]
        }
    }
    with open(os.path.join(test_dir, "complex_structure.json"), "w") as f:
        json.dump(complex_structure, f, indent=2)
    
    logger.info("Created test JSON files with different structures")

def test_simple_object():
    """Test parsing a simple JSON object."""
    try:
        file_path = os.path.join(test_dir, "simple_object.json")
        content = parse_json_file(file_path)
        logger.info(f"Successfully parsed simple JSON object. Content length: {len(content)}")
        assert "John Doe" in content, "JSON content not found"
        assert "1234.56" in content, "JSON content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing simple JSON object: {e}")
        return False

def test_nested_object():
    """Test parsing a nested JSON object."""
    try:
        file_path = os.path.join(test_dir, "nested_object.json")
        content = parse_json_file(file_path)
        logger.info(f"Successfully parsed nested JSON object. Content length: {len(content)}")
        assert "John Doe" in content, "JSON content not found"
        assert "123 Main St" in content, "Nested JSON content not found"
        assert "preferences" in content, "Nested JSON content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing nested JSON object: {e}")
        return False

def test_simple_array():
    """Test parsing a simple JSON array."""
    try:
        file_path = os.path.join(test_dir, "simple_array.json")
        content = parse_json_file(file_path)
        logger.info(f"Successfully parsed simple JSON array. Content length: {len(content)}")
        assert "Array with 10 items" in content, "Array size not found"
        assert "six" in content, "Array content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing simple JSON array: {e}")
        return False

def test_array_of_objects():
    """Test parsing a JSON array of objects."""
    try:
        file_path = os.path.join(test_dir, "array_of_objects.json")
        content = parse_json_file(file_path)
        logger.info(f"Successfully parsed JSON array of objects. Content length: {len(content)}")
        assert "Array with 4 items" in content, "Array size not found"
        assert "John" in content, "Array content not found"
        assert "admin" in content, "Array content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing JSON array of objects: {e}")
        return False

def test_complex_structure():
    """Test parsing a complex nested JSON structure."""
    try:
        file_path = os.path.join(test_dir, "complex_structure.json")
        content = parse_json_file(file_path)
        logger.info(f"Successfully parsed complex JSON structure. Content length: {len(content)}")
        assert "ACME Inc." in content, "JSON content not found"
        assert "Engineering" in content, "Nested JSON content not found"
        assert "Python" in content, "Deeply nested JSON content not found"
        assert "headquarters" in content, "Nested JSON content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing complex JSON structure: {e}")
        return False

def run_tests():
    """Run all tests."""
    tests = [
        ("Simple JSON Object", test_simple_object),
        ("Nested JSON Object", test_nested_object),
        ("Simple JSON Array", test_simple_array),
        ("JSON Array of Objects", test_array_of_objects),
        ("Complex JSON Structure", test_complex_structure),
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
        create_test_json_files()
        success = run_tests()
        sys.exit(0 if success else 1)
    finally:
        cleanup()
