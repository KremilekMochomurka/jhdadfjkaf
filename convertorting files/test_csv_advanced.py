#!/usr/bin/env python3
"""
Advanced test script for CSV file conversion with different delimiters and encodings.
"""

import os
import sys
import logging
import tempfile
import shutil
import codecs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the parsing functions from the convertor module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from convertor.core import parse_csv_file

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

def create_test_csv_files():
    """Create test CSV files with different delimiters and encodings."""
    # Standard CSV with comma delimiter
    with open(os.path.join(test_dir, "comma.csv"), "w") as f:
        f.write("name,age,email\n")
        f.write("John Doe,30,john@example.com\n")
        f.write("Jane Smith,25,jane@example.com\n")
    
    # CSV with semicolon delimiter
    with open(os.path.join(test_dir, "semicolon.csv"), "w") as f:
        f.write("name;age;email\n")
        f.write("John Doe;30;john@example.com\n")
        f.write("Jane Smith;25;jane@example.com\n")
    
    # CSV with tab delimiter
    with open(os.path.join(test_dir, "tab.csv"), "w") as f:
        f.write("name\tage\temail\n")
        f.write("John Doe\t30\tjohn@example.com\n")
        f.write("Jane Smith\t25\tjane@example.com\n")
    
    # CSV with pipe delimiter
    with open(os.path.join(test_dir, "pipe.csv"), "w") as f:
        f.write("name|age|email\n")
        f.write("John Doe|30|john@example.com\n")
        f.write("Jane Smith|25|jane@example.com\n")
    
    # CSV with UTF-8 encoding and special characters
    with codecs.open(os.path.join(test_dir, "utf8.csv"), "w", encoding="utf-8") as f:
        f.write("name,age,country\n")
        f.write("José García,35,España\n")
        f.write("François Dupont,42,France\n")
        f.write("Jürgen Müller,28,Deutschland\n")
    
    # CSV with Latin-1 encoding
    with codecs.open(os.path.join(test_dir, "latin1.csv"), "w", encoding="latin-1") as f:
        f.write("name,age,country\n")
        f.write("José García,35,España\n")
        f.write("François Dupont,42,France\n")
        f.write("Jürgen Müller,28,Deutschland\n")
    
    logger.info("Created test CSV files with different delimiters and encodings")

def test_csv_comma():
    """Test parsing a CSV file with comma delimiter."""
    try:
        file_path = os.path.join(test_dir, "comma.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV with comma delimiter. Content length: {len(content)}")
        assert "John Doe" in content, "CSV content not found"
        assert "Jane Smith" in content, "CSV content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV with comma delimiter: {e}")
        return False

def test_csv_semicolon():
    """Test parsing a CSV file with semicolon delimiter."""
    try:
        file_path = os.path.join(test_dir, "semicolon.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV with semicolon delimiter. Content length: {len(content)}")
        assert "John Doe" in content, "CSV content not found"
        assert "Jane Smith" in content, "CSV content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV with semicolon delimiter: {e}")
        return False

def test_csv_tab():
    """Test parsing a CSV file with tab delimiter."""
    try:
        file_path = os.path.join(test_dir, "tab.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV with tab delimiter. Content length: {len(content)}")
        assert "John Doe" in content, "CSV content not found"
        assert "Jane Smith" in content, "CSV content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV with tab delimiter: {e}")
        return False

def test_csv_pipe():
    """Test parsing a CSV file with pipe delimiter."""
    try:
        file_path = os.path.join(test_dir, "pipe.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV with pipe delimiter. Content length: {len(content)}")
        assert "John Doe" in content, "CSV content not found"
        assert "Jane Smith" in content, "CSV content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV with pipe delimiter: {e}")
        return False

def test_csv_utf8():
    """Test parsing a CSV file with UTF-8 encoding."""
    try:
        file_path = os.path.join(test_dir, "utf8.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV with UTF-8 encoding. Content length: {len(content)}")
        assert "José García" in content, "UTF-8 content not found"
        assert "François Dupont" in content, "UTF-8 content not found"
        assert "Jürgen Müller" in content, "UTF-8 content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV with UTF-8 encoding: {e}")
        return False

def test_csv_latin1():
    """Test parsing a CSV file with Latin-1 encoding."""
    try:
        file_path = os.path.join(test_dir, "latin1.csv")
        content = parse_csv_file(file_path)
        logger.info(f"Successfully parsed CSV with Latin-1 encoding. Content length: {len(content)}")
        assert "José García" in content, "Latin-1 content not found"
        assert "François Dupont" in content, "Latin-1 content not found"
        assert "Jürgen Müller" in content, "Latin-1 content not found"
        return True
    except Exception as e:
        logger.error(f"Error parsing CSV with Latin-1 encoding: {e}")
        return False

def run_tests():
    """Run all tests."""
    tests = [
        ("CSV with Comma Delimiter", test_csv_comma),
        ("CSV with Semicolon Delimiter", test_csv_semicolon),
        ("CSV with Tab Delimiter", test_csv_tab),
        ("CSV with Pipe Delimiter", test_csv_pipe),
        ("CSV with UTF-8 Encoding", test_csv_utf8),
        ("CSV with Latin-1 Encoding", test_csv_latin1),
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
        create_test_csv_files()
        success = run_tests()
        sys.exit(0 if success else 1)
    finally:
        cleanup()
