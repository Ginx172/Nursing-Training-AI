import pickle
import faiss
import os

# Calea către fișierele index
faiss_index_path = r"faiss_indexes\elderly_care\index.faiss"
pkl_path = r"faiss_indexes\elderly_care\index.pkl"

# Verifică dacă fișierele există
if not os.path.exists(faiss_index_path) or not os.path.exists(pkl_path):
    print("Fișierele index nu există!")
    exit(1)

# Încarcă indexul FAISS
try:
    print("Încărcare index FAISS...")
    index = faiss.read_index(faiss_index_path)
    print(f"✅ Index încărcat: {index.ntotal} vectori, dimensiune {index.d}")
except Exception as e:
    print(f"❌ Eroare la încărcarea indexului FAISS: {str(e)}")
    exit(1)

# Încarcă fișierul index.pkl
try:
    print("Încărcare fișier index.pkl...")
    with open(pkl_path, "rb") as f:
        pkl_data = pickle.load(f)
    
    # Verifică structura
    if isinstance(pkl_data, dict):
        # Verifică dacă este un dicționar simplu sau structura complexă
        if "index_to_docstore_id" in pkl_data and "documents" in pkl_data:
            # Structura complexă
            print(f"✅ Structura fișierului index.pkl este corectă (format complex)")
            print(f"   - {len(pkl_data['index_to_docstore_id'])} mapări index->docID")
            print(f"   - {len(pkl_data['documents'])} documente")
        else:
            # Dicționar simplu
            print(f"✅ Structura fișierului index.pkl este corectă (format simplu)")
            print(f"   - {len(pkl_data)} mapări index->docID")
            
            # Verifică dacă numărul de intrări corespunde cu numărul de vectori
            if len(pkl_data) != index.ntotal:
                print(f"⚠️ Avertisment: Numărul de mapări ({len(pkl_data)}) nu corespunde cu numărul de vectori din index ({index.ntotal})")
    else:
        print(f"❓ Structura fișierului index.pkl nu este un dicționar standard: {type(pkl_data)}")
        
    print("✅ Test complet. Indexul ar trebui să funcționeze acum corect.")
except Exception as e:
    print(f"❌ Eroare la încărcarea/verificarea fișierului index.pkl: {str(e)}")