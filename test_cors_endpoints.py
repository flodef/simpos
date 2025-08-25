#!/usr/bin/env python3
"""
Test CORS headers on standard Odoo endpoints after fixing the response patching
"""
import requests
import json

SERVER_URL = "http://45.63.115.102:8069"
ORIGIN = "http://localhost:5173"

def test_cors_headers():
    """Test CORS headers on a standard Odoo JSON-RPC endpoint"""
    print("🔍 Testing CORS headers on /web/dataset/call_kw/pos.config/search_read")
    
    # First test OPTIONS preflight
    headers = {
        'Origin': ORIGIN,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type'
    }
    
    try:
        response = requests.options(f"{SERVER_URL}/web/dataset/call_kw/pos.config/search_read", 
                                  headers=headers)
        print(f"   OPTIONS Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin', 'MISSING')
        cors_credentials = response.headers.get('Access-Control-Allow-Credentials', 'MISSING')
        
        print(f"   ✅ Access-Control-Allow-Origin: {cors_origin}")
        print(f"   ✅ Access-Control-Allow-Credentials: {cors_credentials}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"   ❌ OPTIONS test failed: {e}")
        return False

def test_authenticated_request():
    """Test actual POST request with authentication"""
    print("\n🔍 Testing authenticated POST request with CORS")
    
    session = requests.Session()
    
    # First authenticate
    print("   Step 1: Authenticating...")
    auth_data = {
        "params": {
            "login": "flo@fims.fi",
            "password": "test123", 
            "db": "Annette"
        }
    }
    
    auth_headers = {
        'Content-Type': 'application/json',
        'Origin': ORIGIN
    }
    
    try:
        auth_response = session.post(f"{SERVER_URL}/simpos/v1/sign_in", 
                                   headers=auth_headers, 
                                   json=auth_data)
        
        if auth_response.status_code != 200:
            print(f"   ❌ Authentication failed: {auth_response.status_code}")
            return False
            
        print(f"   ✅ Authentication successful")
        
        # Now test the problematic endpoint
        print("   Step 2: Testing pos.config/search_read with session...")
        
        data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "pos.config",
                "method": "search_read",
                "args": [[]],
                "kwargs": {"fields": ["name"], "limit": 1}
            },
            "id": 1
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Origin': ORIGIN
        }
        
        response = session.post(f"{SERVER_URL}/web/dataset/call_kw/pos.config/search_read",
                              headers=headers, 
                              json=data)
        
        print(f"   Status: {response.status_code}")
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin', 'MISSING')
        cors_credentials = response.headers.get('Access-Control-Allow-Credentials', 'MISSING')
        
        print(f"   Access-Control-Allow-Origin: {cors_origin}")
        print(f"   Access-Control-Allow-Credentials: {cors_credentials}")
        
        if response.status_code == 200 and cors_origin != 'MISSING':
            print("   ✅ Request successful with CORS headers!")
            return True
        else:
            print(f"   ❌ Request failed or missing CORS headers")
            return False
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
        return False

def main():
    print("🚀 Testing CORS fixes for standard Odoo endpoints")
    print(f"Server: {SERVER_URL}")
    print(f"Origin: {ORIGIN}")
    print("="*60)
    
    options_ok = test_cors_headers()
    post_ok = test_authenticated_request()
    
    print("\n" + "="*60)
    print("📊 CORS TEST RESULTS:")
    print(f"   OPTIONS preflight: {'✅ PASS' if options_ok else '❌ FAIL'}")
    print(f"   Authenticated POST: {'✅ PASS' if post_ok else '❌ FAIL'}")
    
    if options_ok and post_ok:
        print("\n🎉 CORS is now working for standard Odoo endpoints!")
        print("The real app should be able to make requests successfully.")
    else:
        print("\n⚠️  CORS issues still exist. Check the server logs.")

if __name__ == "__main__":
    main()
