#!/usr/bin/env python3
"""
Test script for HTML and ODT file conversion.
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
from convertor.core import parse_html_file, parse_odt_file, process_file

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

def create_test_html_file():
    """Create a test HTML file."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Test HTML Document</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { color: blue; }
    </style>
</head>
<body>
    <h1>Test HTML Document</h1>
    <p>This is a paragraph of text for testing HTML parsing.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    <script>
        // This script content should be removed during parsing
        console.log("This should not appear in the parsed content");
    </script>
    <p>Another paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
</body>
</html>"""
    
    with open(os.path.join(test_dir, "test.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    
    logger.info("Created test HTML file")

def test_html_parsing():
    """Test parsing an HTML file."""
    try:
        file_path = os.path.join(test_dir, "test.html")
        content = parse_html_file(file_path)
        logger.info(f"Successfully parsed HTML file. Content length: {len(content)}")
        
        # Check if important content is present
        assert "Test HTML Document" in content, "HTML title not found"
        assert "This is a paragraph of text" in content, "HTML paragraph content not found"
        assert "Item 1" in content, "HTML list content not found"
        assert "Another paragraph with" in content, "HTML paragraph content not found"
        
        # Check if script content is removed
        assert "This should not appear in the parsed content" not in content, "Script content was not removed"
        
        return True
    except Exception as e:
        logger.error(f"Error parsing HTML file: {e}")
        return False

def test_html_processing():
    """Test processing an HTML file through the main process_file function."""
    try:
        file_path = os.path.join(test_dir, "test.html")
        result = process_file(file_path)
        logger.info(f"Process file result for HTML: {result}")
        
        # Check if there's an error (there will be if no API key is set, but that's expected)
        if result["error"] and "API Key Missing" in result["error"]:
            logger.info("API key missing error is expected without a Gemini API key")
            return True
        
        # If there's no API key error, check if content was processed
        if result["content"] is not None:
            return True
        
        # If there's another error, log it
        if result["error"]:
            logger.error(f"Unexpected error processing HTML file: {result['error']}")
            return False
        
        return False
    except Exception as e:
        logger.error(f"Error in test_html_processing: {e}")
        return False

def run_tests():
    """Run all tests."""
    tests = [
        ("HTML Parsing", test_html_parsing),
        ("HTML Processing", test_html_processing),
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
        create_test_html_file()
        success = run_tests()
        sys.exit(0 if success else 1)
    finally:
        cleanup()
