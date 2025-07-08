#!/usr/bin/env python3
"""
Test script for JWT authentication system
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_token_generation():
    """Test token generation for different roles"""
    print("Testing token generation...")
    
    roles = ["admin", "analytics", "user"]
    tokens = {}
    
    for role in roles:
        print(f"\nGenerating token for role: {role}")
        
        token_data = {
            "user_id": f"test_{role}_user",
            "role": role
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/token", json=token_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            tokens[role] = result["access_token"]
            print(f"Token generated successfully")
            print(f"User ID: {result['user_id']}")
            print(f"Role: {result['role']}")
            print(f"Permissions: {result['permissions']}")
            print(f"Expires in: {result['expires_in']} seconds")
        else:
            print(f"Error: {response.text}")
    
    return tokens

def test_protected_endpoints(tokens):
    """Test protected endpoints with different tokens"""
    print("\n" + "="*50)
    print("Testing protected endpoints...")
    
    # Test cases: (endpoint, method, required_role, data)
    test_cases = [
        ("/api/upload", "PUT", "admin", {
            "file_path": "../sample_data/sample_chunks.json",
            "schema_version": "1.0"
        }),
        ("/api/popular", "GET", "analytics", None),
        ("/api/analytics", "GET", "analytics", None),
    ]
    
    for endpoint, method, required_role, data in test_cases:
        print(f"\n--- Testing {method} {endpoint} ---")
        
        # Test with correct role
        if required_role in tokens:
            print(f"✅ Testing with {required_role} token...")
            headers = {"Authorization": f"Bearer {tokens[required_role]}"}
            
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200 or response.status_code == 202:
                print("✅ Success - Access granted")
            else:
                print(f"❌ Failed: {response.text}")
        
        # Test with wrong role (user role for protected endpoints)
        if "user" in tokens and required_role != "user":
            print(f"❌ Testing with user token (should fail)...")
            headers = {"Authorization": f"Bearer {tokens['user']}"}
            
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            elif method == "PUT":
                response = requests.put(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 403:
                print("✅ Correctly blocked - Insufficient permissions")
            else:
                print(f"❌ Unexpected result: {response.text}")
        
        # Test without token
        print("❌ Testing without token (should fail)...")
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly blocked - No authentication")
        else:
            print(f"❌ Unexpected result: {response.text}")

def test_public_endpoints():
    """Test that public endpoints still work without authentication"""
    print("\n" + "="*50)
    print("Testing public endpoints (should work without auth)...")
    
    public_endpoints = [
        ("/", "GET"),
        ("/api/stats", "GET"),
    ]
    
    for endpoint, method in public_endpoints:
        print(f"\n--- Testing {method} {endpoint} ---")
        
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Public endpoint accessible")
        else:
            print(f"❌ Public endpoint failed: {response.text}")

def test_invalid_tokens():
    """Test with invalid tokens"""
    print("\n" + "="*50)
    print("Testing invalid tokens...")
    
    invalid_tokens = [
        "invalid.token.here",
        "Bearer invalid_token",
        "expired_token_would_go_here"
    ]
    
    for token in invalid_tokens:
        print(f"\n--- Testing with invalid token ---")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/api/analytics", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly rejected invalid token")
        else:
            print(f"❌ Unexpected result: {response.text}")

if __name__ == "__main__":
    print("JWT Authentication Test Script")
    print("=" * 50)
    
    # Generate tokens for all roles
    tokens = test_token_generation()
    
    if tokens:
        # Test protected endpoints
        test_protected_endpoints(tokens)
        
        # Test public endpoints
        test_public_endpoints()
        
        # Test invalid tokens
        test_invalid_tokens()
    
    print("\n" + "="*50)
    print("Authentication tests completed!") 