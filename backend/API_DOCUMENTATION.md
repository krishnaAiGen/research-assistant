# Research Assistant API Documentation

## Overview
The Research Assistant API provides endpoints for uploading research papers, performing semantic similarity searches, retrieving documents, and comparing papers using AI-powered analysis.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
```
GET /
```
Returns API health status.

### 2. Upload Papers
```
PUT /api/upload
```
Upload research papers for processing and indexing.

**Request Body:**
```json
{
  "chunks": [...],  // Optional: Direct chunks
  "file_path": "path/to/file.json",  // Optional: File path or URL
  "schema_version": "1.0"  // Required: Schema version
}
```

### 3. Similarity Search
```
POST /api/similarity_search
```
Perform semantic search across uploaded papers.

**Request Body:**
```json
{
  "query": "search query",
  "k": 10,  // Number of results
  "min_score": 0.25  // Minimum similarity score
}
```

### 4. Get Document
```
GET /api/{source_doc_id}
```
Retrieve a specific document by its source_doc_id.

### 5. Compare Papers (NEW)
```
POST /api/compare
```
Compare two research papers and generate summaries plus comparison analysis.

**Request Body:**
```json
{
  "source_doc_id_1": "paper1_id",
  "source_doc_id_2": "paper2_id"
}
```

**Response:**
```json
{
  "paper1_summary": {
    "source_doc_id": "paper1_id",
    "journal": "Journal Name",
    "publish_year": 2023,
    "total_chunks": 15,
    "summary": "AI-generated summary of paper 1...",
    "doi": "10.1234/example"
  },
  "paper2_summary": {
    "source_doc_id": "paper2_id",
    "journal": "Another Journal",
    "publish_year": 2024,
    "total_chunks": 12,
    "summary": "AI-generated summary of paper 2...",
    "doi": "10.5678/example"
  },
  "comparison": "Detailed AI-generated comparison between the two papers...",
  "request_info": {
    "requested_papers": ["paper1_id", "paper2_id"],
    "processing_time": "Generated summaries and comparison using OpenAI",
    "model_used": "gpt-4"
  }
}
```

### 6. Statistics
```
GET /api/stats
```
Get vector store statistics.

## Environment Variables
- `OPENAI_API_KEY`: Required for paper comparison functionality
- `OPENAI_CHAT_MODEL`: Chat model to use for summaries and comparisons (default: "gpt-3.5-turbo")
- `OPENAI_MODEL`: Embedding model for similarity search (default: "text-embedding-ada-002")
- `CHROMA_DB_PATH`: Path to ChromaDB storage
- `CHROMA_COLLECTION_NAME`: Collection name for vector storage

## Error Handling
All endpoints return appropriate HTTP status codes:
- 200: Success
- 202: Accepted (for async operations)
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

## Usage Examples

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

## Notes
- The comparison endpoint uses OpenAI's GPT-4 model by default
- Text is limited to 15,000 characters per paper to avoid token limits
- Summaries are generated to be 300-500 words
- Comparison analysis covers methodology, findings, and research context