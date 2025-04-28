# Code Examples

This document provides code examples for common integration scenarios with the File Conversion System API.

## Prerequisites

Before using these examples, make sure you have:

1. Access to the File Conversion System API
2. A valid API key (see [Authentication Guide](authentication_guide.md))
3. The base URL of your File Conversion System installation

## Examples by Programming Language

### Python

#### Installing Required Libraries

```bash
pip install requests
```

#### Uploading a File

```python
import requests

def upload_file(api_base_url, api_key, file_path):
    """
    Upload a file to the File Conversion System.
    
    Args:
        api_base_url (str): Base URL of the API
        api_key (str): Your API key
        file_path (str): Path to the file to upload
        
    Returns:
        dict: API response
    """
    url = f"{api_base_url}/upload"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    with open(file_path, 'rb') as file:
        files = {'files[]': file}
        response = requests.post(url, headers=headers, files=files)
    
    return response.json()

# Example usage
api_base_url = "https://your-server-address/api"
api_key = "your_api_key"
file_path = "path/to/document.pdf"

result = upload_file(api_base_url, api_key, file_path)
print(result)
```

#### Listing Documents

```python
import requests

def list_documents(api_base_url, api_key, folder_id=None, page=1, per_page=20):
    """
    List documents from the File Conversion System.
    
    Args:
        api_base_url (str): Base URL of the API
        api_key (str): Your API key
        folder_id (int, optional): Filter by folder ID
        page (int, optional): Page number for pagination
        per_page (int, optional): Items per page
        
    Returns:
        dict: API response with documents and pagination info
    """
    url = f"{api_base_url}/documents"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    params = {
        "page": page,
        "per_page": per_page
    }
    
    if folder_id is not None:
        params["folder_id"] = folder_id
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Example usage
api_base_url = "https://your-server-address/api"
api_key = "your_api_key"

# List all documents
all_docs = list_documents(api_base_url, api_key)
print(f"Found {len(all_docs['documents'])} documents")

# List documents in a specific folder
folder_docs = list_documents(api_base_url, api_key, folder_id=1)
print(f"Found {len(folder_docs['documents'])} documents in folder 1")
```

#### Getting Document Content

```python
import requests
import time

def get_document_content(api_base_url, api_key, doc_id, max_retries=10, retry_delay=2):
    """
    Get the content of a processed document, with retry logic for documents still processing.
    
    Args:
        api_base_url (str): Base URL of the API
        api_key (str): Your API key
        doc_id (int): Document ID
        max_retries (int, optional): Maximum number of retries for processing documents
        retry_delay (int, optional): Delay between retries in seconds
        
    Returns:
        dict: Document details including content
    """
    url = f"{api_base_url}/documents/{doc_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Check if document is still processing
        if data.get("status") == "processing":
            print(f"Document still processing. Retry {attempt + 1}/{max_retries}...")
            time.sleep(retry_delay)
            continue
            
        return data
    
    # If we've exhausted retries
    return {"error": "Document processing timed out"}

# Example usage
api_base_url = "https://your-server-address/api"
api_key = "your_api_key"
doc_id = 123

document = get_document_content(api_base_url, api_key, doc_id)
if "error" not in document:
    print(f"Document content: {document['content'][:100]}...")  # Print first 100 chars
else:
    print(f"Error: {document['error']}")
```

#### Complete Integration Example

```python
import requests
import time
import os

class FileConversionClient:
    def __init__(self, api_base_url, api_key):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}"
        }
    
    def upload_file(self, file_path):
        """Upload a file for processing"""
        url = f"{self.api_base_url}/upload"
        
        with open(file_path, 'rb') as file:
            files = {'files[]': file}
            response = requests.post(url, headers=self.headers, files=files)
        
        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.text}")
            
        return response.json()
    
    def get_document_status(self, doc_id):
        """Check document processing status"""
        url = f"{self.api_base_url}/documents/{doc_id}/status"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Status check failed: {response.text}")
            
        return response.json()
    
    def get_document_content(self, doc_id):
        """Get document content"""
        url = f"{self.api_base_url}/documents/{doc_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Content retrieval failed: {response.text}")
            
        return response.json()
    
    def wait_for_processing(self, doc_id, max_retries=30, retry_delay=2):
        """Wait for document processing to complete"""
        for attempt in range(max_retries):
            status = self.get_document_status(doc_id)
            
            if status["status"] == "completed":
                return True
            elif status["status"] == "error":
                raise Exception(f"Processing error: {status.get('error_message')}")
            
            print(f"Document still processing. Retry {attempt + 1}/{max_retries}...")
            time.sleep(retry_delay)
        
        raise Exception("Document processing timed out")
    
    def process_file(self, file_path):
        """Complete process: upload, wait, and get content"""
        # Upload file
        print(f"Uploading {os.path.basename(file_path)}...")
        upload_result = self.upload_file(file_path)
        doc_id = upload_result["documents"][0]["id"]
        
        # Wait for processing
        print(f"Waiting for processing to complete...")
        self.wait_for_processing(doc_id)
        
        # Get content
        print(f"Retrieving processed content...")
        document = self.get_document_content(doc_id)
        
        return document

# Example usage
api_base_url = "https://your-server-address/api"
api_key = "your_api_key"
file_path = "path/to/document.pdf"

client = FileConversionClient(api_base_url, api_key)

try:
    result = client.process_file(file_path)
    print(f"Successfully processed {os.path.basename(file_path)}")
    print(f"Content preview: {result['content'][:200]}...")  # First 200 chars
except Exception as e:
    print(f"Error: {e}")
```

### JavaScript (Node.js)

#### Installing Required Libraries

```bash
npm install axios form-data
```

#### Uploading a File

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function uploadFile(apiBaseUrl, apiKey, filePath) {
  const url = `${apiBaseUrl}/upload`;
  const formData = new FormData();
  
  // Add file to form data
  formData.append('files[]', fs.createReadStream(filePath));
  
  try {
    const response = await axios.post(url, formData, {
      headers: {
        ...formData.getHeaders(),
        'Authorization': `Bearer ${apiKey}`
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Upload error:', error.response?.data || error.message);
    throw error;
  }
}

// Example usage
const apiBaseUrl = 'https://your-server-address/api';
const apiKey = 'your_api_key';
const filePath = 'path/to/document.pdf';

uploadFile(apiBaseUrl, apiKey, filePath)
  .then(result => console.log('Upload result:', result))
  .catch(error => console.error('Error:', error));
```

#### Complete Integration Example

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

class FileConversionClient {
  constructor(apiBaseUrl, apiKey) {
    this.apiBaseUrl = apiBaseUrl;
    this.apiKey = apiKey;
    this.headers = {
      'Authorization': `Bearer ${apiKey}`
    };
  }
  
  async uploadFile(filePath) {
    const url = `${this.apiBaseUrl}/upload`;
    const formData = new FormData();
    
    formData.append('files[]', fs.createReadStream(filePath));
    
    try {
      const response = await axios.post(url, formData, {
        headers: {
          ...formData.getHeaders(),
          ...this.headers
        }
      });
      
      return response.data;
    } catch (error) {
      throw new Error(`Upload failed: ${error.response?.data?.error || error.message}`);
    }
  }
  
  async getDocumentStatus(docId) {
    const url = `${this.apiBaseUrl}/documents/${docId}/status`;
    
    try {
      const response = await axios.get(url, { headers: this.headers });
      return response.data;
    } catch (error) {
      throw new Error(`Status check failed: ${error.response?.data?.error || error.message}`);
    }
  }
  
  async getDocumentContent(docId) {
    const url = `${this.apiBaseUrl}/documents/${docId}`;
    
    try {
      const response = await axios.get(url, { headers: this.headers });
      return response.data;
    } catch (error) {
      throw new Error(`Content retrieval failed: ${error.response?.data?.error || error.message}`);
    }
  }
  
  async waitForProcessing(docId, maxRetries = 30, retryDelay = 2000) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const status = await this.getDocumentStatus(docId);
      
      if (status.status === 'completed') {
        return true;
      } else if (status.status === 'error') {
        throw new Error(`Processing error: ${status.error_message}`);
      }
      
      console.log(`Document still processing. Retry ${attempt + 1}/${maxRetries}...`);
      await new Promise(resolve => setTimeout(resolve, retryDelay));
    }
    
    throw new Error('Document processing timed out');
  }
  
  async processFile(filePath) {
    // Upload file
    console.log(`Uploading ${path.basename(filePath)}...`);
    const uploadResult = await this.uploadFile(filePath);
    const docId = uploadResult.documents[0].id;
    
    // Wait for processing
    console.log('Waiting for processing to complete...');
    await this.waitForProcessing(docId);
    
    // Get content
    console.log('Retrieving processed content...');
    const document = await this.getDocumentContent(docId);
    
    return document;
  }
}

// Example usage
const apiBaseUrl = 'https://your-server-address/api';
const apiKey = 'your_api_key';
const filePath = 'path/to/document.pdf';

const client = new FileConversionClient(apiBaseUrl, apiKey);

client.processFile(filePath)
  .then(result => {
    console.log(`Successfully processed ${path.basename(filePath)}`);
    console.log(`Content preview: ${result.content.substring(0, 200)}...`);
  })
  .catch(error => {
    console.error(`Error: ${error.message}`);
  });
```

### PHP

```php
<?php
// Example of uploading a file using PHP

function uploadFile($apiBaseUrl, $apiKey, $filePath) {
    $url = $apiBaseUrl . '/upload';
    
    // Create cURL resource
    $ch = curl_init();
    
    // Setup request
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    // Set headers
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $apiKey
    ]);
    
    // Create file field
    $cFile = new CURLFile($filePath);
    $postFields = ['files[]' => $cFile];
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
    
    // Execute request
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    // Close cURL resource
    curl_close($ch);
    
    // Process response
    if ($httpCode === 200) {
        return json_decode($response, true);
    } else {
        throw new Exception('Upload failed: ' . $response);
    }
}

// Example usage
$apiBaseUrl = 'https://your-server-address/api';
$apiKey = 'your_api_key';
$filePath = 'path/to/document.pdf';

try {
    $result = uploadFile($apiBaseUrl, $apiKey, $filePath);
    echo "Upload successful. Document ID: " . $result['documents'][0]['id'] . "\n";
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

## Webhook Integration

If the File Conversion System supports webhooks, you can register a webhook URL to receive notifications when document processing is complete.

### Registering a Webhook (Python Example)

```python
import requests

def register_webhook(api_base_url, api_key, webhook_url, events=None):
    """
    Register a webhook to receive notifications.
    
    Args:
        api_base_url (str): Base URL of the API
        api_key (str): Your API key
        webhook_url (str): URL to receive webhook notifications
        events (list, optional): List of events to subscribe to
        
    Returns:
        dict: API response
    """
    url = f"{api_base_url}/webhooks"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "url": webhook_url,
        "events": events or ["document.completed", "document.error"]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Example usage
api_base_url = "https://your-server-address/api"
api_key = "your_api_key"
webhook_url = "https://your-application.com/webhooks/file-conversion"

result = register_webhook(api_base_url, api_key, webhook_url)
print(result)
```

### Processing Webhook Notifications (Node.js Example)

```javascript
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// Webhook endpoint
app.post('/webhooks/file-conversion', (req, res) => {
  const event = req.body;
  
  console.log('Received webhook:', event);
  
  // Process different event types
  switch (event.type) {
    case 'document.completed':
      console.log(`Document ${event.document_id} processing completed`);
      // Fetch the document content or notify users
      break;
      
    case 'document.error':
      console.log(`Document ${event.document_id} processing failed: ${event.error_message}`);
      // Handle the error
      break;
      
    default:
      console.log(`Unknown event type: ${event.type}`);
  }
  
  // Acknowledge receipt of the webhook
  res.status(200).send({ received: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Webhook server listening on port ${PORT}`);
});
```

## Error Handling Best Practices

When integrating with the File Conversion System API, implement proper error handling:

1. **Retry Logic**: Implement exponential backoff for transient errors
2. **Timeout Handling**: Set appropriate timeouts for API requests
3. **Validation**: Validate input parameters before making API calls
4. **Logging**: Log API responses for debugging
5. **User Feedback**: Provide meaningful error messages to users

## Additional Resources

- [API Integration Guide](api_integration_guide.md)
- [API Reference](api_reference.md)
- [Authentication Guide](authentication_guide.md)
