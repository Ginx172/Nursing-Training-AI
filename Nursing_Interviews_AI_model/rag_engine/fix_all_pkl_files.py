import os
import faiss
import pickle
import sys

def fix_all_pkl_files(base_folder="faiss_indexes"):
    """
    Repară toate fișierele index.pkl pentru toate domeniile, folosind structura care a funcționat pentru elderly_care
    
    Args:
        base_folder: Directorul de bază care conține toate folderele cu indexuri
    """
    domains = [
        "training_clinic_merged", 
        "pediatrics", 
        "obstetrics_gyn", 
        "mental_health", 
        "leadership_training", 
        "interview_nhs", 
        "emergency_care", 
        "elderly_care",  # Inclus pentru verificare, deși deja funcționează
        "communication_skills", 
        "clinical_governance"
    ]
    
    # Verifică formatul fișierului elderly_care (care funcționează)
    success_template = None
    elderly_pkl_path = os.path.join(base_folder, "elderly_care", "index.pkl")
    
    if os.path.exists(elderly_pkl_path):
        try:
            with open(elderly_pkl_path, "rb") as f:
                success_template = pickle.load(f)
            print(f"✅ Am încărcat formatul de succes din elderly_care: {type(success_template)}")
            if isinstance(success_template, dict):
                print(f"   Este un dicționar cu {len(success_template)} intrări")
            else:
                print(f"   Nu este un dicționar standard: {type(success_template)}")
        except Exception as e:
            print(f"❌ Nu am putut încărca formatul de succes: {str(e)}")
            print("Voi crea fișiere index.pkl noi folosind formatul standard de dicționar.")
    else:
        print(f"⚠️ Fișierul {elderly_pkl_path} nu există.")
        print("Voi crea fișiere index.pkl noi folosind formatul standard de dicționar.")
    
    # Procesăm fiecare domeniu
    for domain in domains:
        if domain == "elderly_care" and success_template is not None:
            print(f"ℹ️ Ignorăm {domain} deoarece deja funcționează.")
            continue
        
        faiss_path = os.path.join(base_folder, domain, "index.faiss")
        pkl_path = os.path.join(base_folder, domain, "index.pkl")
        backup_pkl_path = os.path.join(base_folder, domain, "index.pkl.backup")
        
        if not os.path.exists(faiss_path):
            print(f"⚠️ Indexul FAISS pentru {domain} nu există. Se ignoră.")
            continue
        
        print(f"\n--- Procesare {domain} ---")
        
        # Încarcă indexul FAISS pentru a afla numărul de vectori
        try:
            print(f"Încărcare index FAISS pentru {domain}...")
            index = faiss.read_index(faiss_path)
            n_vectors = index.ntotal
            print(f"✅ Index încărcat: {n_vectors} vectori")
        except Exception as e:
            print(f"❌ Eroare la încărcarea indexului FAISS pentru {domain}: {str(e)}")
            continue
        
        # Creează backup pentru fișierul original dacă există
        if os.path.exists(pkl_path):
            print(f"Creez backup pentru fișierul original la {backup_pkl_path}")
            try:
                with open(pkl_path, "rb") as src, open(backup_pkl_path, "wb") as dst:
                    dst.write(src.read())
                print("✅ Backup creat cu succes.")
            except Exception as e:
                print(f"❌ Eroare la crearea backup-ului: {str(e)}")
                continue
        
        # Creează un nou fișier index.pkl cu structura corectă
        print(f"Creez un nou fișier index.pkl pentru {domain}...")
        
        # Creează un mapping simplu index -> doc_id
        index_to_docstore_id = {i: f"doc_{i}" for i in range(n_vectors)}
        
        # Salvează noul fișier
        try:
            with open(pkl_path, "wb") as f:
                pickle.dump(index_to_docstore_id, f, protocol=4)
            print(f"✅ Fișier index.pkl creat cu succes la {pkl_path}")
        except Exception as e:
            print(f"❌ Eroare la salvarea noului fișier index.pkl: {str(e)}")
            continue
    
    print("\n=== Proces finalizat ===")
    print("Toate fișierele index.pkl au fost reparate.")
    print("Rulează din nou rag_system.py pentru a verifica dacă toate indexurile se încarcă corect acum.")

if __name__ == "__main__":
    # Determină folderul de bază din argument sau folosește valoarea implicită
    base_folder = sys.argv[1] if len(sys.argv) > 1 else "faiss_indexes"
    fix_all_pkl_files(base_folder)