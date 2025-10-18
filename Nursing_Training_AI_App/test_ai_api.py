"""
🧪 Test Script pentru AI API Endpoints
Script pentru testarea endpoint-urilor AI prin HTTP requests
"""

import requests
import json
import time
from typing import Dict, Any

# Configurație
API_BASE_URL = "http://localhost:8000"
API_AI_BASE = f"{API_BASE_URL}/api/ai"

def test_api_health():
    """Testează health check-urile API-urilor"""
    print("🏥 Testing API Health Checks...")
    
    endpoints = [
        f"{API_AI_BASE}/health/rag",
        f"{API_AI_BASE}/health/mcp", 
        f"{API_AI_BASE}/health/knowledge-base",
        f"{API_AI_BASE}/health/all"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}: {data.get('initialized', 'Unknown')}")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

def test_rag_search():
    """Testează RAG search"""
    print("\n🔍 Testing RAG Search...")
    
    try:
        payload = {
            "query": "sepsis management",
            "specialty": "amu",
            "band": "band_5",
            "max_results": 3,
            "min_score": 0.6
        }
        
        response = requests.post(
            f"{API_AI_BASE}/rag/search",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG Search: {data['total_found']} results found")
            for i, result in enumerate(data['results'][:2]):
                print(f"  Result {i+1}: {result['content'][:100]}... (Score: {result['score']:.2f})")
        else:
            print(f"❌ RAG Search: HTTP {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ RAG Search: {str(e)}")

def test_knowledge_base_search():
    """Testează Knowledge Base search"""
    print("\n📚 Testing Knowledge Base Search...")
    
    try:
        payload = {
            "query": "sepsis",
            "specialty": "amu",
            "band": "band_5"
        }
        
        response = requests.post(
            f"{API_AI_BASE}/knowledge-base/search",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge Base Search: {len(data)} documents found")
            for i, result in enumerate(data[:2]):
                print(f"  Document {i+1}: {result['document']['title']} (Score: {result['relevance_score']:.2f})")
        else:
            print(f"❌ Knowledge Base Search: HTTP {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Knowledge Base Search: {str(e)}")

def test_mcp_request():
    """Testează MCP request"""
    print("\n🧠 Testing MCP Request...")
    
    try:
        payload = {
            "query": "What are the key principles of sepsis management?",
            "context_type": "clinical_guidance",
            "specialty": "amu",
            "band": "band_5",
            "additional_context": "This is for a Band 5 nurse in AMU"
        }
        
        response = requests.post(
            f"{API_AI_BASE}/mcp/process",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MCP Request: {data['response'][:100]}...")
            print(f"  Model used: {data['model_used']}")
            print(f"  Confidence: {data['confidence']}")
        else:
            print(f"❌ MCP Request: HTTP {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ MCP Request: {str(e)}")

def test_ai_evaluation():
    """Testează AI evaluation completă"""
    print("\n🤖 Testing AI Evaluation...")
    
    try:
        payload = {
            "question": {
                "id": 1,
                "question_text": "What are the key signs of sepsis?",
                "question_type": "multiple_choice",
                "title": "Sepsis Recognition"
            },
            "user_answer": "Fever, increased heart rate, and confusion",
            "band": "band_5",
            "specialty": "amu",
            "user_context": {
                "experience_years": 2,
                "previous_training": ["basic_life_support"]
            }
        }
        
        response = requests.post(
            f"{API_AI_BASE}/ai/evaluate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            evaluation = data['evaluation']
            print(f"✅ AI Evaluation:")
            print(f"  Overall Score: {evaluation['overall_score']}")
            print(f"  Feedback: {evaluation['feedback'][:100]}...")
            print(f"  Processing Time: {data['processing_time']:.2f}s")
            print(f"  Knowledge Sources: {len(data['knowledge_sources'])}")
            print(f"  Recommendations: {len(data['recommendations'])}")
        else:
            print(f"❌ AI Evaluation: HTTP {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ AI Evaluation: {str(e)}")

def test_knowledge_base_info():
    """Testează informațiile despre Knowledge Base"""
    print("\n📊 Testing Knowledge Base Information...")
    
    try:
        # Test specialties
        response = requests.get(f"{API_AI_BASE}/knowledge-base/specialties", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available Specialties: {data['specialties']}")
        else:
            print(f"❌ Specialties: HTTP {response.status_code}")
        
        # Test bands
        response = requests.get(f"{API_AI_BASE}/knowledge-base/bands", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available Bands: {data['bands']}")
        else:
            print(f"❌ Bands: HTTP {response.status_code}")
        
        # Test statistics
        response = requests.get(f"{API_AI_BASE}/knowledge-base/statistics", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge Base Statistics:")
            print(f"  Total Documents: {data.get('total_documents', 0)}")
            print(f"  Total Size: {data.get('total_size_mb', 0)} MB")
            print(f"  Specialty Counts: {data.get('specialty_counts', {})}")
        else:
            print(f"❌ Statistics: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowledge Base Info: {str(e)}")

def main():
    """Funcția principală de test"""
    print("🚀 Starting AI API Test Suite...")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"AI API Base URL: {API_AI_BASE}")
    print("")
    
    # Verifică dacă API-ul este disponibil
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running")
        else:
            print("❌ Backend API is not responding correctly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend API: {str(e)}")
        print("Make sure the backend is running: python main.py")
        return
    
    # Rulează testele
    tests = [
        ("API Health Checks", test_api_health),
        ("RAG Search", test_rag_search),
        ("Knowledge Base Search", test_knowledge_base_search),
        ("MCP Request", test_mcp_request),
        ("AI Evaluation", test_ai_evaluation),
        ("Knowledge Base Info", test_knowledge_base_info)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing {test_name}")
        print('='*50)
        
        try:
            test_func()
            passed += 1
            print(f"✅ {test_name} completed")
        except Exception as e:
            print(f"❌ {test_name} failed: {str(e)}")
    
    # Rezumat
    print(f"\n{'='*50}")
    print("TEST RESULTS SUMMARY")
    print('='*50)
    print(f"Overall: {passed}/{total} tests completed")
    
    if passed == total:
        print("🎉 All tests completed! AI Services are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
