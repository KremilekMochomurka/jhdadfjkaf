# API Reference

This document provides detailed information about all available API endpoints in the File Conversion System.

## Base URL

All API endpoints are relative to the base URL of your File Conversion System installation:

```
https://your-server-address/api
```

Replace `your-server-address` with the actual address where the File Conversion System is hosted.

## Authentication

Authentication methods are detailed in the [Authentication Guide](authentication_guide.md).

## API Endpoints

### Document Management

#### Upload Documents

```
POST /upload
```

Upload one or more files for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `files[]`: One or more files to upload (required)

**Response:**
```json
{
  "documents": [
    {
      "id": 123,
      "filename": "document.pdf",
      "status": "processing",
      "upload_time": "2023-06-15T10:30:00Z"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (no files or invalid files)
- 413: File too large
- 500: Server error

---

#### List Documents

```
GET /documents
```

Retrieve a list of all documents.

**Query Parameters:**
- `show_parts`: Boolean, whether to include document parts (default: false)
- `folder_id`: Integer, filter by folder ID
- `content_type`: String, filter by content type
- `status`: String, filter by processing status
- `page`: Integer, page number for pagination (default: 1)
- `per_page`: Integer, items per page (default: 20)

**Response:**
```json
{
  "documents": [
    {
      "id": 123,
      "filename": "document.pdf",
      "status": "completed",
      "upload_time": "2023-06-15T10:30:00Z",
      "folder_id": 1,
      "content_type": "pdf"
    }
  ],
  "pagination": {
    "total_items": 50,
    "total_pages": 3,
    "current_page": 1,
    "per_page": 20,
    "has_next": true,
    "has_prev": false
  }
}
```

**Status Codes:**
- 200: Success
- 500: Server error

---

#### Get Document Details

```
GET /documents/{doc_id}
```

Retrieve details and content of a specific document.

**Path Parameters:**
- `doc_id`: Document ID (required)

**Response:**
```json
{
  "id": 123,
  "filename": "document.pdf",
  "original_filename": "important_document.pdf",
  "status": "completed",
  "upload_time": "2023-06-15T10:30:00Z",
  "completion_time": "2023-06-15T10:31:30Z",
  "content": "Extracted document content...",
  "folder_id": 1,
  "content_type": "pdf",
  "file_size": 1024000,
  "page_count": 5
}
```

**Status Codes:**
- 200: Success
- 404: Document not found
- 500: Server error

---

#### Update Document

```
PUT /documents/{doc_id}
```

Update a document's content or metadata.

**Path Parameters:**
- `doc_id`: Document ID (required)

**Request Body:**
```json
{
  "content": "Updated document content...",
  "filename": "new_filename.pdf"
}
```

**Response:**
```json
{
  "id": 123,
  "filename": "new_filename.pdf",
  "status": "completed",
  "update_time": "2023-06-15T11:30:00Z"
}
```

**Status Codes:**
- 200: Success
- 404: Document not found
- 500: Server error

---

#### Delete Document

```
DELETE /documents/{doc_id}
```

Delete a document.

**Path Parameters:**
- `doc_id`: Document ID (required)

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

**Status Codes:**
- 200: Success
- 404: Document not found
- 500: Server error

---

#### Get Document Status

```
GET /documents/{doc_id}/status
```

Check the processing status of a document.

**Path Parameters:**
- `doc_id`: Document ID (required)

**Response:**
```json
{
  "id": 123,
  "status": "completed",
  "error_message": null
}
```

**Status Codes:**
- 200: Success
- 404: Document not found
- 500: Server error

---

#### Move Document

```
POST /documents/{doc_id}/move
```

Move a document to a different folder.

**Path Parameters:**
- `doc_id`: Document ID (required)

**Request Body:**
```json
{
  "folder_id": 2
}
```

**Response:**
```json
{
  "success": true,
  "message": "Document moved successfully"
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (missing folder_id)
- 404: Document or folder not found
- 500: Server error

---

### Folder Management

#### List Folders

```
GET /folders
```

Retrieve a list of all folders.

**Query Parameters:**
- `type`: String, filter by folder type
- `parent_id`: Integer, filter by parent folder ID

**Response:**
```json
{
  "folders": [
    {
      "id": 1,
      "name": "Emailová korespondence",
      "description": "Složka pro emailovou korespondenci",
      "folder_type": "email",
      "parent_id": null,
      "created_at": "2023-06-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Firemní know-how",
      "description": "Složka pro firemní dokumentaci, návody a postupy",
      "folder_type": "company_know_how",
      "parent_id": null,
      "created_at": "2023-06-15T10:30:00Z"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 500: Server error

---

#### Create Folder

```
POST /folders
```

Create a new folder.

**Request Body:**
```json
{
  "name": "New Folder",
  "description": "Folder description",
  "parent_id": null,
  "folder_type": "company_know_how"
}
```

**Response:**
```json
{
  "id": 3,
  "name": "New Folder",
  "description": "Folder description",
  "folder_type": "company_know_how",
  "parent_id": null,
  "created_at": "2023-06-15T10:30:00Z"
}
```

**Status Codes:**
- 201: Created
- 400: Bad request (missing required fields)
- 500: Server error

---

#### Get Folder Details

```
GET /folders/{folder_id}
```

Retrieve details of a specific folder, including documents and subfolders.

**Path Parameters:**
- `folder_id`: Folder ID (required)

**Response:**
```json
{
  "id": 1,
  "name": "Emailová korespondence",
  "description": "Složka pro emailovou korespondenci",
  "folder_type": "email",
  "parent_id": null,
  "created_at": "2023-06-15T10:30:00Z",
  "documents": [
    {
      "id": 123,
      "filename": "email.pdf",
      "status": "completed"
    }
  ],
  "subfolders": []
}
```

**Status Codes:**
- 200: Success
- 404: Folder not found
- 500: Server error

---

#### Delete Folder

```
DELETE /folders/{folder_id}
```

Delete a folder and move its documents to the parent folder.

**Path Parameters:**
- `folder_id`: Folder ID (required)

**Response:**
```json
{
  "success": true,
  "message": "Folder deleted successfully"
}
```

**Status Codes:**
- 200: Success
- 404: Folder not found
- 500: Server error

## Error Responses

All API endpoints return errors in a consistent format:

```json
{
  "error": "Error message describing what went wrong",
  "details": "Additional details about the error (if available)"
}
```

## Pagination

Endpoints that return lists of items support pagination through the following query parameters:
- `page`: Page number (starting from 1)
- `per_page`: Number of items per page

Paginated responses include a `pagination` object with metadata about the pagination:

```json
"pagination": {
  "total_items": 50,
  "total_pages": 3,
  "current_page": 1,
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```
