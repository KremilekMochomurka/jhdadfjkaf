# Authentication Guide

This guide explains how to authenticate with the File Conversion System API.

## Authentication Methods

The File Conversion System supports the following authentication methods:

### 1. Session-Based Authentication (Web Interface)

When accessing the API from the web interface, authentication is handled through browser sessions. This is the default authentication method when using the system through a web browser.

### 2. API Key Authentication (For Integration)

For programmatic access and integration with other applications, API key authentication is recommended.

## Obtaining an API Key

To obtain an API key for integration:

1. Log in to the File Conversion System web interface
2. Navigate to the Settings section
3. Select the "API Access" tab
4. Click "Generate New API Key"
5. Copy and securely store your API key

**Important**: Treat your API key as a sensitive credential. Do not share it or commit it to version control systems.

## Using API Key Authentication

To authenticate API requests, include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

Replace `YOUR_API_KEY` with your actual API key.

### Example Request with API Key

```bash
curl -X GET "https://your-server-address/api/documents" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Error Responses

If authentication fails, the API will respond with a 401 Unauthorized status code:

```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API key"
}
```

## API Key Management

### Regenerating API Keys

If you believe your API key has been compromised, you should regenerate it immediately:

1. Log in to the File Conversion System web interface
2. Navigate to the Settings section
3. Select the "API Access" tab
4. Click "Regenerate API Key"
5. Confirm the action

**Note**: Regenerating an API key will invalidate the previous key. You will need to update any applications or services that use the API key.

### Revoking API Keys

To revoke an API key:

1. Log in to the File Conversion System web interface
2. Navigate to the Settings section
3. Select the "API Access" tab
4. Click "Revoke API Key"
5. Confirm the action

## Best Practices

1. **Secure Storage**: Store API keys securely, such as in environment variables or a secure credential store
2. **Least Privilege**: Use API keys with the minimum required permissions
3. **Regular Rotation**: Rotate API keys periodically as part of your security practices
4. **Monitoring**: Monitor API key usage for suspicious activity
5. **HTTPS**: Always use HTTPS for API requests to ensure credentials are encrypted in transit

## Future Authentication Methods

The system may support additional authentication methods in future releases, such as:

- OAuth 2.0
- JWT (JSON Web Tokens)
- SAML integration

Check the documentation for updates on supported authentication methods.
