#!/usr/bin/env python3
"""
Test script for the Research Assistant API
Demonstrates how to use the three main endpoints
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_upload_chunks():
    """Test uploading chunks directly to the API"""
    print("Testing direct chunk upload...")
    
    # Load sample data
    with open("../sample_data/sample_chunks.json", "r") as f:
        chunks = json.load(f)
    
    # Prepare upload request - chunks and schema version
    upload_data = {
        "chunks": chunks,
        "schema_version": "1.0"
    }
    
    # Make PUT request
    response = requests.put(f"{BASE_URL}/api/upload", json=upload_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Wait a bit for background processing
    if response.status_code == 202:
        print("Waiting for background processing...")
        time.sleep(5)

def test_upload_local_file():
    """Test uploading from local file path"""
    print("Testing local file upload...")
    
    # Use the local sample file
    upload_data = {
        "file_path": "../sample_data/sample_chunks.json",
        "schema_version": "1.0"
    }
    
    # Make PUT request
    response = requests.put(f"{BASE_URL}/api/upload", json=upload_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Wait a bit for background processing
    if response.status_code == 202:
        print("Waiting for background processing...")
        time.sleep(5)

def test_upload_url():
    """Test uploading from URL"""
    print("Testing URL upload...")
    
    # Example with a hypothetical URL (you'd need a real URL)
    upload_data = {
        "file_path": "https://example.com/sample_chunks.json",
        "schema_version": "1.0"
    }
    
    # Make PUT request
    response = requests.put(f"{BASE_URL}/api/upload", json=upload_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Wait a bit for background processing
    if response.status_code == 202:
        print("Waiting for background processing...")
        time.sleep(10)  # File download might take longer

def test_upload_google_drive():
    """Test uploading from Google Drive"""
    print("Testing Google Drive upload...")
    
    # Example Google Drive sharing URL (you'd need a real one)
    upload_data = {
        "file_path": "https://drive.google.com/file/d/1ABC123DEF456/view?usp=sharing",
        "schema_version": "1.0"
    }
    
    # Make PUT request
    response = requests.put(f"{BASE_URL}/api/upload", json=upload_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Wait a bit for background processing
    if response.status_code == 202:
        print("Waiting for background processing...")
        time.sleep(10)

def test_similarity_search():
    """Test similarity search"""
    print("Testing similarity search...")
    
    # Test queries
    test_queries = [
        "What is velvet bean?",
        "How does attention mechanism work?",
        "Soil fertility and nitrogen fixation",
        "Neural network architecture"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        
        search_data = {
            "query": query,
            "k": 5,
            "min_score": 0.25
        }
        
        response = requests.post(f"{BASE_URL}/api/similarity_search", json=search_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['total_results']} results:")
            for i, item in enumerate(result['results'][:3], 1):
                print(f"  {i}. {item['section_heading']} (Score: {item['score']:.3f})")
                print(f"     Journal: {item['journal']} ({item['publish_year']})")
                print(f"     Text: {item['text'][:100]}...")
        else:
            print(f"Error: {response.text}")
        print()

def test_get_document():
    """Test retrieving a specific document"""
    print("Testing document retrieval...")
    
    # Test with the mucuna document
    journal_id = "extension_brief_mucuna.pdf"
    
    response = requests.get(f"{BASE_URL}/api/{journal_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        document = response.json()
        print(f"Document: {document['source_doc_id']}")
        print(f"Journal: {document['journal']}")
        print(f"Year: {document['publish_year']}")
        print(f"Total chunks: {document['total_chunks']}")
        print(f"Chunks:")
        for chunk in document['chunks']:
            print(f"  - {chunk['section_heading']} (Index: {chunk['chunk_index']})")
    else:
        print(f"Error: {response.text}")
    print()

def test_stats():
    """Test getting vector store statistics"""
    print("Testing stats endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_compare_papers():
    """Test comparing two papers"""
    print("Testing paper comparison...")
    
    # Test with two different document IDs
    # You'll need to replace these with actual source_doc_ids from your database
    compare_data = {
        "source_doc_id_1": "extension_brief_mucuna.pdf",
        "source_doc_id_2": "another_paper_id.pdf"  # Replace with actual ID
    }
    
    print(f"Comparing papers: {compare_data['source_doc_id_1']} vs {compare_data['source_doc_id_2']}")
    
    response = requests.post(f"{BASE_URL}/api/compare", json=compare_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Comparison Results:")
        print(f"Paper 1: {result['paper1_summary']['journal']} ({result['paper1_summary']['publish_year']})")
        print(f"Summary 1: {result['paper1_summary']['summary'][:200]}...")
        print()
        print(f"Paper 2: {result['paper2_summary']['journal']} ({result['paper2_summary']['publish_year']})")
        print(f"Summary 2: {result['paper2_summary']['summary'][:200]}...")
        print()
        print(f"Comparison: {result['comparison'][:300]}...")
        print()
        print(f"Model used: {result['request_info']['model_used']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_popular_papers():
    """Test getting popular papers"""
    print("Testing popular papers endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/popular")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Popular chunks found: {len(result['popular_chunks'])}")
        for i, chunk in enumerate(result['popular_chunks'][:3], 1):
            print(f"  {i}. Chunk ID: {chunk['chunk_id']}")
            print(f"     Source: {chunk['source_doc_id']}")
            print(f"     Usage Count: {chunk['usage_count']}")
            print(f"     Last Accessed: {chunk['last_accessed']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_analytics():
    """Test getting analytics"""
    print("Testing analytics endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/analytics")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total chunks accessed: {result['total_chunks_accessed']}")
        print(f"Total accesses: {result['total_accesses']}")
        print(f"Most popular chunks: {len(result['most_popular'])}")
        print(f"Recent activity today: {len(result['recent_activity'])}")
        
        if result['most_popular']:
            print("\nTop 3 most popular:")
            for i, chunk in enumerate(result['most_popular'][:3], 1):
                print(f"  {i}. {chunk['chunk_id']} - {chunk['usage_count']} accesses")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("Research Assistant API Test Script")
    print("=" * 40)
    
    # Test all endpoints
    test_health_check()
    test_upload_chunks()
    test_similarity_search()
    test_get_document()
    test_stats()
    test_popular_papers()
    test_analytics()
    test_compare_papers()
    
    print("Test completed!") 