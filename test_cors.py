#!/usr/bin/env python3
"""
Simple test script to verify CORS headers on Odoo JSON responses
"""
import requests
import json
import socket

# Test configuration - try multiple possible ports
POSSIBLE_URLS = [
    "http://localhost:8069",
    "http://127.0.0.1:8069", 
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

def check_port_open(host, port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def find_odoo_url():
    """Find the correct Odoo URL"""
    for url in POSSIBLE_URLS:
        try:
            host = url.split("://")[1].split(":")[0]
            port = int(url.split(":")[2]) if ":" in url.split("://")[1] else 80
            if check_port_open(host, port):
                print(f"Found Odoo running on {url}")
                return url
        except:
            continue
    return None

def test_cors_headers(url, method="POST", json_data=None):
    """Test CORS headers on a specific endpoint"""
    print(f"\n=== Testing {method} {url} ===")
    
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:5173'
    }
    
    try:
        if method == "OPTIONS":
            response = requests.options(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=json_data)
        
        print(f"Status Code: {response.status_code}")
        print("CORS Headers:")
        cors_headers = {k: v for k, v in response.headers.items() 
                       if k.lower().startswith('access-control')}
        
        if cors_headers:
            for header, value in cors_headers.items():
                print(f"  {header}: {value}")
        else:
            print("  No CORS headers found!")
            
        return cors_headers
        
    except Exception as e:
        print(f"Error: {e}")
        return {}

def main():
    print("Testing CORS implementation...")
    
    # Find running Odoo instance
    odoo_url = find_odoo_url()
    if not odoo_url:
        print("❌ No Odoo instance found running. Please start Odoo first.")
        print("Expected ports: 8069, 8080")
        return
    
    # Test OPTIONS preflight
    test_cors_headers(f"{odoo_url}/web/dataset/call_kw/res.users/search_read", "OPTIONS")
    
    # Test actual JSON request (simplified to avoid auth issues)
    json_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {},
        "id": 1
    }
    
    test_cors_headers(f"{odoo_url}/web/dataset/call_kw/res.users/search_read", "POST", json_payload)
    
    # Test sign_in OPTIONS
    test_cors_headers(f"{odoo_url}/simpos/v1/sign_in", "OPTIONS")

if __name__ == "__main__":
    main()
