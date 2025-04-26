#!/usr/bin/env python3
"""
Test script for ODT file conversion.
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
from convertor.core import parse_odt_file, process_file

# Import odfpy for creating test ODT files
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties
from odf.text import P, Span

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

def create_test_odt_file():
    """Create a test ODT file using odfpy."""
    try:
        # Create a new ODT document
        doc = OpenDocumentText()
        
        # Create a style for bold text
        bold_style = Style(name="Bold", family="text")
        bold_style.addElement(TextProperties(fontweight="bold"))
        doc.styles.addElement(bold_style)
        
        # Create a style for italic text
        italic_style = Style(name="Italic", family="text")
        italic_style.addElement(TextProperties(fontstyle="italic"))
        doc.styles.addElement(italic_style)
        
        # Add a heading
        heading = P(stylename="Heading1")
        heading.addText("Test ODT Document")
        doc.text.addElement(heading)
        
        # Add a paragraph
        para1 = P()
        para1.addText("This is a paragraph of text for testing ODT parsing.")
        doc.text.addElement(para1)
        
        # Add a paragraph with styled text
        para2 = P()
        para2.addText("This paragraph contains ")
        
        bold_span = Span(stylename="Bold")
        bold_span.addText("bold")
        para2.addElement(bold_span)
        
        para2.addText(" and ")
        
        italic_span = Span(stylename="Italic")
        italic_span.addText("italic")
        para2.addElement(italic_span)
        
        para2.addText(" text.")
        doc.text.addElement(para2)
        
        # Add a list-like paragraph
        doc.text.addElement(P(text="- Item 1"))
        doc.text.addElement(P(text="- Item 2"))
        doc.text.addElement(P(text="- Item 3"))
        
        # Save the document
        file_path = os.path.join(test_dir, "test.odt")
        doc.save(file_path)
        
        logger.info("Created test ODT file")
        return True
    except Exception as e:
        logger.error(f"Error creating test ODT file: {e}")
        return False

def test_odt_parsing():
    """Test parsing an ODT file."""
    try:
        file_path = os.path.join(test_dir, "test.odt")
        content = parse_odt_file(file_path)
        logger.info(f"Successfully parsed ODT file. Content length: {len(content)}")
        
        # Check if important content is present
        assert "Test ODT Document" in content, "ODT heading not found"
        assert "This is a paragraph of text" in content, "ODT paragraph content not found"
        assert "This paragraph contains" in content, "ODT paragraph content not found"
        assert "Item 1" in content, "ODT list content not found"
        
        return True
    except Exception as e:
        logger.error(f"Error parsing ODT file: {e}")
        return False

def test_odt_processing():
    """Test processing an ODT file through the main process_file function."""
    try:
        file_path = os.path.join(test_dir, "test.odt")
        result = process_file(file_path)
        logger.info(f"Process file result for ODT: {result}")
        
        # Check if there's an error (there will be if no API key is set, but that's expected)
        if result["error"] and "API Key Missing" in result["error"]:
            logger.info("API key missing error is expected without a Gemini API key")
            return True
        
        # If there's no API key error, check if content was processed
        if result["content"] is not None:
            return True
        
        # If there's another error, log it
        if result["error"]:
            logger.error(f"Unexpected error processing ODT file: {result['error']}")
            return False
        
        return False
    except Exception as e:
        logger.error(f"Error in test_odt_processing: {e}")
        return False

def run_tests():
    """Run all tests."""
    tests = [
        ("ODT Parsing", test_odt_parsing),
        ("ODT Processing", test_odt_processing),
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
        if create_test_odt_file():
            success = run_tests()
            sys.exit(0 if success else 1)
        else:
            logger.error("Failed to create test ODT file, skipping tests")
            sys.exit(1)
    finally:
        cleanup()
