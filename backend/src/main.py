from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import requests
import json
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from typing import List
from openai import OpenAI

try:
    from .models import (
        UploadRequest, UploadResponse, SimilaritySearchRequest, 
        SimilaritySearchResponse, JournalDocument, ErrorResponse,
        CompareRequest, CompareResponse, PaperSummary
    )
    from .embeddings import EmbeddingGenerator
    from .vector_store import ChromaVectorStore
except ImportError:
    from models import (
        UploadRequest, UploadResponse, SimilaritySearchRequest, 
        SimilaritySearchResponse, JournalDocument, ErrorResponse,
        CompareRequest, CompareResponse, PaperSummary
    )
    from embeddings import EmbeddingGenerator
    from vector_store import ChromaVectorStore

load_dotenv()

# Configure OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(
    title="Research Assistant API",
    description="AI-powered research assistant for scientific journal publishers",
    version="1.0.0"
)

# CORS configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
embedding_generator = EmbeddingGenerator()
vector_store = ChromaVectorStore()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Research Assistant API is running", "status": "healthy"}

@app.get("/api/stats")
async def get_stats():
    """Get vector store statistics"""
    stats = vector_store.get_collection_stats()
    return stats

@app.put("/api/upload", response_model=UploadResponse, status_code=202)
async def upload_chunks(request: UploadRequest, background_tasks: BackgroundTasks):
    """
    Upload journal chunks, local file path, or URL (including Google Drive), 
    generate embeddings, and store them in the vector database.
    Requires schema_version to be specified.
    Returns 202 Accepted as the processing happens asynchronously.
    """
    try:
        # Log the schema version being used
        print(f"Processing upload with schema version: {request.schema_version}")
        
        if request.chunks:
            # Direct chunks provided
            chunks_data = [chunk.dict() for chunk in request.chunks]
            chunks_count = len(request.chunks)
            
            # Add background task to process chunks with schema version
            background_tasks.add_task(process_chunks, chunks_data, request.schema_version)
            
            return UploadResponse(
                message=f"Direct chunks accepted for processing ({chunks_count} chunks) with schema v{request.schema_version}",
                status="accepted",
                processing_type="direct_chunks"
            )
            
        elif request.file_path:
            # File path provided - can be local file, URL, or Google Drive
            background_tasks.add_task(process_file_path, request.file_path, request.schema_version)
            
            # Determine file type for better messaging
            if request.file_path.startswith(('http://', 'https://')):
                if "drive.google.com" in request.file_path:
                    file_type = "Google Drive URL"
                    processing_type = "google_drive_url"
                else:
                    file_type = "URL"
                    processing_type = "url"
            else:
                file_type = "local file"
                processing_type = "local_file"
            
            return UploadResponse(
                message=f"{file_type} accepted for processing with schema v{request.schema_version}",
                status="accepted",
                processing_type=processing_type
            )
        
        else:
            raise HTTPException(status_code=400, detail="Must provide either chunks or file_path")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

async def process_chunks(chunks: List[dict], schema_version: str):
    """
    Background task to process chunks: generate embeddings and store in vector database
    """
    try:
        print(f"Processing {len(chunks)} chunks with schema version {schema_version}...")
        
        # Extract text content for embedding generation
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = embedding_generator.generate_embeddings_batch(texts)
        
        # Store in vector database
        print("Storing in vector database...")
        success = vector_store.add_chunks(chunks, embeddings, schema_version)
        
        if success:
            print(f"Successfully processed {len(chunks)} chunks with schema v{schema_version}")
        else:
            print("Failed to store chunks in vector database")
            
    except Exception as e:
        print(f"Error in background processing: {str(e)}")

def convert_google_drive_url(url: str) -> str:
    """
    Convert Google Drive sharing URL to direct download URL
    """
    if "drive.google.com" in url:
        # Extract file ID from various Google Drive URL formats
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
        else:
            # Try to extract from folders URL or other formats
            return url  # Return original if can't parse
        
        # Convert to direct download URL
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    return url

async def process_file_path(file_path: str, schema_version: str):
    """
    Background task to process file from local path, URL, or Google Drive
    """
    temp_file_path = None
    try:
        # Determine if it's a URL or local file path
        if file_path.startswith(('http://', 'https://')):
            # It's a URL - download the file
            print(f"Processing URL: {file_path} with schema version {schema_version}")
            
            # Convert Google Drive URLs to direct download URLs
            download_url = convert_google_drive_url(file_path)
            print(f"Download URL: {download_url}")
            
            # Download the file
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(download_url, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_file.write(response.text)
                temp_file_path = temp_file.name
            
            print(f"File downloaded to: {temp_file_path}")
            file_to_process = temp_file_path
            
        else:
            # It's a local file path
            print(f"Processing local file: {file_path} with schema version {schema_version}")
            
            # Check if file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Local file not found: {file_path}")
            
            file_to_process = file_path
        
        # Parse JSON content
        with open(file_to_process, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        # Validate that it's a list of chunks
        if not isinstance(chunks_data, list):
            raise ValueError("File must contain a JSON array of chunks")
        
        print(f"Found {len(chunks_data)} chunks in file")
        
        # Process the chunks
        await process_chunks(chunks_data, schema_version)
        
        print("File processing completed successfully")
        
    except requests.RequestException as e:
        print(f"Error downloading file: {str(e)}")
    except FileNotFoundError as e:
        print(f"File not found: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {str(e)}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
    finally:
        # Clean up temporary file (only if we downloaded it)
        if temp_file_path and Path(temp_file_path).exists():
            try:
                Path(temp_file_path).unlink()
                print(f"Temporary file deleted: {temp_file_path}")
            except Exception as e:
                print(f"Error deleting temporary file: {str(e)}")

@app.post("/api/similarity_search", response_model=SimilaritySearchResponse)
async def similarity_search(request: SimilaritySearchRequest):
    """
    Perform semantic similarity search using the provided query.
    Returns top-k most similar chunks with their similarity scores.
    """
    try:
        # Generate embedding for the query
        query_embedding = embedding_generator.generate_embedding(request.query)
        
        # Perform similarity search
        results = vector_store.similarity_search(
            query_embedding=query_embedding,
            k=request.k,
            min_score=request.min_score
        )
        
        # Convert to response format
        search_results = []
        for result in results:
            search_results.append({
                "id": result["id"],
                "source_doc_id": result["source_doc_id"],
                "chunk_index": result["chunk_index"],
                "section_heading": result["section_heading"],
                "journal": result["journal"],
                "publish_year": result["publish_year"],
                "usage_count": result["usage_count"],
                "attributes": result["attributes"],
                "link": result["link"],
                "text": result["text"],
                "score": result["score"],
                "doi": result.get("doi")
            })
        
        return SimilaritySearchResponse(
            results=search_results,
            total_results=len(search_results),
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing similarity search: {str(e)}")

@app.get("/api/{journal_id}", response_model=JournalDocument)
async def get_journal_document(journal_id: str):
    """
    Retrieve metadata and all chunk content for a specific journal document.
    The journal_id should be the source_doc_id of the document.
    """
    try:
        # Get all chunks for the document
        chunks = vector_store.get_document_chunks(journal_id)
        
        if not chunks:
            raise HTTPException(status_code=404, detail=f"Document with ID '{journal_id}' not found")
        
        # Extract metadata from the first chunk
        first_chunk = chunks[0]
        metadata = {
            "journal": first_chunk["journal"],
            "publish_year": first_chunk["publish_year"],
            "total_chunks": len(chunks),
            "source_doc_id": first_chunk["source_doc_id"]
        }
        
        # Add DOI if available
        if "doi" in first_chunk:
            metadata["doi"] = first_chunk["doi"]
        
        return JournalDocument(
            source_doc_id=first_chunk["source_doc_id"],
            journal=first_chunk["journal"],
            publish_year=first_chunk["publish_year"],
            total_chunks=len(chunks),
            chunks=chunks,
            metadata=metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

async def generate_paper_summary(paper_data: dict) -> str:
    """
    Generate a summary of a paper using OpenAI
    """
    try:
        prompt = f"""Please provide a comprehensive summary of this research paper:

Title/Journal: {paper_data['journal']}
Publication Year: {paper_data['publish_year']}
Total Sections: {paper_data['total_chunks']}

Full Text:
{paper_data['full_text'][:15000]}  # Limit to avoid token limits

Please provide a structured summary including:
1. Main research question/objective
2. Key methodology
3. Main findings
4. Conclusions
5. Significance/implications

Keep the summary concise but comprehensive (300-500 words)."""

        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are an expert research analyst. Provide clear, structured summaries of academic papers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return f"Error generating summary for this paper: {str(e)}"

async def generate_comparison(paper1_data: dict, paper2_data: dict, summary1: str, summary2: str) -> str:
    """
    Generate a comparison between two papers using OpenAI
    """
    try:
        prompt = f"""Compare these two research papers:

PAPER 1:
Journal: {paper1_data['journal']} ({paper1_data['publish_year']})
Summary: {summary1}

PAPER 2:
Journal: {paper2_data['journal']} ({paper2_data['publish_year']})
Summary: {summary2}

Please provide a detailed comparison covering:
1. Research objectives/questions - similarities and differences
2. Methodological approaches - how they differ or align
3. Key findings - complementary or conflicting results
4. Scope and focus areas
5. Temporal context (publication years and their significance)
6. Potential for cross-referencing or building upon each other

Structure your comparison to highlight both similarities and differences, and discuss how these papers might relate to each other in the broader research landscape."""

        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "You are an expert research analyst specializing in comparative analysis of academic papers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error generating comparison: {str(e)}")
        return f"Error generating comparison: {str(e)}"

@app.post("/api/compare", response_model=CompareResponse)
async def compare_papers(request: CompareRequest):
    """
    Compare two research papers by generating summaries and a comparison analysis.
    Takes two source_doc_ids and returns summaries for each paper plus a comparison.
    """
    try:
        print(f"Comparing papers: {request.source_doc_id_1} vs {request.source_doc_id_2}")
        
        # Get full text for both papers
        paper1_data = vector_store.get_document_full_text(request.source_doc_id_1)
        paper2_data = vector_store.get_document_full_text(request.source_doc_id_2)
        
        # Check if both papers exist
        if not paper1_data:
            raise HTTPException(status_code=404, detail=f"Paper with ID '{request.source_doc_id_1}' not found")
        
        if not paper2_data:
            raise HTTPException(status_code=404, detail=f"Paper with ID '{request.source_doc_id_2}' not found")
        
        print(f"Retrieved paper 1: {paper1_data['journal']} ({paper1_data['publish_year']})")
        print(f"Retrieved paper 2: {paper2_data['journal']} ({paper2_data['publish_year']})")
        
        # Generate summaries for both papers
        print("Generating summary for paper 1...")
        summary1 = await generate_paper_summary(paper1_data)
        
        print("Generating summary for paper 2...")
        summary2 = await generate_paper_summary(paper2_data)
        
        # Generate comparison
        print("Generating comparison analysis...")
        comparison = await generate_comparison(paper1_data, paper2_data, summary1, summary2)
        
        # Prepare response
        paper1_summary = PaperSummary(
            source_doc_id=paper1_data["source_doc_id"],
            journal=paper1_data["journal"],
            publish_year=paper1_data["publish_year"],
            total_chunks=paper1_data["total_chunks"],
            summary=summary1,
            doi=paper1_data.get("doi")
        )
        
        paper2_summary = PaperSummary(
            source_doc_id=paper2_data["source_doc_id"],
            journal=paper2_data["journal"],
            publish_year=paper2_data["publish_year"],
            total_chunks=paper2_data["total_chunks"],
            summary=summary2,
            doi=paper2_data.get("doi")
        )
        
        request_info = {
            "requested_papers": [request.source_doc_id_1, request.source_doc_id_2],
            "processing_time": "Generated summaries and comparison using OpenAI",
            "model_used": os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo")
        }
        
        return CompareResponse(
            paper1_summary=paper1_summary,
            paper2_summary=paper2_summary,
            comparison=comparison,
            request_info=request_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error comparing papers: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    ) 