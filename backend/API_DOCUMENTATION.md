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

### 7. Popular Papers (NEW)
```
GET /api/popular
```
Get the most popular chunks based on usage tracking.

**Response:**
```json
{
  "popular_chunks": [
    {
      "chunk_id": "mucuna_01_intro",
      "usage_count": 15,
      "last_accessed": "2024-01-15",
      "source_doc_id": "extension_brief_mucuna.pdf"
    }
  ]
}
```

### 8. Analytics (NEW)
```
GET /api/analytics
```
Get comprehensive usage analytics and statistics.

**Response:**
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

## Environment Variables
- `OPENAI_API_KEY`: Required for paper comparison functionality
- `OPENAI_CHAT_MODEL`: Chat model to use for summaries and comparisons (default: "gpt-3.5-turbo")
- `OPENAI_MODEL`: Embedding model for similarity search (default: "text-embedding-ada-002")
- `CHROMA_DB_PATH`: Path to ChromaDB storage
- `CHROMA_COLLECTION_NAME`: Collection name for vector storage
- `REDIS_HOST`: Redis server host (default: "localhost")
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_DB`: Redis database number (default: 2)

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