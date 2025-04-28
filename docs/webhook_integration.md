# Webhook Integration

This guide explains how to set up and use webhooks with the File Conversion System to receive real-time notifications about document processing events.

## What are Webhooks?

Webhooks are user-defined HTTP callbacks that are triggered by specific events in the File Conversion System. When an event occurs, the system sends an HTTP POST request to the URL configured for the webhook.

## Use Cases for Webhooks

Webhooks are useful for:

1. **Real-time notifications**: Get notified immediately when document processing completes
2. **Automation**: Trigger workflows in your application based on document events
3. **Asynchronous processing**: Build systems that don't need to poll the API for status updates
4. **Integration**: Connect the File Conversion System with other services and applications

## Supported Events

The File Conversion System supports the following webhook events:

| Event | Description |
|-------|-------------|
| `document.uploaded` | Triggered when a new document is uploaded |
| `document.processing` | Triggered when document processing begins |
| `document.completed` | Triggered when document processing completes successfully |
| `document.error` | Triggered when document processing fails |
| `document.deleted` | Triggered when a document is deleted |

## Setting Up Webhooks

### Prerequisites

To set up webhooks, you need:

1. A publicly accessible HTTPS endpoint on your server to receive webhook notifications
2. Authentication credentials for the File Conversion System API

### Registering a Webhook

To register a webhook, make a POST request to the `/webhooks` endpoint:

```
POST /api/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-application.com/webhooks/file-conversion",
  "events": ["document.completed", "document.error"],
  "description": "Notification endpoint for document processing events"
}
```

**Response:**
```json
{
  "id": "wh_123456",
  "url": "https://your-application.com/webhooks/file-conversion",
  "events": ["document.completed", "document.error"],
  "description": "Notification endpoint for document processing events",
  "created_at": "2023-06-15T10:30:00Z"
}
```

### Listing Registered Webhooks

To view all registered webhooks:

```
GET /api/webhooks
```

**Response:**
```json
{
  "webhooks": [
    {
      "id": "wh_123456",
      "url": "https://your-application.com/webhooks/file-conversion",
      "events": ["document.completed", "document.error"],
      "description": "Notification endpoint for document processing events",
      "created_at": "2023-06-15T10:30:00Z"
    }
  ]
}
```

### Updating a Webhook

To update an existing webhook:

```
PUT /api/webhooks/{webhook_id}
```

**Request Body:**
```json
{
  "url": "https://your-application.com/webhooks/new-endpoint",
  "events": ["document.completed", "document.error", "document.deleted"],
  "description": "Updated notification endpoint"
}
```

### Deleting a Webhook

To delete a webhook:

```
DELETE /api/webhooks/{webhook_id}
```

## Webhook Payload Format

When an event occurs, the File Conversion System sends an HTTP POST request to your webhook URL with a JSON payload.

### Example Payload for `document.completed` Event

```json
{
  "event": "document.completed",
  "timestamp": "2023-06-15T10:35:00Z",
  "data": {
    "document_id": 123,
    "filename": "important_document.pdf",
    "status": "completed",
    "processing_time_ms": 5200,
    "content_type": "pdf",
    "folder_id": 1
  }
}
```

### Example Payload for `document.error` Event

```json
{
  "event": "document.error",
  "timestamp": "2023-06-15T10:35:00Z",
  "data": {
    "document_id": 124,
    "filename": "corrupted_file.pdf",
    "status": "error",
    "error_message": "Failed to extract text from PDF: File is corrupted or password protected",
    "folder_id": 1
  }
}
```

## Handling Webhook Notifications

### Security Considerations

To ensure the security of your webhook endpoint:

1. **Verify the source**: Implement signature verification to ensure requests come from the File Conversion System
2. **Use HTTPS**: Always use HTTPS for your webhook endpoint
3. **Implement authentication**: Consider adding authentication to your webhook endpoint
4. **Validate the payload**: Verify the structure and content of the webhook payload

### Signature Verification

The File Conversion System signs webhook requests with a signature in the `X-Webhook-Signature` header. To verify this signature:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    """
    Verify the webhook signature.
    
    Args:
        payload (str): The raw request body
        signature (str): The signature from the X-Webhook-Signature header
        secret (str): Your webhook secret
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    computed_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)
```

### Responding to Webhooks

Your webhook endpoint should:

1. Process the webhook payload
2. Respond with a 200 OK status code to acknowledge receipt
3. Complete any processing asynchronously to avoid timeout issues

Example webhook handler in Node.js:

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');

const app = express();
app.use(bodyParser.json({
  verify: (req, res, buf) => {
    // Store the raw request body for signature verification
    req.rawBody = buf;
  }
}));

// Webhook secret (should match the one used by the File Conversion System)
const WEBHOOK_SECRET = 'your_webhook_secret';

// Webhook endpoint
app.post('/webhooks/file-conversion', (req, res) => {
  // Verify signature
  const signature = req.headers['x-webhook-signature'];
  const computedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(req.rawBody)
    .digest('hex');
    
  if (!crypto.timingSafeEqual(
    Buffer.from(computedSignature, 'hex'),
    Buffer.from(signature, 'hex')
  )) {
    return res.status(401).send('Invalid signature');
  }
  
  // Process the webhook
  const event = req.body;
  console.log('Received webhook:', event);
  
  // Acknowledge receipt immediately
  res.status(200).send({ received: true });
  
  // Process the event asynchronously
  processWebhookEvent(event).catch(error => {
    console.error('Error processing webhook:', error);
  });
});

async function processWebhookEvent(event) {
  // Handle different event types
  switch (event.event) {
    case 'document.completed':
      await handleCompletedDocument(event.data);
      break;
      
    case 'document.error':
      await handleDocumentError(event.data);
      break;
      
    // Handle other event types...
  }
}

async function handleCompletedDocument(data) {
  // Implement your logic for completed documents
  console.log(`Document ${data.document_id} processing completed`);
  
  // Example: Fetch the document content
  // const documentContent = await fetchDocumentContent(data.document_id);
  
  // Example: Notify users
  // await notifyUsers(data.document_id, 'Document processing completed');
}

async function handleDocumentError(data) {
  // Implement your logic for document errors
  console.log(`Document ${data.document_id} processing failed: ${data.error_message}`);
  
  // Example: Log the error
  // await logDocumentError(data.document_id, data.error_message);
  
  // Example: Notify administrators
  // await notifyAdmins(data.document_id, data.error_message);
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Webhook server listening on port ${PORT}`);
});
```

## Webhook Best Practices

1. **Idempotency**: Design your webhook handler to be idempotent (able to receive the same webhook multiple times without side effects)
2. **Quick Response**: Respond to webhook requests quickly (within a few seconds) to avoid timeouts
3. **Retry Handling**: Be prepared to handle duplicate webhook deliveries due to retries
4. **Error Logging**: Log webhook processing errors for debugging
5. **Monitoring**: Monitor webhook deliveries and processing for reliability
6. **Testing**: Test your webhook endpoint with sample payloads before going live

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**
   - Check that the webhook URL is publicly accessible
   - Verify that the webhook is registered correctly
   - Check for any network issues or firewalls blocking incoming requests

2. **Signature verification failing**
   - Ensure you're using the correct webhook secret
   - Check that you're verifying the signature correctly
   - Verify that the raw request body is being used for signature verification

3. **Webhook timing out**
   - Ensure your webhook handler responds quickly
   - Move time-consuming processing to an asynchronous task

### Webhook Logs

The File Conversion System maintains logs of webhook deliveries. You can view these logs in the web interface or through the API:

```
GET /api/webhooks/{webhook_id}/deliveries
```

This endpoint returns a list of recent webhook delivery attempts, including status codes and response times.

## Additional Resources

- [API Integration Guide](api_integration_guide.md)
- [API Reference](api_reference.md)
- [Code Examples](code_examples.md)
