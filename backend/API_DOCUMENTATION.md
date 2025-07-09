# Research Assistant API Documentation

## Overview
The Research Assistant API provides endpoints for uploading research papers, performing semantic similarity searches, retrieving documents, and comparing papers using AI-powered analysis.

**Authentication**: Some endpoints require JWT token authentication with role-based access control.

## ⚠️ Important: API Usage Workflow

**Before using any search or analysis features, you MUST follow this sequence:**

1. **Get Authentication Token**: Use `/api/auth/token` to generate a JWT token with admin role
2. **Upload Data First**: Use `/api/upload` with the token to upload research papers and create embeddings
3. **Use Other APIs**: Only after uploading data can you use search, comparison, and analytics features

**Why this sequence is required:**
- The vector database starts empty
- Search APIs (`/api/similarity_search`) will return no results without uploaded data
- Comparison APIs (`/api/compare`) need existing documents to compare
- Analytics APIs (`/api/analytics`) track usage of uploaded documents

### Quick Start Example:
```bash
# Step 1: Get token
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "admin", "role": "admin"}'

# Step 2: Upload data (replace YOUR_TOKEN_HERE with actual token)
curl -X PUT "http://localhost:8000/api/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "path/to/papers.json", "schema_version": "1.0"}'

# Step 3: Now you can search
curl -X POST "http://localhost:8000/api/similarity_search" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "k": 5}'
```

## Base URL
```
http://localhost:8000
```

## Authentication

### JWT Token Authentication
Protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### User Roles & Permissions
- **`admin`**: Full access - can upload, view analytics, and access popular papers
- **`analytics`**: Can view analytics and popular papers
- **`user`**: Basic access to search and document retrieval (no special permissions for protected endpoints)

### Getting a Token
```
POST /api/auth/token
```

**Request Body:**
```json
{
  "user_id": "your_user_id",
  "role": "admin"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "your_user_id",
  "role": "admin",
  "permissions": ["upload", "analytics", "popular"]
}
```

## API Endpoints

### 1. Health Check
```
GET /
```
**Authentication**: None required

**Request**: No parameters required

**Response (200 OK):**
```json
{
  "message": "Research Assistant API is running",
  "status": "healthy"
}
```

---

### 2. Generate Authentication Token
```
POST /api/auth/token
```
**Authentication**: None required

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "user_id": "string",     // Required: User identifier
  "role": "string"         // Required: One of "admin", "analytics", "user"
}
```

**Request Body Example:**
```json
{
  "user_id": "admin_user_123",
  "role": "admin"
}
```

**Response (200 OK):**
```json
{
  "access_token": "string",      // JWT token for authentication
  "token_type": "bearer",        // Always "bearer"
  "expires_in": 86400,          // Token expiration in seconds
  "user_id": "string",          // User identifier
  "role": "string",             // User role
  "permissions": ["string"]     // Array of permissions
}
```

**Response Example:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdF9hZG1pbl91c2VyIiwicm9sZSI6ImFkbWluIiwicGVybWlzc2lvbnMiOlsidXBsb2FkIiwiYW5hbHl0aWNzIiwicG9wdWxhciJdLCJleHAiOjE3MjA1MjEzMTYsImlhdCI6MTcyMDQzNDkxNn0.example",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "admin_user_123",
  "role": "admin",
  "permissions": ["upload", "analytics", "popular"]
}
```

**Error Responses:**
- **400 Bad Request**: Invalid role
- **500 Internal Server Error**: Token generation failed

---

### 3. Database Statistics
```
GET /api/stats
```
**Authentication**: None required

**Note**: This endpoint shows database statistics including total chunks count. It will show 0 chunks if no data has been uploaded yet.

**Request**: No parameters required

**Response (200 OK):**
```json
{
  "total_chunks": "integer",        // Total number of chunks in database
  "collection_name": "string"       // ChromaDB collection name
}
```

**Response Example:**
```json
{
  "total_chunks": 25,
  "collection_name": "journal_chunks"
}
```

---

### 4. Upload Papers 🔒
```
PUT /api/upload
```
**Authentication**: Required (admin role)

**Request Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body (Option 1 - Direct Chunks):**
```json
{
  "chunks": [
    {
      "id": "string",                    // Required: Unique chunk identifier
      "source_doc_id": "string",         // Required: Source document ID
      "chunk_index": "integer",          // Required: Position in document
      "section_heading": "string",       // Required: Section title
      "journal": "string",               // Required: Journal name
      "publish_year": "integer",         // Required: Publication year
      "usage_count": "integer",          // Required: Usage count
      "attributes": ["string"],          // Required: Array of attributes/tags
      "link": "string",                  // Required: Source URL
      "text": "string",                  // Required: Content text
      "doi": "string"                    // Optional: DOI identifier
    }
  ],
  "schema_version": "string"             // Required: Schema version (e.g., "1.0")
}
```

**Request Body (Option 2 - File Path):**
```json
{
  "file_path": "string",          // Required: Local file path, URL, or Google Drive URL
  "schema_version": "string"      // Required: Schema version (e.g., "1.0")
}
```

**Request Body Examples:**

*Direct Chunks:*
```json
{
  "chunks": [
    {
      "id": "mucuna_01_intro",
      "source_doc_id": "extension_brief_mucuna.pdf",
      "chunk_index": 1,
      "section_heading": "Velvet bean description",
      "journal": "ILRI extension brief",
      "publish_year": 2016,
      "usage_count": 42,
      "attributes": ["Botanical description", "Morphology"],
      "link": "https://cgspace.cgiar.org/server/api/core/bitstreams/68bfaec0-8d32-4567-9133-7df9ec7f3e23/content",
      "text": "Velvet bean–Mucuna pruriens var. utilis, also known as mucuna—is a twining annual leguminous vine...",
      "doi": "10.1234/example.doi"
    }
  ],
  "schema_version": "1.0"
}
```

*Local File:*
```json
{
  "file_path": "/Users/username/Documents/chunks.json",
  "schema_version": "1.0"
}
```

*URL:*
```json
{
  "file_path": "https://example.com/sample_chunks.json",
  "schema_version": "1.0"
}
```

*Google Drive:*
```json
{
  "file_path": "https://drive.google.com/file/d/1ABC123DEF456/view?usp=sharing",
  "schema_version": "1.0"
}
```

**Response (202 Accepted):**
```json
{
  "message": "string",              // Upload status message
  "status": "accepted",             // Always "accepted"
  "processing_type": "string"       // Type: "direct_chunks", "local_file", "url", "google_drive_url"
}
```

**Response Examples:**
```json
{
  "message": "Direct chunks accepted for processing (15 chunks) with schema v1.0",
  "status": "accepted",
  "processing_type": "direct_chunks"
}
```

**Error Responses:**
- **400 Bad Request**: Missing required fields or validation errors
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Insufficient permissions (not admin)
- **500 Internal Server Error**: Upload processing failed

---

### 5. Similarity Search
```
POST /api/similarity_search
```
**Authentication**: None required

**⚠️ Prerequisites**: You must first upload data using `/api/upload` endpoint. This endpoint will return empty results if no data has been uploaded to the vector database.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "string",           // Required: Natural language search query
  "k": "integer",             // Optional: Number of results (1-100, default: 10)
  "min_score": "float"        // Optional: Minimum similarity score (0.0-1.0, default: 0.25)
}
```

**Request Body Example:**
```json
{
  "query": "What is velvet bean cultivation?",
  "k": 5,
  "min_score": 0.3
}
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "string",                    // Chunk identifier
      "source_doc_id": "string",         // Source document ID
      "chunk_index": "integer",          // Position in document
      "section_heading": "string",       // Section title
      "journal": "string",               // Journal name
      "publish_year": "integer",         // Publication year
      "usage_count": "integer",          // Usage count
      "attributes": ["string"],          // Array of attributes/tags
      "link": "string",                  // Source URL
      "text": "string",                  // Content text
      "score": "float",                  // Similarity score (0.0-1.0)
      "doi": "string"                    // DOI identifier (nullable)
    }
  ],
  "total_results": "integer",            // Number of results returned
  "query": "string"                      // Original search query
}
```

**Response Example:**
```json
{
  "results": [
    {
      "id": "mucuna_01_intro",
      "source_doc_id": "extension_brief_mucuna.pdf",
      "chunk_index": 1,
      "section_heading": "Velvet bean description",
      "journal": "ILRI extension brief",
      "publish_year": 2016,
      "usage_count": 42,
      "attributes": ["Botanical description", "Morphology"],
      "link": "https://cgspace.cgiar.org/server/api/core/bitstreams/68bfaec0-8d32-4567-9133-7df9ec7f3e23/content",
      "text": "Velvet bean–Mucuna pruriens var. utilis, also known as mucuna—is a twining annual leguminous vine...",
      "score": 0.85,
      "doi": "10.1234/example.doi"
    }
  ],
  "total_results": 1,
  "query": "What is velvet bean cultivation?"
}
```

**Error Responses:**
- **400 Bad Request**: Invalid query parameters
- **500 Internal Server Error**: Search processing failed

---

### 6. Get Document
```
GET /api/{source_doc_id}
```
**Authentication**: None required

**⚠️ Prerequisites**: You must first upload documents using `/api/upload` endpoint. This endpoint will return 404 if the document hasn't been uploaded.

**Path Parameters:**
- `source_doc_id` (string): The source document identifier

**Request Example:**
```
GET /api/extension_brief_mucuna.pdf
```

**Response (200 OK):**
```json
{
  "source_doc_id": "string",            // Source document ID
  "journal": "string",                  // Journal name
  "publish_year": "integer",            // Publication year
  "total_chunks": "integer",            // Number of chunks in document
  "chunks": [
    {
      "id": "string",                    // Chunk identifier
      "source_doc_id": "string",         // Source document ID
      "chunk_index": "integer",          // Position in document
      "section_heading": "string",       // Section title
      "journal": "string",               // Journal name
      "publish_year": "integer",         // Publication year
      "usage_count": "integer",          // Usage count
      "attributes": ["string"],          // Array of attributes/tags
      "link": "string",                  // Source URL
      "text": "string",                  // Content text
      "doi": "string",                   // DOI identifier (nullable)
      "schema_version": "string"         // Schema version
    }
  ],
  "metadata": {
    "journal": "string",                 // Journal name
    "publish_year": "integer",           // Publication year
    "total_chunks": "integer",           // Number of chunks
    "source_doc_id": "string",           // Source document ID
    "doi": "string"                      // DOI identifier (nullable)
  }
}
```

**Response Example:**
```json
{
  "source_doc_id": "extension_brief_mucuna.pdf",
  "journal": "ILRI extension brief",
  "publish_year": 2016,
  "total_chunks": 10,
  "chunks": [
    {
      "id": "mucuna_01_intro",
      "source_doc_id": "extension_brief_mucuna.pdf",
      "chunk_index": 1,
      "section_heading": "Velvet bean description",
      "journal": "ILRI extension brief",
      "publish_year": 2016,
      "usage_count": 42,
      "attributes": ["Botanical description", "Morphology"],
      "link": "https://cgspace.cgiar.org/server/api/core/bitstreams/68bfaec0-8d32-4567-9133-7df9ec7f3e23/content",
      "text": "Velvet bean–Mucuna pruriens var. utilis...",
      "doi": "10.1234/example.doi",
      "schema_version": "1.0"
    }
  ],
  "metadata": {
    "journal": "ILRI extension brief",
    "publish_year": 2016,
    "total_chunks": 10,
    "source_doc_id": "extension_brief_mucuna.pdf",
    "doi": "10.1234/example.doi"
  }
}
```

**Error Responses:**
- **404 Not Found**: Document with specified ID not found
- **500 Internal Server Error**: Document retrieval failed

---

### 7. Compare Papers
```
POST /api/compare
```
**Authentication**: None required

**⚠️ Prerequisites**: You must first upload documents using `/api/upload` endpoint. Both papers must exist in the database before comparison.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "source_doc_id_1": "string",     // Required: First paper's source document ID
  "source_doc_id_2": "string"      // Required: Second paper's source document ID
}
```

**Request Body Example:**
```json
{
  "source_doc_id_1": "extension_brief_mucuna.pdf",
  "source_doc_id_2": "1706.03762v7.pdf"
}
```

**Response (200 OK):**
```json
{
  "paper1_summary": {
    "source_doc_id": "string",       // Paper 1 source document ID
    "journal": "string",             // Paper 1 journal name
    "publish_year": "integer",       // Paper 1 publication year
    "total_chunks": "integer",       // Paper 1 number of chunks
    "summary": "string",             // AI-generated summary of paper 1
    "doi": "string"                  // Paper 1 DOI (nullable)
  },
  "paper2_summary": {
    "source_doc_id": "string",       // Paper 2 source document ID
    "journal": "string",             // Paper 2 journal name
    "publish_year": "integer",       // Paper 2 publication year
    "total_chunks": "integer",       // Paper 2 number of chunks
    "summary": "string",             // AI-generated summary of paper 2
    "doi": "string"                  // Paper 2 DOI (nullable)
  },
  "comparison": "string",            // AI-generated comparison analysis
  "request_info": {
    "requested_papers": ["string"],  // Array of requested paper IDs
    "processing_time": "string",     // Processing description
    "model_used": "string"           // OpenAI model used
  }
}
```

**Response Example:**
```json
{
  "paper1_summary": {
    "source_doc_id": "extension_brief_mucuna.pdf",
    "journal": "ILRI extension brief",
    "publish_year": 2016,
    "total_chunks": 10,
    "summary": "This paper provides a comprehensive guide to velvet bean cultivation...",
    "doi": "10.1234/example.doi"
  },
  "paper2_summary": {
    "source_doc_id": "1706.03762v7.pdf",
    "journal": "arXiv preprint",
    "publish_year": 2017,
    "total_chunks": 45,
    "summary": "This paper introduces the Transformer architecture for neural machine translation...",
    "doi": null
  },
  "comparison": "These two papers address completely different domains. The first focuses on agricultural practices for velvet bean cultivation, while the second presents a breakthrough in neural network architecture...",
  "request_info": {
    "requested_papers": ["extension_brief_mucuna.pdf", "1706.03762v7.pdf"],
    "processing_time": "Generated summaries and comparison using OpenAI",
    "model_used": "gpt-3.5-turbo"
  }
}
```

**Error Responses:**
- **400 Bad Request**: Missing required fields
- **404 Not Found**: One or both papers not found
- **500 Internal Server Error**: Comparison processing failed

---

### 8. Popular Papers 🔒
```
GET /api/popular
```
**Authentication**: Required (admin or analytics role)

**⚠️ Prerequisites**: You must first upload documents using `/api/upload` endpoint. This endpoint tracks usage of uploaded documents.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request**: No parameters required

**Response (200 OK):**
```json
{
  "popular_chunks": [
    {
      "chunk_id": "string",            // Chunk identifier
      "usage_count": "integer",        // Number of times accessed
      "last_accessed": "string",       // Last access date (YYYY-MM-DD)
      "source_doc_id": "string"        // Source document ID
    }
  ]
}
```

**Response Example:**
```json
{
  "popular_chunks": [
    {
      "chunk_id": "mucuna_01_intro",
      "usage_count": 15,
      "last_accessed": "2024-01-15",
      "source_doc_id": "extension_brief_mucuna.pdf"
    },
    {
      "chunk_id": "transformer_attention",
      "usage_count": 12,
      "last_accessed": "2024-01-15",
      "source_doc_id": "1706.03762v7.pdf"
    }
  ]
}
```

**Error Responses:**
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Insufficient permissions
- **500 Internal Server Error**: Analytics retrieval failed

---

### 9. Analytics 🔒
```
GET /api/analytics
```
**Authentication**: Required (admin or analytics role)

**⚠️ Prerequisites**: You must first upload documents using `/api/upload` endpoint. This endpoint provides analytics on uploaded document usage.

**Request Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request**: No parameters required

**Response (200 OK):**
```json
{
  "total_chunks_accessed": "integer",   // Number of unique chunks accessed
  "total_accesses": "integer",          // Sum of all access counts
  "most_popular": [
    {
      "chunk_id": "string",             // Chunk identifier
      "usage_count": "integer",         // Number of times accessed
      "last_accessed": "string",        // Last access date (YYYY-MM-DD)
      "source_doc_id": "string"         // Source document ID
    }
  ],
  "recent_activity": [
    {
      "chunk_id": "string",             // Chunk identifier
      "usage_count": "integer",         // Number of times accessed
      "last_accessed": "string",        // Last access date (YYYY-MM-DD)
      "source_doc_id": "string"         // Source document ID
    }
  ]
}
```

**Response Example:**
```json
{
  "total_chunks_accessed": 25,
  "total_accesses": 150,
  "most_popular": [
    {
      "chunk_id": "mucuna_01_intro",
      "usage_count": 15,
      "last_accessed": "2024-01-15",
      "source_doc_id": "extension_brief_mucuna.pdf"
    },
    {
      "chunk_id": "transformer_attention",
      "usage_count": 12,
      "last_accessed": "2024-01-15",
      "source_doc_id": "1706.03762v7.pdf"
    }
  ],
  "recent_activity": [
    {
      "chunk_id": "transformer_attention",
      "usage_count": 8,
      "last_accessed": "2024-01-15",
      "source_doc_id": "1706.03762v7.pdf"
    }
  ]
}
```

#### Analytics Metrics Explained:

**`total_chunks_accessed`** = **Unique chunks**
- **What it counts**: The number of different/unique chunks that have been accessed at least once
- **Example**: If you access chunks A, B, C, D, E → `total_chunks_accessed = 5`

**`total_accesses`** = **Total interactions**
- **What it counts**: The sum of all usage counts across all chunks (total interactions)
- **Example**: If chunk A was accessed 3 times, chunk B was accessed 2 times, and chunks C, D, E were accessed 1 time each → `total_accesses = 3 + 2 + 1 + 1 + 1 = 8`

**Real-world Example:**
```json
Usage data:
[
  {"chunk_id": "chunk_A", "usage_count": 5},
  {"chunk_id": "chunk_B", "usage_count": 3},
  {"chunk_id": "chunk_C", "usage_count": 2},
  {"chunk_id": "chunk_D", "usage_count": 1}
]

Results:
- total_chunks_accessed: 4 (4 unique chunks accessed)
- total_accesses: 11 (5 + 3 + 2 + 1 = 11 total interactions)
```

**Analytics Insights:**
- **High accesses, low chunks**: Users repeatedly access the same popular content
- **Similar numbers**: Users explore diverse content without much repetition
- **Growing gap**: Some content is very popular while other content gets occasional access

This helps understand both the **breadth** (diversity) and **depth** (intensity) of content usage patterns.

**Error Responses:**
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Insufficient permissions
- **500 Internal Server Error**: Analytics retrieval failed

---

## Environment Variables
- `OPENAI_API_KEY`: Required for paper comparison functionality
- `OPENAI_CHAT_MODEL`: Chat model to use for summaries and comparisons (default: "gpt-3.5-turbo")
- `OPENAI_MODEL`: Embedding model for similarity search (default: "text-embedding-ada-002")
- `CHROMA_DB_PATH`: Path to ChromaDB storage
- `CHROMA_COLLECTION_NAME`: Collection name for vector storage
- `REDIS_HOST`: Redis server host (default: "localhost")
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_DB`: Redis database number (default: 2)
- `JWT_SECRET_KEY`: Secret key for JWT token signing (required for auth)
- `JWT_EXPIRATION_HOURS`: Token expiration time in hours (default: 24)

## Error Handling
All endpoints return appropriate HTTP status codes:
- **200**: Success
- **202**: Accepted (for async operations)
- **400**: Bad Request (validation errors, missing fields)
- **401**: Unauthorized (missing or invalid token)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found (resource not found)
- **500**: Internal Server Error (server processing errors)

### Standard Error Response Format:
```json
{
  "error": "string",        // Error type
  "detail": "string"        // Detailed error message
}
```

## Authentication Examples

### Generate Admin Token
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "admin_user", "role": "admin"}'
```

### Access Protected Endpoint
```bash
# Get analytics with admin token
curl -X GET "http://localhost:8000/api/analytics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Upload with admin token
curl -X PUT "http://localhost:8000/api/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/file.json", "schema_version": "1.0"}'
```

## Usage Examples

### Complete Authentication Flow
```python
import requests

# 1. Generate token
token_response = requests.post("http://localhost:8000/api/auth/token", json={
    "user_id": "admin_user",
    "role": "admin"
})
token = token_response.json()["access_token"]

# 2. Use token for protected endpoints
headers = {"Authorization": f"Bearer {token}"}

# Get analytics
analytics = requests.get("http://localhost:8000/api/analytics", headers=headers)
print(analytics.json())

# Upload data
upload_data = {"file_path": "/path/to/file.json", "schema_version": "1.0"}
upload = requests.put("http://localhost:8000/api/upload", json=upload_data, headers=headers)
```

### Compare Two Papers
```python
import requests

compare_data = {
    "source_doc_id_1": "paper1.pdf",
    "source_doc_id_2": "paper2.pdf"
}

response = requests.post(
    "http://localhost:8000/api/compare",
    json=compare_data
)

if response.status_code == 200:
    result = response.json()
    print("Paper 1 Summary:", result['paper1_summary']['summary'])
    print("Paper 2 Summary:", result['paper2_summary']['summary'])
    print("Comparison:", result['comparison'])
```

## Testing Authentication

Run the authentication test script:
```bash
cd backend
python test_auth.py
```

This will test:
- Token generation for all roles
- Protected endpoint access with correct/incorrect tokens
- Public endpoint accessibility
- Invalid token handling

## Notes
- The comparison endpoint uses OpenAI's GPT-3.5-turbo model by default
- Text is limited to 15,000 characters per paper to avoid token limits
- Summaries are generated to be 300-500 words
- Comparison analysis covers methodology, findings, and research context
- JWT tokens expire after 24 hours by default
- Protected endpoints are marked with 🔒 in the documentation
- All request/response examples are provided in JSON format
- File uploads support local files, URLs, and Google Drive links
- Usage tracking is automatic for search and document retrieval endpoints