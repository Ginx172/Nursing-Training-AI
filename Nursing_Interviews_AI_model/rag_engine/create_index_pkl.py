import pickle
import faiss
import os
import numpy as np

# Calea către fișierele index
faiss_index_path = r"faiss_indexes\elderly_care\index.faiss"
pkl_path = r"faiss_indexes\elderly_care\index.pkl"
backup_pkl_path = r"faiss_indexes\elderly_care\index.pkl.backup"

# Creează backup pentru fișierul index.pkl existent
if os.path.exists(pkl_path):
    print(f"Creez backup pentru fișierul original la {backup_pkl_path}")
    try:
        with open(pkl_path, "rb") as src, open(backup_pkl_path, "wb") as dst:
            dst.write(src.read())
        print("Backup creat cu succes.")
    except Exception as e:
        print(f"Eroare la crearea backup-ului: {str(e)}")
        exit(1)

# Încarcă indexul FAISS pentru a afla numărul de vectori
print(f"Încărcare index FAISS de la {faiss_index_path}...")
try:
    index = faiss.read_index(faiss_index_path)
    n_vectors = index.ntotal
    print(f"Index încărcat cu succes: {n_vectors} vectori")
except Exception as e:
    print(f"Eroare la încărcarea indexului FAISS: {str(e)}")
    exit(1)

# Creează un nou mapping pentru index.pkl
print("Creez un nou fișier index.pkl cu structura corectă...")

# Opțiunea 1: Structura simplă - dicționar cu mapare index -> doc_id
index_to_docstore_id = {i: f"doc_{i}" for i in range(n_vectors)}

# Opțiunea 2: Structura complexă - include și maparea și documentele
# Decomentează și adaptează acest cod dacă ai nevoie de această structură
"""
documents = {}
for i in range(n_vectors):
    doc_id = f"doc_{i}"
    documents[doc_id] = {
        "text": f"Document placeholder {i}",  # Trebuie înlocuit cu textul real
        "metadata": {"source": f"source_{i}"}  # Trebuie înlocuit cu metadata reală
    }

index_data = {
    "index_to_docstore_id": index_to_docstore_id,
    "documents": documents
}
"""

# Alege ce structură să salvezi
data_to_save = index_to_docstore_id  # sau index_data pentru structura complexă

# Salvează noul fișier
try:
    with open(pkl_path, "wb") as f:
        pickle.dump(data_to_save, f, protocol=4)
    print(f"Fișier index.pkl creat cu succes la {pkl_path}")
except Exception as e:
    print(f"Eroare la salvarea noului fișier index.pkl: {str(e)}")
    exit(1)

print("Proces finalizat. Verifică dacă indexul funcționează acum corect.")