# Research Assistant API Documentation

A FastAPI-based research assistant that provides semantic search capabilities over scientific journal documents using OpenAI embeddings and ChromaDB vector storage.

## 🚀 Base URL
```
http://localhost:8000
```

## 📋 API Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/stats` | Get database statistics |
| PUT | `/api/upload` | Upload chunks or file for processing |
| POST | `/api/similarity_search` | Semantic search |
| GET | `/api/{journal_id}` | Get document by ID |

---

## 🔍 Detailed API Documentation

### 1. Health Check

**Endpoint:** `GET /`

**Description:** Check if the API is running and healthy.

**Request:**
```http
GET http://localhost:8000/
```

**Response:**
```json
{
  "message": "Research Assistant API is running",
  "status": "healthy"
}
```

---

### 2. Database Statistics

**Endpoint:** `GET /api/stats`

**Description:** Get statistics about the vector database.

**Request:**
```http
GET http://localhost:8000/api/stats
```

**Response:**
```json
{
  "total_chunks": 15,
  "collection_name": "journal_chunks"
}
```

---

### 3. Upload Data

**Endpoint:** `PUT /api/upload`

**Description:** Upload journal chunks for embedding generation and storage. Supports four input methods:
- Direct chunks in request body
- Local file path (absolute paths required)
- HTTP/HTTPS URL
- Google Drive sharing URL (automatically converted to direct download)

**Important Notes:**
- **schema_version is REQUIRED** for all upload requests
- Processing happens asynchronously in the background
- Returns 202 Accepted immediately
- Wait 5-10 seconds after upload before searching
- For file uploads, temporary files are automatically cleaned up

**Headers:**
```
Content-Type: application/json
```

#### Method 1: Direct Chunks

**Request Body:**
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
      "text": "Velvet bean–Mucuna pruriens var. utilis, also known as mucuna—is a twining annual leguminous vine common to most parts of the tropics...",
      "doi": "10.1234/example.doi"
    }
  ],
  "schema_version": "1.0"
}
```

**Response (202 Accepted):**
```json
{
  "message": "Direct chunks accepted for processing (15 chunks) with schema v1.0",
  "status": "accepted",
  "processing_type": "direct_chunks"
}
```

#### Method 2: Local File Path

**Important:** Must use absolute file paths (e.g., `/Users/username/Documents/chunks.json`)

**Request Body:**
```json
{
  "file_path": "/Users/krishnayadav/Downloads/Sample_chunks.json",
  "schema_version": "1.0"
}
```

**Response (202 Accepted):**
```json
{
  "message": "local file accepted for processing with schema v1.0",
  "status": "accepted",
  "processing_type": "local_file"
}
```

#### Method 3: HTTP/HTTPS URL

**Request Body:**
```json
{
  "file_path": "https://example.com/sample_chunks.json",
  "schema_version": "1.0"
}
```

**Response (202 Accepted):**
```json
{
  "message": "URL accepted for processing with schema v1.0",
  "status": "accepted",
  "processing_type": "url"
}
```

#### Method 4: Google Drive URL

**Supported URL formats:**
- `https://drive.google.com/file/d/FILE_ID/view?usp=sharing`
- `https://drive.google.com/open?id=FILE_ID`
- Other Google Drive sharing formats

**Request Body:**
```json
{
  "file_path": "https://drive.google.com/file/d/1ABC123DEF456/view?usp=sharing",
  "schema_version": "1.0"
}
```

**Response (202 Accepted):**
```json
{
  "message": "Google Drive URL accepted for processing with schema v1.0",
  "status": "accepted",
  "processing_type": "google_drive_url"
}
```

**Required Fields:**
- `schema_version` (string): **REQUIRED** - Version of the data schema being used
- Either `chunks` OR `file_path` (but not both)

**Chunk Schema:**
Each chunk must contain the following fields:
- `id` (string): Unique identifier
- `source_doc_id` (string): Source document ID
- `chunk_index` (integer): Position in document
- `section_heading` (string): Section title
- `journal` (string): Journal name
- `publish_year` (integer): Publication year
- `usage_count` (integer): Usage count
- `attributes` (array): List of attributes/tags
- `link` (string): Source URL
- `text` (string): Content text
- `doi` (string, optional): DOI identifier

---

### 4. Similarity Search

**Endpoint:** `POST /api/similarity_search`

**Description:** Perform semantic search to find chunks similar to a query using OpenAI embeddings.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "What is velvet bean?",
  "k": 5,
  "min_score": 0.25
}
```

**Parameters:**
- `query` (string): Natural language search query
- `k` (integer, 1-100): Number of results to return (default: 10)
- `min_score` (float, 0.0-1.0): Minimum similarity score (default: 0.25)

**Sample Queries:**
```json
{
  "query": "How to grow velvet bean?",
  "k": 3,
  "min_score": 0.3
}
```

```json
{
  "query": "What is attention mechanism in transformers?",
  "k": 5,
  "min_score": 0.25
}
```

```json
{
  "query": "Soil fertility and nitrogen fixation",
  "k": 10,
  "min_score": 0.2
}
```

**Response (200 OK):**
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
      "doi": "10.1234/example.doi",
      "schema_version": "1.0"
    }
  ],
  "total_results": 1,
  "query": "What is velvet bean?"
}
```

---

### 5. Get Document

**Endpoint:** `GET /api/{journal_id}`

**Description:** Retrieve all chunks and metadata for a specific document.

**Path Parameters:**
- `journal_id` (string): The source document ID (e.g., "extension_brief_mucuna.pdf")

**Request:**
```http
GET http://localhost:8000/api/extension_brief_mucuna.pdf
```

**Response (200 OK):**
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

**Available Documents:**
- `extension_brief_mucuna.pdf` - ILRI extension brief about velvet bean
- `1706.03762v7.pdf` - Transformer paper from arXiv

---

## 🔧 Error Responses

### 400 Bad Request
```json
{
  "detail": "Must provide either chunks or file_path"
}
```

### 404 Not Found
```json
{
  "detail": "Document with ID 'nonexistent.pdf' not found"
}
```

### 405 Method Not Allowed
```json
{
  "detail": "Method Not Allowed"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "schema_version"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "detail": "Error details here"
}
```

---

## 🧪 Testing Workflow

### 1. Basic Test Sequence
```bash
# 1. Check health
GET http://localhost:8000/

# 2. Upload sample data (schema_version required)
PUT http://localhost:8000/api/upload
# Body: {"chunks": [...], "schema_version": "1.0"}

# 3. Wait 5-10 seconds for background processing

# 4. Check stats to verify upload
GET http://localhost:8000/api/stats

# 5. Search for content
POST http://localhost:8000/api/similarity_search
# Body: {"query": "What is velvet bean?", "k": 5}

# 6. Get specific document
GET http://localhost:8000/api/extension_brief_mucuna.pdf
```

### 2. File Upload Test Sequence
```bash
# Local file (absolute path required)
PUT http://localhost:8000/api/upload
# Body: {"file_path": "/Users/username/Documents/chunks.json", "schema_version": "1.0"}

# URL
PUT http://localhost:8000/api/upload
# Body: {"file_path": "https://example.com/chunks.json", "schema_version": "1.0"}

# Google Drive
PUT http://localhost:8000/api/upload
# Body: {"file_path": "https://drive.google.com/file/d/FILE_ID/view", "schema_version": "1.0"}

# Always wait 5-10 seconds after upload before searching
```

### 3. Using the Test Script
```bash
cd backend
python test_api.py
```

---

## 🔑 Environment Setup

### Required Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=text-embedding-ada-002

# ChromaDB Configuration
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=journal_chunks

# FastAPI Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 🚀 Quick Start

### 1. Setup
```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env with your OpenAI API key
```

### 2. Start Server
```bash
python run.py
```

**Server Logs:**
- `INFO: Will watch for changes in these directories` - Normal uvicorn auto-reload message
- `INFO: Started server process` - Server is starting
- `INFO: Waiting for application startup` - Server is ready
- `Processing upload with schema version: 1.0` - Schema version logging

### 3. Test with Sample Data
```bash
python test_api.py
```

---

## 📊 Technical Details

### Schema Version
- **Purpose:** Track data format versions for compatibility
- **Storage:** Stored as metadata with each chunk
- **Retrieval:** Included in search results and document retrieval
- **Default:** "1.0" if not specified in existing data

### Embedding Model
- **Model:** OpenAI text-embedding-ada-002
- **Dimensions:** 1536
- **Max Input:** 8191 tokens
- **Cost:** ~$0.0001 per 1K tokens

### Vector Database
- **Database:** ChromaDB
- **Storage:** Persistent local storage in `./chroma_db/`
- **Distance Metric:** L2 distance (converted to similarity score)
- **Similarity Score:** 0.0 to 1.0 (higher = more similar)

### Processing
- **Background Tasks:** Async processing for all uploads
- **Batch Processing:** Efficient batch embedding generation
- **Auto Cleanup:** Temporary downloaded files automatically deleted
- **File Support:** JSON files with chunk arrays
- **URL Handling:** Smart detection and conversion (especially Google Drive)
- **Schema Tracking:** Version information stored with each chunk

### Performance
- **Concurrent Uploads:** Multiple uploads can be processed simultaneously
- **Memory Efficient:** Streaming file downloads for large files
- **Error Resilient:** Comprehensive error handling and logging

---

## 🔄 Data Management

### Reset Vector Database
```bash
# Stop the server (Ctrl+C)
cd backend
rm -rf chroma_db/
python run.py  # Restart server
```

### Backup Database
```bash
# Copy the entire chroma_db directory
cp -r chroma_db/ chroma_db_backup/
```

### View Database Contents
```bash
# Check collection stats
GET http://localhost:8000/api/stats

# List all documents (use similarity search with broad query)
POST http://localhost:8000/api/similarity_search
# Body: {"query": "document", "k": 100, "min_score": 0.0}
```

---

## 🛠️ Troubleshooting

### Common Issues

1. **"schema_version field required" Error**
   - Always include `schema_version` in upload requests
   - Use "1.0" as default version

2. **"Method Not Allowed" Error**
   - Check HTTP method (PUT for upload, POST for search)
   - Ensure correct endpoint URL

3. **"File not found" Error**
   - Use absolute file paths for local files
   - Verify file exists and is readable

4. **Empty Search Results**
   - Wait 5-10 seconds after upload for processing
   - Check if chunks were uploaded using `/api/stats`
   - Lower `min_score` parameter

5. **Google Drive Download Issues**
   - Ensure file is publicly accessible
   - Check if sharing is enabled
   - Try direct download URL format

6. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check API quota and billing
   - Ensure text chunks are not too long

### Debug Mode
When `DEBUG=True` in environment:
- Auto-reload enabled (server restarts on code changes)
- Detailed logging and error messages
- File watching enabled
- Schema version logging in console

---

## 📝 Notes

- **schema_version is REQUIRED** for all upload requests
- Upload processing is always asynchronous (202 Accepted response)
- Similarity scores are computed from L2 distance: `score = 1 / (1 + distance)`
- Google Drive URLs are automatically converted to direct download format
- Local files are read directly without temporary copies
- Only downloaded files from URLs are automatically cleaned up
- ChromaDB may show duplicate ID warnings on re-uploads (this is normal)
- Server logs "Will watch for changes" message is normal uvicorn behavior in debug mode
- Schema version is stored with each chunk and returned in search results
- Existing data without schema_version will default to "1.0"

---

## 🔄 Migration Notes

### From Previous Versions
If you have existing data without schema_version:
1. Existing chunks will automatically get schema_version "1.0"
2. New uploads MUST include schema_version
3. All API responses now include schema_version field
4. No data migration required - handled automatically