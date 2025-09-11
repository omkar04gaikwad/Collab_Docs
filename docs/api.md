# API Documentation

## Overview

This document describes the REST API and WebSocket endpoints for the Collaborative Document Editor. The API follows RESTful principles for document management and uses WebSockets for real-time collaboration.

## Base URL

```
Production: https://api.collaborative-docs.com/v1
Development: http://localhost:8000/v1
```

## Authentication

All API endpoints require authentication using JWT tokens.

### Headers
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Token Refresh
```http
POST /auth/refresh
```

## REST API Endpoints

### Authentication Endpoints

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "jwt_token_here",
  "refresh_token": "refresh_token_here"
}
```

#### Login User
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "jwt_token_here",
  "refresh_token": "refresh_token_here"
}
```

#### OAuth Login
```http
POST /auth/oauth/{provider}
```

**Providers:** `google`, `microsoft`, `github`

**Request Body:**
```json
{
  "code": "oauth_code",
  "state": "state_parameter"
}
```

### User Management

#### Get User Profile
```http
GET /users/me
```

**Response:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2024-01-01T00:00:00Z",
  "preferences": {
    "theme": "light",
    "language": "en",
    "notifications": true
  }
}
```

#### Update User Profile
```http
PUT /users/me
```

**Request Body:**
```json
{
  "name": "John Smith",
  "preferences": {
    "theme": "dark",
    "language": "en",
    "notifications": false
  }
}
```

### Document Management

#### Create Document
```http
POST /documents
```

**Request Body:**
```json
{
  "title": "My New Document",
  "content": "Initial content",
  "is_public": false,
  "tags": ["work", "important"]
}
```

**Response:**
```json
{
  "id": "doc_123",
  "title": "My New Document",
  "content": "Initial content",
  "owner_id": "user_123",
  "is_public": false,
  "tags": ["work", "important"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "version": 1,
  "collaborators": [
    {
      "user_id": "user_123",
      "permission": "owner",
      "joined_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Document
```http
GET /documents/{document_id}
```

**Response:**
```json
{
  "id": "doc_123",
  "title": "My Document",
  "content": "Document content",
  "owner_id": "user_123",
  "is_public": false,
  "tags": ["work"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "version": 15,
  "collaborators": [
    {
      "user_id": "user_123",
      "permission": "owner",
      "joined_at": "2024-01-01T00:00:00Z"
    },
    {
      "user_id": "user_456",
      "permission": "editor",
      "joined_at": "2024-01-01T01:00:00Z"
    }
  ],
  "permissions": {
    "can_edit": true,
    "can_comment": true,
    "can_share": true,
    "can_delete": true
  }
}
```

#### List Documents
```http
GET /documents
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `search`: Search term
- `tags`: Filter by tags (comma-separated)
- `sort`: Sort field (`created_at`, `updated_at`, `title`)
- `order`: Sort order (`asc`, `desc`)

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_123",
      "title": "My Document",
      "owner_id": "user_123",
      "is_public": false,
      "tags": ["work"],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "version": 15,
      "collaborator_count": 2
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

#### Update Document Metadata
```http
PUT /documents/{document_id}
```

**Request Body:**
```json
{
  "title": "Updated Title",
  "tags": ["work", "updated"],
  "is_public": true
}
```

#### Delete Document
```http
DELETE /documents/{document_id}
```

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

### Document Sharing

#### Share Document
```http
POST /documents/{document_id}/share
```

**Request Body:**
```json
{
  "email": "collaborator@example.com",
  "permission": "editor",
  "message": "Please review this document"
}
```

**Response:**
```json
{
  "share_link": "https://app.collaborative-docs.com/shared/doc_123/token_abc",
  "expires_at": "2024-01-08T00:00:00Z"
}
```

#### Update Collaborator Permission
```http
PUT /documents/{document_id}/collaborators/{user_id}
```

**Request Body:**
```json
{
  "permission": "viewer"
}
```

#### Remove Collaborator
```http
DELETE /documents/{document_id}/collaborators/{user_id}
```

### Document Versions

#### Get Document Versions
```http
GET /documents/{document_id}/versions
```

**Query Parameters:**
- `page`: Page number
- `limit`: Items per page

**Response:**
```json
{
  "versions": [
    {
      "version": 15,
      "created_at": "2024-01-01T00:00:00Z",
      "author_id": "user_123",
      "author_name": "John Doe",
      "changes": "Added new section",
      "snapshot_url": "/api/v1/documents/doc_123/versions/15/snapshot"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15,
    "pages": 1
  }
}
```

#### Restore Document Version
```http
POST /documents/{document_id}/versions/{version}/restore
```

**Response:**
```json
{
  "message": "Document restored to version 10",
  "current_version": 16
}
```

### Comments

#### Add Comment
```http
POST /documents/{document_id}/comments
```

**Request Body:**
```json
{
  "position": {
    "site_id": "user_123",
    "clock": 100,
    "path": [1, 2, 3]
  },
  "content": "This needs clarification",
  "parent_id": null
}
```

**Response:**
```json
{
  "id": "comment_123",
  "position": {
    "site_id": "user_123",
    "clock": 100,
    "path": [1, 2, 3]
  },
  "content": "This needs clarification",
  "author_id": "user_123",
  "author_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "resolved": false,
  "replies": []
}
```

#### Get Comments
```http
GET /documents/{document_id}/comments
```

#### Resolve Comment
```http
PUT /documents/{document_id}/comments/{comment_id}/resolve
```

### File Upload

#### Upload File
```http
POST /files/upload
```

**Request:** Multipart form data
- `file`: File to upload
- `document_id`: Target document ID

**Response:**
```json
{
  "id": "file_123",
  "filename": "image.jpg",
  "url": "https://cdn.collaborative-docs.com/files/file_123",
  "size": 1024000,
  "mime_type": "image/jpeg",
  "uploaded_at": "2024-01-01T00:00:00Z"
}
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket('wss://api.collaborative-docs.com/ws');
```

### Authentication

```json
{
  "type": "auth",
  "token": "jwt_token_here"
}
```

### Document Operations

#### Join Document
```json
{
  "type": "join_document",
  "document_id": "doc_123"
}
```

#### Leave Document
```json
{
  "type": "leave_document",
  "document_id": "doc_123"
}
```

#### Send Operation
```json
{
  "type": "operation",
  "document_id": "doc_123",
  "operation": {
    "op_type": "insert",
    "position": {
      "site_id": "user_123",
      "clock": 100,
      "path": [1, 2, 3]
    },
    "content": "Hello",
    "attributes": {
      "bold": true
    }
  }
}
```

#### Update Cursor Position
```json
{
  "type": "cursor_update",
  "document_id": "doc_123",
  "position": {
    "site_id": "user_123",
    "clock": 100,
    "path": [1, 2, 3]
  },
  "selection": {
    "start": {
      "site_id": "user_123",
      "clock": 100,
      "path": [1, 2, 3]
    },
    "end": {
      "site_id": "user_123",
      "clock": 105,
      "path": [1, 2, 8]
    }
  }
}
```

### WebSocket Events

#### Operation Received
```json
{
  "type": "operation_received",
  "document_id": "doc_123",
  "operation": {
    "op_type": "insert",
    "position": {
      "site_id": "user_456",
      "clock": 200,
      "path": [1, 2, 4]
    },
    "content": "World",
    "attributes": {}
  },
  "author_id": "user_456"
}
```

#### User Joined
```json
{
  "type": "user_joined",
  "document_id": "doc_123",
  "user": {
    "id": "user_456",
    "name": "Jane Doe",
    "avatar_url": "https://example.com/avatar.jpg"
  }
}
```

#### User Left
```json
{
  "type": "user_left",
  "document_id": "doc_123",
  "user_id": "user_456"
}
```

#### Cursor Update
```json
{
  "type": "cursor_update",
  "document_id": "doc_123",
  "user_id": "user_456",
  "position": {
    "site_id": "user_456",
    "clock": 200,
    "path": [1, 2, 4]
  },
  "selection": {
    "start": {
      "site_id": "user_456",
      "clock": 200,
      "path": [1, 2, 4]
    },
    "end": {
      "site_id": "user_456",
      "clock": 200,
      "path": [1, 2, 4]
    }
  }
}
```

#### Document State Sync
```json
{
  "type": "state_sync",
  "document_id": "doc_123",
  "operations": [
    {
      "op_type": "insert",
      "position": {
        "site_id": "user_123",
        "clock": 100,
        "path": [1, 2, 3]
      },
      "content": "Hello",
      "attributes": {}
    }
  ],
  "version": 15
}
```

#### Error Messages
```json
{
  "type": "error",
  "code": "INVALID_OPERATION",
  "message": "Operation is invalid or malformed",
  "document_id": "doc_123"
}
```

## Error Handling

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `422`: Unprocessable Entity
- `429`: Too Many Requests
- `500`: Internal Server Error

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_REQUIRED`: Authentication token missing or invalid
- `PERMISSION_DENIED`: User doesn't have required permissions
- `DOCUMENT_NOT_FOUND`: Document doesn't exist or user can't access it
- `OPERATION_CONFLICT`: CRDT operation conflict
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `UNSUPPORTED_FILE_TYPE`: File type not supported

## Rate Limiting

### Limits
- **Authentication**: 5 requests per minute
- **Document Operations**: 100 requests per minute
- **File Upload**: 10 requests per minute
- **WebSocket Connections**: 5 per user

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks

### Document Events
```http
POST /webhooks/document-events
```

**Events:**
- `document.created`
- `document.updated`
- `document.deleted`
- `document.shared`
- `document.commented`

**Payload:**
```json
{
  "event": "document.updated",
  "data": {
    "document_id": "doc_123",
    "user_id": "user_123",
    "changes": "Updated title and content",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## SDK Examples

### JavaScript/TypeScript
```typescript
import { CollaborativeDocsClient } from '@collaborative-docs/sdk';

const client = new CollaborativeDocsClient({
  apiUrl: 'https://api.collaborative-docs.com/v1',
  token: 'jwt_token_here'
});

// Create document
const doc = await client.documents.create({
  title: 'My Document',
  content: 'Initial content'
});

// Join real-time collaboration
const ws = client.websocket.joinDocument(doc.id);
ws.on('operation', (operation) => {
  // Handle incoming operations
});
```

### Python
```python
from collaborative_docs import Client

client = Client(
    api_url='https://api.collaborative-docs.com/v1',
    token='jwt_token_here'
)

# Create document
doc = client.documents.create({
    'title': 'My Document',
    'content': 'Initial content'
})

# Join real-time collaboration
ws = client.websocket.join_document(doc['id'])
ws.on_operation(lambda op: print(f"Received operation: {op}"))
```
