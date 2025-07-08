from pydantic import BaseModel, Field, validator
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
    chunks: Optional[List[JournalChunk]] = None
    file_path: Optional[str] = None
    schema_version: str = Field(description="Schema version for the data format")
    
    @validator('chunks', 'file_path')
    def validate_chunks_or_file_path(cls, v, values):
        chunks = values.get('chunks') if 'chunks' in values else v
        file_path = values.get('file_path') if 'file_path' in values else None
        
        # If this is the file_path field being validated
        if v is not None and isinstance(v, str):
            file_path = v
        
        # Check that exactly one of chunks or file_path is provided
        if chunks is not None and file_path is not None:
            raise ValueError('Provide either chunks or file_path, not both')
        if chunks is None and file_path is None:
            raise ValueError('Must provide either chunks or file_path')
        
        return v

class UploadResponse(BaseModel):
    message: str
    status: str = "accepted"
    processing_type: str

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

class CompareRequest(BaseModel):
    source_doc_id_1: str = Field(description="First paper's source document ID")
    source_doc_id_2: str = Field(description="Second paper's source document ID")

class PaperSummary(BaseModel):
    source_doc_id: str
    journal: str
    publish_year: int
    total_chunks: int
    summary: str
    doi: Optional[str] = None

class CompareResponse(BaseModel):
    paper1_summary: PaperSummary
    paper2_summary: PaperSummary
    comparison: str
    request_info: dict

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None 