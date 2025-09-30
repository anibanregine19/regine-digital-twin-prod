#!/usr/bin/env python3
"""
Deployment Verification Script
Tests all endpoints of your deployed Digital Twin
Usage: python verify_deployment.py https://your-app.vercel.app
"""

import sys
import requests
import json
from datetime import datetime

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_result(passed, message):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")

def test_endpoint(url, endpoint, method='GET', data=None):
    """Test a single endpoint"""
    full_url = f"{url}{endpoint}"
    try:
        if method == 'POST':
            response = requests.post(full_url, json=data, timeout=10)
        else:
            response = requests.get(full_url, timeout=10)
        
        return response.status_code, response.json()
    except requests.exceptions.Timeout:
        return None, {"error": "Request timeout"}
    except requests.exceptions.RequestException as e:
        return None, {"error": str(e)}
    except json.JSONDecodeError:
        return response.status_code, {"error": "Invalid JSON response"}

def verify_deployment(base_url):
    """Run all verification tests"""
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    print_header("Digital Twin Deployment Verification")
    print(f"Testing: {base_url}")
    print(f"Time: {datetime.now().isoformat()}")
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 0
    }
    
    # Test 1: Home Endpoint
    print_header("Test 1: Home Endpoint")
    status, data = test_endpoint(base_url, "/")
    results['total'] += 1
    
    if status == 200 and 'name' in data:
        results['passed'] += 1
        print_result(True, "Home endpoint is accessible")
        print(f"   Name: {data.get('name')}")
        print(f"   Version: {data.get('version')}")
    else:
        results['failed'] += 1
        print_result(False, f"Home endpoint failed (Status: {status})")
        print(f"   Response: {data}")
    
    # Test 2: Health Check
    print_header("Test 2: Health Check")
    status, data = test_endpoint(base_url, "/health")
    results['total'] += 1
    
    if status == 200 and data.get('status') == 'healthy':
        results['passed'] += 1
        print_result(True, "Health check passed")
        
        services = data.get('services', {})
        for service, service_status in services.items():
            if service_status == 'connected' or service_status == 'configured':
                print(f"   ✅ {service}: {service_status}")
            else:
                print(f"   ⚠️  {service}: {service_status}")
    else:
        results['failed'] += 1
        print_result(False, f"Health check failed (Status: {status})")
        print(f"   Response: {data}")
    
    # Test 3: Test Endpoint
    print_header("Test 3: API Test Endpoint")
    status, data = test_endpoint(base_url, "/api/test")
    results['total'] += 1
    
    if status == 200 and 'message' in data:
        results['passed'] += 1
        print_result(True, "Test endpoint is working")
        print(f"   Message: {data.get('message')}")
        print(f"   Features: {', '.join(data.get('features', []))}")
    else:
        results['failed'] += 1
        print_result(False, f"Test endpoint failed (Status: {status})")
        print(f"   Response: {data}")
    
    # Test 4: Query Endpoint (if services are configured)
    print_header("Test 4: Query Endpoint")
    
    # Check if services are configured
    health_status, health_data = test_endpoint(base_url, "/health")
    services = health_data.get('services', {})
    
    if (services.get('vector_db') in ['connected', 'configured'] and 
        services.get('groq_api') in ['connected', 'configured']):
        
        test_query = {"query": "Tell me about yourself"}
        status, data = test_endpoint(base_url, "/api/query", method='POST', data=test_query)
        results['total'] += 1
        
        if status == 200 and 'content' in data:
            results['passed'] += 1
            print_result(True, "Query endpoint is working")
            print(f"   Response length: {len(data.get('content', ''))} characters")
            if 'metadata' in data:
                print(f"   Response time: {data['metadata'].get('response_time', 'N/A')}s")
                print(f"   Vector hits: {data['metadata'].get('vector_hits', 'N/A')}")
        else:
            results['failed'] += 1
            print_result(False, f"Query endpoint failed (Status: {status})")
            print(f"   Response: {data}")
    else:
        print_result(False, "Skipping - Required services not configured")
        print("   Vector DB or Groq API not configured")
        print("   Configure these services to enable AI chat functionality")
    
    # Test 5: Analytics Endpoint (if database is configured)
    print_header("Test 5: Analytics Endpoint")
    
    if services.get('database') == 'connected':
        status, data = test_endpoint(base_url, "/api/analytics")
        results['total'] += 1
        
        if status == 200 and 'total_chats' in data:
            results['passed'] += 1
            print_result(True, "Analytics endpoint is working")
            print(f"   Total chats: {data.get('total_chats', 0)}")
            print(f"   Avg response time: {data.get('avg_response_time', 0)}s")
        else:
            results['failed'] += 1
            print_result(False, f"Analytics endpoint failed (Status: {status})")
            print(f"   Response: {data}")
    else:
        print_result(False, "Skipping - Database not configured")
        print("   Configure DATABASE_URL to enable analytics")
    
    # Summary
    print_header("Verification Summary")
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed! Your Digital Twin is working correctly.")
        print("📝 Note: Some features may be disabled if services aren't configured.")
    else:
        print("\n⚠️  Some tests failed. Check the following:")
        print("   1. Verify environment variables in Vercel")
        print("   2. Check service configuration (Neon, Upstash, Groq)")
        print("   3. Review deployment logs in Vercel dashboard")
        print("   4. See TROUBLESHOOTING.md for detailed help")
    
    print("\n" + "="*60)
    return results['failed'] == 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_deployment.py https://your-app.vercel.app")
        print("\nExample:")
        print("  python verify_deployment.py https://regine-digital-twin-prod.vercel.app")
        sys.exit(1)
    
    url = sys.argv[1]
    success = verify_deployment(url)
    sys.exit(0 if success else 1)
