"""
🧪 Test Script pentru Serviciile AI
Script pentru testarea serviciilor RAG, MCP și Knowledge Base
"""

import asyncio
import logging
import sys
from pathlib import Path

# Adaugă calea către backend în sys.path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from services.rag_service import rag_service
from services.mcp_service import mcp_service, MCPRequest, ContextType
from services.knowledge_base_service import knowledge_base_service
from services.ai_integration_service import ai_integration_service, AIEvaluationRequest

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_rag_service():
    """Testează serviciul RAG"""
    print("\n🔍 Testing RAG Service...")
    
    try:
        # Inițializează serviciul
        initialized = await rag_service.initialize()
        if not initialized:
            print("❌ RAG Service failed to initialize")
            return False
        
        # Test health check
        health = await rag_service.health_check()
        print(f"✅ RAG Service Health: {health}")
        
        # Test search (dacă există indexuri)
        if health.get("loaded_indexes"):
            from services.rag_service import RAGQuery
            query = RAGQuery(
                query_text="sepsis management",
                specialty="amu",
                band="band_5",
                max_results=3
            )
            
            results = await rag_service.search(query)
            print(f"✅ RAG Search Results: {len(results)} found")
            
            for i, result in enumerate(results[:2]):
                print(f"  Result {i+1}: {result.content[:100]}... (Score: {result.score:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG Service test failed: {str(e)}")
        return False

async def test_mcp_service():
    """Testează serviciul MCP"""
    print("\n🧠 Testing MCP Service...")
    
    try:
        # Inițializează serviciul
        initialized = await mcp_service.initialize()
        if not initialized:
            print("❌ MCP Service failed to initialize")
            return False
        
        # Test health check
        health = await mcp_service.health_check()
        print(f"✅ MCP Service Health: {health}")
        
        # Test request (doar dacă OpenAI API key este configurat)
        if health.get("openai_configured"):
            request = MCPRequest(
                query="What are the key principles of sepsis management?",
                context_type=ContextType.CLINICAL_GUIDANCE,
                specialty="amu",
                band="band_5"
            )
            
            response = await mcp_service.process_request(request)
            print(f"✅ MCP Response: {response.response[:100]}...")
            print(f"  Model used: {response.model_used}")
            print(f"  Confidence: {response.confidence}")
        else:
            print("⚠️ OpenAI API key not configured, skipping MCP request test")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP Service test failed: {str(e)}")
        return False

async def test_knowledge_base_service():
    """Testează serviciul Knowledge Base"""
    print("\n📚 Testing Knowledge Base Service...")
    
    try:
        # Inițializează serviciul
        initialized = await knowledge_base_service.initialize()
        if not initialized:
            print("❌ Knowledge Base Service failed to initialize")
            return False
        
        # Test health check
        health = await knowledge_base_service.health_check()
        print(f"✅ Knowledge Base Service Health: {health}")
        
        # Test search
        results = await knowledge_base_service.search_documents(
            query="sepsis",
            specialty="amu",
            band="band_5"
        )
        print(f"✅ Knowledge Base Search Results: {len(results)} found")
        
        for i, result in enumerate(results[:2]):
            print(f"  Document {i+1}: {result.document.title} (Score: {result.relevance_score:.2f})")
        
        # Test statistics
        stats = await knowledge_base_service.get_statistics()
        print(f"✅ Knowledge Base Statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge Base Service test failed: {str(e)}")
        return False

async def test_ai_integration_service():
    """Testează serviciul de integrare AI"""
    print("\n🤖 Testing AI Integration Service...")
    
    try:
        # Inițializează serviciul
        initialized = await ai_integration_service.initialize()
        if not initialized:
            print("❌ AI Integration Service failed to initialize")
            return False
        
        # Test health check
        health = await ai_integration_service.health_check()
        print(f"✅ AI Integration Service Health: {health}")
        
        # Test evaluation (doar dacă toate serviciile sunt disponibile)
        if health.get("all_services_healthy"):
            request = AIEvaluationRequest(
                question={
                    "id": 1,
                    "question_text": "What are the key signs of sepsis?",
                    "question_type": "multiple_choice",
                    "title": "Sepsis Recognition"
                },
                user_answer="Fever, increased heart rate, and confusion",
                band="band_5",
                specialty="amu"
            )
            
            response = await ai_integration_service.evaluate_answer(request)
            print(f"✅ AI Evaluation Response:")
            print(f"  Overall Score: {response.evaluation.overall_score}")
            print(f"  Feedback: {response.evaluation.feedback[:100]}...")
            print(f"  Processing Time: {response.processing_time:.2f}s")
            print(f"  Knowledge Sources: {len(response.knowledge_sources)}")
        else:
            print("⚠️ Not all services are healthy, skipping evaluation test")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Integration Service test failed: {str(e)}")
        return False

async def main():
    """Funcția principală de test"""
    print("🚀 Starting AI Services Test Suite...")
    
    # Testează fiecare serviciu
    tests = [
        ("RAG Service", test_rag_service),
        ("MCP Service", test_mcp_service),
        ("Knowledge Base Service", test_knowledge_base_service),
        ("AI Integration Service", test_ai_integration_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing {test_name}")
        print('='*50)
        
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Rezumat
    print(f"\n{'='*50}")
    print("TEST RESULTS SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI Services are working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    # Rulează testele
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
