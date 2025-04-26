# File Conversion Module

This module provides functionality for extracting content from various file formats and processing it using AI.

## Supported File Formats

### Text Documents
- Plain Text (.txt)
  - Extracts raw text content
  - Handles UTF-8 encoding

- PDF Documents (.pdf)
  - Extracts text from a limited number of pages (default: 5) to avoid API limits
  - Handles multi-page documents with smart page limiting
  - Reports extraction failures for individual pages
  - Supports OCR (Optical Character Recognition) for scanned documents
  - Falls back to AI image description for image-only PDFs
  - Provides information about total pages in the document

- Microsoft Word Documents (.docx)
  - Extracts text from paragraphs
  - Preserves paragraph structure
  - (Future enhancement: Extract tables)

- Microsoft Word Legacy Documents (.doc)
  - Uses antiword command-line tool
  - Requires antiword to be installed on the system
  - Handles UTF-8 encoding

- OpenDocument Text (.odt)
  - Extracts text from paragraphs
  - Handles text spans and formatting
  - Compatible with LibreOffice/OpenOffice documents

- HTML Documents (.html, .htm)
  - Extracts text content
  - Removes scripts and styles
  - Preserves document structure
  - Extracts title if available

### Structured Data
- Excel Spreadsheets (.xlsx, .xls)
  - Extracts data from all sheets
  - Handles multi-sheet documents
  - Formats data in a readable table format

- CSV Files (.csv)
  - Automatically detects delimiters (comma, semicolon, tab, pipe)
  - Handles different encodings (UTF-8, Latin-1)
  - Formats data in a readable table format

- JSON Files (.json)
  - Validates and formats JSON data
  - Handles arrays and objects
  - Converts arrays of objects to table format when possible
  - Pretty-prints complex structures

### Images
- Supported formats: PNG (.png), JPEG (.jpg, .jpeg), WebP (.webp), GIF (.gif), BMP (.bmp)
- Uses Google's Gemini API for image description
- Generates descriptive text based on image content

## Core Functions

### `process_file(file_path)`

The main function for processing files. It:
1. Identifies the file type based on extension
2. Calls the appropriate parsing function
3. Processes the extracted content with AI (if applicable)
4. Returns a dictionary with `content` and `error` keys

Example:
```python
result = process_file("document.pdf")
if result["error"]:
    print(f"Error: {result['error']}")
else:
    print(f"Content: {result['content']}")
```

### Parsing Functions

- `parse_text_file(file_path)`: Parses plain text files
- `parse_pdf_file(file_path)`: Parses PDF files
- `parse_docx_file(file_path)`: Parses DOCX files
- `parse_doc_file(file_path)`: Parses DOC files using antiword
- `parse_xlsx_file(file_path)`: Parses Excel files
- `parse_csv_file(file_path)`: Parses CSV files
- `parse_json_file(file_path)`: Parses JSON files
- `parse_html_file(file_path)`: Parses HTML files
- `parse_odt_file(file_path)`: Parses ODT files

### AI Processing Functions

- `get_ai_summary(content)`: Generates a summary of text content using Gemini API
- `get_ai_image_description(file_path)`: Generates a description of an image using Gemini API

## Error Handling

The module includes robust error handling:
- File not found errors
- Parsing errors for each file type
- API errors when calling Gemini
- Invalid file format errors

All errors are logged and returned in the result dictionary.

## Dependencies

- `PyPDF2`: For PDF parsing
- `pytesseract`: For OCR (Optical Character Recognition)
- `pdf2image`: For converting PDF to images for OCR
- `python-docx`: For DOCX parsing
- `antiword`: For DOC parsing (command-line tool)
- `pandas` and `openpyxl`: For Excel and CSV parsing
- `odfpy`: For ODT parsing
- `beautifulsoup4` and `lxml`: For HTML parsing
- `Pillow`: For image processing
- `google-generativeai`: For AI processing

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

## Environment Variables

- `GEMINI_API_KEY`: Required for AI processing with Google's Gemini API
