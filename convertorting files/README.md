# File Conversion System

A robust file conversion system that extracts content from various file formats and processes it using AI for summarization or description.

## Supported File Formats

The system supports the following file formats:

### Text Documents
- Plain Text (.txt)
- PDF Documents (.pdf)
- Microsoft Word Documents (.docx, .doc)
- OpenDocument Text (.odt)
- HTML Documents (.html, .htm)

### Structured Data
- Excel Spreadsheets (.xlsx, .xls)
- CSV Files (.csv)
- JSON Files (.json)

### Images
- PNG Images (.png)
- JPEG Images (.jpg, .jpeg)
- WebP Images (.webp)
- GIF Images (.gif)
- BMP Images (.bmp)

## Features

- **Text Extraction**: Extracts text content from various document formats
- **OCR Processing**: Uses Optical Character Recognition for scanned documents
- **Image Description**: Generates descriptions for images using AI
- **Data Structuring**: Processes structured data from spreadsheets and JSON files
- **AI Summarization**: Summarizes extracted content using Google's Gemini API
- **Smart Page Limiting**: Automatically limits pages processed for large documents
- **Content Truncation**: Intelligently truncates large content to avoid API limits
- **Retry Logic**: Implements automatic retries for API calls
- **Robust Error Handling**: Gracefully handles errors and edge cases
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Requirements

The system requires the following dependencies:

```
Flask>=2.0
Flask-SQLAlchemy>=2.5
python-dotenv>=0.19
google-generativeai>=0.4
Pillow>=9.0
python-docx>=1.1.0
PyPDF2>=3.0.0
openpyxl>=3.1.0
pandas>=2.0.0
odfpy>=1.4.1
beautifulsoup4>=4.11.0
lxml>=4.9.0
pytesseract>=0.3.10
pdf2image>=1.16.3
```

### OCR Dependencies

For OCR functionality to work, you need to install:

1. Tesseract OCR engine:
   - On macOS: `brew install tesseract tesseract-lang`
   - On Ubuntu/Debian: `apt-get install tesseract-ocr tesseract-ocr-ces tesseract-ocr-eng`
   - On Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

2. Poppler (for pdf2image):
   - On macOS: `brew install poppler`
   - On Ubuntu/Debian: `apt-get install poppler-utils`
   - On Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases

Additionally, for processing .doc files, the system requires the `antiword` command-line tool to be installed on the system.

## Installation

1. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Install antiword (for .doc file support):
   - On macOS: `brew install antiword`
   - On Ubuntu/Debian: `apt-get install antiword`
   - On Windows: Download from [Antiword website](http://www.winfield.demon.nl/) and add to PATH

3. Set up environment variables:
   - Create a `.env` file with your Google Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

## Usage

### As a Library

```python
from convertor.core import process_file

# Process a file
result = process_file("path/to/your/file.pdf")

# Check for errors
if result["error"]:
    print(f"Error: {result['error']}")
else:
    print(f"Processed content: {result['content']}")
```

### As a Web Service

The system can be used as a web service with Flask:

1. Start the Flask application:
   ```
   python app.py
   ```

2. Access the web interface at `http://localhost:5001`

3. Upload files through the web interface

## Testing

The system includes comprehensive tests for all supported file formats:

```
# Test all formats
python test_all_formats.py

# Test specific formats
python test_file_conversion.py
python test_excel_conversion.py
python test_html_odt.py
python test_error_handling.py
python test_csv_advanced.py
python test_json_advanced.py
```

## License

[MIT License](LICENSE)
