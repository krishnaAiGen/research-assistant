import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import json

load_dotenv()

class ChromaVectorStore:
    def __init__(self):
        self.db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.collection_name = os.getenv("CHROMA_COLLECTION_NAME", "journal_chunks")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """
        Get existing collection or create a new one
        """
        try:
            collection = self.client.get_collection(name=self.collection_name)
            print(f"Using existing collection: {self.collection_name}")
        except:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Journal chunks for semantic search"}
            )
            print(f"Created new collection: {self.collection_name}")
        
        return collection
    
    def add_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]], schema_version: str = "1.0") -> bool:
        """
        Add chunks with their embeddings to the vector store
        """
        try:
            # Prepare data for ChromaDB
            ids = [chunk["id"] for chunk in chunks]
            texts = [chunk["text"] for chunk in chunks]
            metadatas = []
            
            for chunk in chunks:
                metadata = {
                    "source_doc_id": chunk["source_doc_id"],
                    "chunk_index": chunk["chunk_index"],
                    "section_heading": chunk["section_heading"],
                    "journal": chunk["journal"],
                    "publish_year": chunk["publish_year"],
                    "usage_count": chunk["usage_count"],
                    "attributes": json.dumps(chunk["attributes"]),
                    "link": chunk["link"],
                    "schema_version": schema_version
                }
                if "doi" in chunk and chunk["doi"]:
                    metadata["doi"] = chunk["doi"]
                
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            print(f"Successfully added {len(chunks)} chunks to vector store with schema v{schema_version}")
            return True
            
        except Exception as e:
            print(f"Error adding chunks to vector store: {str(e)}")
            return False
    
    def similarity_search(self, query_embedding: List[float], k: int = 10, min_score: float = 0.25) -> List[Dict[str, Any]]:
        """
        Perform similarity search using query embedding
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["documents", "metadatas", "distances"]
            )
            
            # Process results
            processed_results = []
            for i in range(len(results["ids"][0])):
                chunk_id = results["ids"][0][i]
                distance = results["distances"][0][i]
                metadata = results["metadatas"][0][i]
                text = results["documents"][0][i]
                
                # Convert distance to similarity score (ChromaDB returns L2 distance)
                # We'll convert to a similarity score between 0 and 1
                similarity_score = max(0, 1 - distance)
                
                if similarity_score >= min_score:
                    result = {
                        "id": chunk_id,
                        "source_doc_id": metadata["source_doc_id"],
                        "chunk_index": metadata["chunk_index"],
                        "section_heading": metadata["section_heading"],
                        "journal": metadata["journal"],
                        "publish_year": metadata["publish_year"],
                        "usage_count": metadata["usage_count"],
                        "attributes": json.loads(metadata["attributes"]),
                        "link": metadata["link"],
                        "text": text,
                        "score": similarity_score,
                        "schema_version": metadata.get("schema_version", "1.0")
                    }
                    
                    if "doi" in metadata:
                        result["doi"] = metadata["doi"]
                    
                    processed_results.append(result)
            
            # Sort by similarity score (highest first)
            processed_results.sort(key=lambda x: x["score"], reverse=True)
            
            return processed_results
            
        except Exception as e:
            print(f"Error performing similarity search: {str(e)}")
            return []
    
    def get_document_chunks(self, source_doc_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific document
        """
        try:
            results = self.collection.get(
                where={"source_doc_id": source_doc_id},
                include=["documents", "metadatas"]
            )
            
            chunks = []
            for i in range(len(results["ids"])):
                chunk_id = results["ids"][i]
                metadata = results["metadatas"][i]
                text = results["documents"][i]
                
                chunk = {
                    "id": chunk_id,
                    "source_doc_id": metadata["source_doc_id"],
                    "chunk_index": metadata["chunk_index"],
                    "section_heading": metadata["section_heading"],
                    "journal": metadata["journal"],
                    "publish_year": metadata["publish_year"],
                    "usage_count": metadata["usage_count"],
                    "attributes": json.loads(metadata["attributes"]),
                    "link": metadata["link"],
                    "text": text,
                    "schema_version": metadata.get("schema_version", "1.0")
                }
                
                if "doi" in metadata:
                    chunk["doi"] = metadata["doi"]
                
                chunks.append(chunk)
            
            # Sort by chunk_index
            chunks.sort(key=lambda x: x["chunk_index"])
            
            return chunks
            
        except Exception as e:
            print(f"Error retrieving document chunks: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        """
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection_name
            }
        except Exception as e:
            print(f"Error getting collection stats: {str(e)}")
            return {"total_chunks": 0, "collection_name": self.collection_name} 