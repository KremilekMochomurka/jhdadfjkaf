# User Guide - File Conversion System

This guide explains how to use the file conversion system to upload, process, and manage various file types.

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

## Uploading Files

1. Navigate to the main page of the application
2. In the "Upload New Document" section, click the file input field
3. Select a file from your computer (must be one of the supported formats)
4. Click the "Upload and Process" button
5. Wait for the file to be processed (this may take a few seconds to a minute depending on the file size and type)

## Viewing Processed Documents

1. After uploading, your document will appear in the "Processed Documents" section
2. Click on a document to view its processed content
3. The processed content will be displayed in the editor

## Editing Processed Content

1. After viewing a processed document, you can edit its content in the editor
2. Make your changes to the text
3. Click the "Save" button to save your changes

## Managing Documents

1. To refresh the list of documents, click the "Refresh List" button
2. To delete a document, click the delete button next to the document in the list

## Troubleshooting

If you encounter any issues:

- **File Not Supported**: Make sure your file is one of the supported formats listed above
- **Processing Error**: Some files may be corrupted or in an unsupported format variant
- **Empty Content**: Some files may not contain extractable text content
- **Large Files**: Very large files may take longer to process or may fail due to size limitations

## API Access

Advanced users can access the system programmatically through the API:

- `POST /api/upload`: Upload a new file
- `GET /api/documents`: Get a list of all documents
- `GET /api/documents/<id>`: Get details of a specific document
- `PUT /api/documents/<id>`: Update a document's content
- `DELETE /api/documents/<id>`: Delete a document

For detailed information on integrating with the API, please refer to the [Integration Documentation](../docs/index.md).
