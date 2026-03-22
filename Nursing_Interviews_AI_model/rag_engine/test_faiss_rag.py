import faiss
import pickle
import numpy as np
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
import time
import os

# Configurare cu calea completă
BASE_DIR = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine")
MODULE_NAME = "training_clinic_merged"
FAISS_FOLDER = BASE_DIR / "faiss_indexes" / MODULE_NAME
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"

def test_faiss_for_rag():
    print(f"🔍 Testare index FAISS pentru {MODULE_NAME}")
    print(f"📁 Director FAISS: {FAISS_FOLDER}")
    
    # Verifică existența fișierelor necesare
    index_path = FAISS_FOLDER / "index.faiss"
    docstore_path = FAISS_FOLDER / "index.pkl"
    
    if not index_path.exists():
        print(f"❌ Fișierul index.faiss nu există la calea: {index_path}")
        return False
    
    if not docstore_path.exists():
        print(f"❌ Fișierul index.pkl nu există la calea: {docstore_path}")
        return False
    
    print(f"✅ Fișierele index FAISS există:")
    print(f"   - {index_path} ({index_path.stat().st_size / (1024*1024):.2f} MB)")
    print(f"   - {docstore_path} ({docstore_path.stat().st_size / (1024*1024):.2f} MB)")
    
    try:
        # Încarcă indexul FAISS
        print("🔧 Încărcare index FAISS...")
        index = faiss.read_index(str(index_path))
        print(f"✅ Index încărcat: {index.ntotal} vectori, dimensiune {index.d}")
        
        # Încarcă docstore și analizează structura
        print("🔧 Încărcare fișier index.pkl...")
        with open(docstore_path, "rb") as f:
            docstore_data = pickle.load(f)
        
        # Determină tipul datelor pentru a le accesa corect
        print(f"✅ Fișier index.pkl încărcat, tipul datelor: {type(docstore_data)}")
        
        # Analizează primele elemente pentru a înțelege structura
        if isinstance(docstore_data, list) or isinstance(docstore_data, tuple):
            print(f"   Lista/Tuplu cu {len(docstore_data)} elemente")
            if len(docstore_data) > 0:
                print(f"   Tipul primului element: {type(docstore_data[0])}")
                if isinstance(docstore_data[0], tuple) and len(docstore_data[0]) > 0:
                    print(f"   Lungimea primului tuplu: {len(docstore_data[0])}")
                    print(f"   Exemplu conținut: {str(docstore_data[0][0])[:100]}..." if len(docstore_data[0]) > 0 else "N/A")
        elif isinstance(docstore_data, dict):
            print(f"   Dicționar cu {len(docstore_data)} chei")
            sample_key = next(iter(docstore_data))
            print(f"   Exemplu cheie: {sample_key}")
            print(f"   Exemplu valoare: {str(docstore_data[sample_key])[:100]}...")
        
        # Inițializează embeddings
        print("🔧 Inițializare model de embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        print(f"✅ Model embeddings inițializat: {MODEL_NAME}")
        
        # Testează căutarea cu câteva termeni relevante pentru nursing
        test_queries = [
            "nursing interventions for pain management",
            "blood pressure measurement technique",
            "patient assessment"
        ]
        
        print("\n📊 REZULTATE CĂUTARE:")
        print("-" * 80)
        
        # Funcție helper pentru a extrage text din structura de date
        def get_document_text(doc_index):
            try:
                if isinstance(docstore_data, list) or isinstance(docstore_data, tuple):
                    if 0 <= doc_index < len(docstore_data):
                        item = docstore_data[doc_index]
                        # Dacă item este un tuplu, extrage textul din prima poziție (sau adaptat la structura reală)
                        if isinstance(item, tuple):
                            if len(item) > 0:
                                return str(item[0])  # Presupunem că textul este primul element din tuplu
                        return str(item)
                elif isinstance(docstore_data, dict):
                    return str(docstore_data.get(doc_index, "Document negăsit"))
                return "Structură de date necunoscută"
            except Exception as e:
                return f"Eroare la accesarea documentului: {e}"
        
        for query in test_queries:
            print(f"\n🔎 Query: '{query}'")
            
            # Măsoară timpul de răspuns
            start_time = time.time()
            
            # Generează embedding pentru query
            query_embedding = embeddings.embed_query(query)
            
            # Convertește la formatul potrivit pentru FAISS
            query_embedding_np = np.array(query_embedding).astype('float32').reshape(1, -1)
            
            # Caută în indexul FAISS
            k = 3  # număr de rezultate
            distances, indices = index.search(query_embedding_np, k)
            
            end_time = time.time()
            search_time = end_time - start_time
            
            print(f"⏱️ Timp de răspuns: {search_time:.4f} secunde")
            
            # Afișează rezultatele
            for i, (doc_index, distance) in enumerate(zip(indices[0], distances[0])):
                text = get_document_text(doc_index)
                excerpt = text[:150] + "..." if len(text) > 150 else text
                print(f"\n  Rezultat #{i+1} (ID: {doc_index}, Distanță: {distance:.4f}):")
                print(f"  {excerpt}")
        
        print("\n" + "-" * 80)
        print("✅ Test complet. Indexul FAISS pare funcțional pentru RAG.")
        
        # Simulare flux RAG de bază
        print("\n🤖 Exemplu de flux RAG:")
        test_query = "Care sunt pașii pentru măsurarea tensiunii arteriale?"
        print(f"Întrebare: {test_query}")
        
        # Obține documente relevante
        query_embedding = embeddings.embed_query(test_query)
        query_embedding_np = np.array(query_embedding).astype('float32').reshape(1, -1)
        distances, indices = index.search(query_embedding_np, 3)
        
        # Construiește context pentru LLM
        context = ""
        for doc_index in indices[0]:
            text = get_document_text(doc_index)
            context += text + "\n\n"
        
        print(f"\nContext recuperat ({len(context)} caractere)")
        print(f"Primele 200 caractere din context: {context[:200]}...")
        
        print("\nAcest context ar fi trimis către un LLM pentru a genera un răspuns.")
        return True
        
    except Exception as e:
        print(f"❌ Eroare în timpul testului: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_faiss_for_rag()