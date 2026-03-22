import faiss
import pickle
import numpy as np
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
import time
import os

# Configurare cu calea completă
BASE_DIR = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine")
MODULE_NAME = "elderly_care"
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
        
        # Încarcă docstore
        print("🔧 Încărcare fișier index.pkl...")
        with open(docstore_path, "rb") as f:
            # index.pkl conține un tuplu cu 2 elemente: (docstore, index_to_id_map)
            pkl_data = pickle.load(f)
            
        # Extragem docstore-ul din primul element al tuplului
        if isinstance(pkl_data, tuple) and len(pkl_data) > 0:
            docstore = pkl_data[0]
            print(f"✅ Docstore încărcat: {type(docstore)}")
            
            # Verificăm dacă docstore-ul are un dicționar _dict
            if hasattr(docstore, '_dict'):
                print(f"   Docstore conține {len(docstore._dict)} documente")
                # Afișăm câteva chei de exemple
                sample_keys = list(docstore._dict.keys())[:3]
                print(f"   Exemple de chei: {sample_keys}")
            else:
                print("   Docstore nu conține atributul _dict")
                # Încercăm alte atribute comune
                for attr in ['docstore', 'documents', 'docs', '_docs']:
                    if hasattr(docstore, attr):
                        attr_value = getattr(docstore, attr)
                        print(f"   Atribut găsit: {attr}, Tip: {type(attr_value)}")
                        if hasattr(attr_value, '__len__'):
                            print(f"   Conține {len(attr_value)} elemente")
        else:
            print("❌ Structura fișierului index.pkl nu este cea așteptată")
            return False
        
        # Inițializează embeddings
        print("🔧 Inițializare model de embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        print(f"✅ Model embeddings inițializat: {MODEL_NAME}")
        
        # Testează căutarea cu câteva termeni relevante pentru nursing
        test_queries = [
            "nursing interventions for pain management",
            "blood pressure measurement technique"
        ]
        
        print("\n📊 REZULTATE CĂUTARE:")
        print("-" * 80)
        
        # Funcție helper pentru a extrage text din docstore
        def get_document_text(doc_id):
            try:
                # Încercăm metodele standard de accesare a documentelor din LangChain docstore
                if hasattr(docstore, 'search'):
                    return str(docstore.search(doc_id))
                elif hasattr(docstore, 'get'):
                    return str(docstore.get(doc_id))
                elif hasattr(docstore, '_dict'):
                    return str(docstore._dict.get(doc_id, "Document negăsit"))
                else:
                    # Ca ultimă soluție, încercăm să-l tratăm ca pe un dicționar
                    return str(docstore[doc_id]) if doc_id in docstore else "Document negăsit"
            except Exception as e:
                return f"Eroare la accesarea documentului {doc_id}: {e}"
        
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
            
            # Verificăm dacă avem un mapping pentru indici
            id_map = None
            if isinstance(pkl_data, tuple) and len(pkl_data) > 1:
                id_map = pkl_data[1]
                print(f"   Folosim mapping ID: {type(id_map)}")
            
            # Afișează rezultatele
            for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
                # Convertim indexul la ID-ul corespunzător din docstore dacă avem un mapping
                doc_id = id_map[idx] if id_map is not None else idx
                
                # Obținem textul
                text = get_document_text(doc_id)
                excerpt = text[:150] + "..." if len(text) > 150 else text
                
                print(f"\n  Rezultat #{i+1} (ID: {doc_id}, Index: {idx}, Distanță: {distance:.4f}):")
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
        for idx in indices[0]:
            # Convertim indexul la ID-ul corespunzător din docstore dacă avem un mapping
            doc_id = id_map[idx] if id_map is not None else idx
            text = get_document_text(doc_id)
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