from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from typing import List

try:
    from .models import (
        UploadRequest, UploadResponse, SimilaritySearchRequest, 
        SimilaritySearchResponse, JournalDocument, ErrorResponse
    )
    from .embeddings import EmbeddingGenerator
    from .vector_store import ChromaVectorStore
except ImportError:
    from models import (
        UploadRequest, UploadResponse, SimilaritySearchRequest, 
        SimilaritySearchResponse, JournalDocument, ErrorResponse
    )
    from embeddings import EmbeddingGenerator
    from vector_store import ChromaVectorStore

load_dotenv()

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
    Upload journal chunks, generate embeddings, and store them in the vector database.
    Returns 202 Accepted as the processing happens asynchronously.
    """
    try:
        # Validate request
        if not request.chunks:
            raise HTTPException(status_code=400, detail="No chunks provided")
        
        # Add background task to process chunks
        background_tasks.add_task(process_chunks, [chunk.dict() for chunk in request.chunks])
        
        return UploadResponse(
            message="Chunks accepted for processing",
            chunks_processed=len(request.chunks),
            status="accepted"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")

async def process_chunks(chunks: List[dict]):
    """
    Background task to process chunks: generate embeddings and store in vector database
    """
    try:
        print(f"Processing {len(chunks)} chunks...")
        
        # Extract text content for embedding generation
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = embedding_generator.generate_embeddings_batch(texts)
        
        # Store in vector database
        print("Storing in vector database...")
        success = vector_store.add_chunks(chunks, embeddings)
        
        if success:
            print(f"Successfully processed {len(chunks)} chunks")
        else:
            print("Failed to store chunks in vector database")
            
    except Exception as e:
        print(f"Error in background processing: {str(e)}")

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