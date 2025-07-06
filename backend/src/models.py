from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

class JournalChunk(BaseModel):
    id: str
    source_doc_id: str
    chunk_index: int
    section_heading: str
    journal: str
    publish_year: int
    usage_count: int
    attributes: List[str]
    link: str
    text: str
    doi: Optional[str] = None

class UploadRequest(BaseModel):
    chunks: List[JournalChunk]

class UploadResponse(BaseModel):
    message: str
    chunks_processed: int
    status: str = "accepted"

class SimilaritySearchRequest(BaseModel):
    query: str
    k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    min_score: float = Field(default=0.25, ge=0.0, le=1.0, description="Minimum similarity score")

class SearchResult(BaseModel):
    id: str
    source_doc_id: str
    chunk_index: int
    section_heading: str
    journal: str
    publish_year: int
    usage_count: int
    attributes: List[str]
    link: str
    text: str
    score: float
    doi: Optional[str] = None

class SimilaritySearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    query: str

class JournalDocument(BaseModel):
    source_doc_id: str
    journal: str
    publish_year: int
    total_chunks: int
    chunks: List[JournalChunk]
    metadata: dict

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None 