import os
import time
import hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from tqdm import tqdm

# Pentru LangChain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# === CONFIG ===
MODULE_NAME = "interview_nhs"
BASE_FOLDER = Path("sorted_by_module") / MODULE_NAME
FAISS_FOLDER = Path("faiss_indexes") / MODULE_NAME
MAX_WORKERS = os.cpu_count() or 4  # Folosim toate nucleele disponibile
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
BATCH_SIZE = 500  # Număr de documente pentru procesare în batch

# === UTILS ===
def find_txt_files(folder):
    """Găsește toate fișierele text recursiv - optimizat"""
    return list(folder.rglob("*.txt"))

def hash_file(path):
    """Calculează hash pentru un fișier - optimizat cu buffer pentru fișiere mari"""
    h = hashlib.md5()
    with open(path, 'rb') as f:
        # Citim bucăți de 8192 bytes pentru eficiență
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def process_file_batch(file_paths):
    """Procesează un batch de fișiere pentru deduplicare"""
    results = {}
    for path in file_paths:
        try:
            file_hash = hash_file(path)
            results[path] = file_hash
        except Exception as e:
            print(f"    ⚠️ Eroare la calcularea hash pentru {path.name}: {e}")
    return results

def remove_exact_duplicates(file_paths):
    """Elimină duplicate exacte folosind paralelizare"""
    print("[1/4] Eliminăm duplicate exacte (paralel)...")
    
    # Împărțim fișierele în batch-uri optime pentru procesare paralelă
    batch_size = max(1, min(100, len(file_paths) // MAX_WORKERS))  # Optimizat pentru echilibrarea sarcinilor
    batches = [file_paths[i:i + batch_size] for i in range(0, len(file_paths), batch_size)]
    
    unique_files = []
    hashes = {}
    duplicates_count = 0
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_file_batch, batch) for batch in batches]
        
        # Procesăm rezultatele pe măsură ce sunt finalizate
        for future in tqdm(as_completed(futures), total=len(futures), desc="Procesare batch-uri"):
            batch_results = future.result()
            for path, file_hash in batch_results.items():
                if file_hash not in hashes:
                    hashes[file_hash] = path
                    unique_files.append(path)
                else:
                    duplicates_count += 1
                    print(f"    ⚠️ Duplicat eliminat: {path.name}")
    
    print(f"    ✅ Reținute {len(unique_files)} fișiere unice din {len(file_paths)} totale ({duplicates_count} duplicate eliminate)")
    return unique_files

def load_document(path, text_splitter):
    """Încarcă și împarte un document"""
    try:
        loader = TextLoader(path, encoding="utf-8")
        docs = loader.load()
        split_docs = text_splitter.split_documents(docs)
        return split_docs
    except UnicodeDecodeError:
        # Încercăm cu alte codificări dacă UTF-8 eșuează
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                loader = TextLoader(path, encoding=encoding)
                docs = loader.load()
                split_docs = text_splitter.split_documents(docs)
                print(f"    ℹ️ {path.name}: Utilizăm codificarea {encoding}")
                return split_docs
            except Exception:
                continue
        print(f"    ⚠️ Eroare la {path.name}: Nu s-a putut determina codificarea")
        return []
    except Exception as e:
        print(f"    ⚠️ Eroare la {path.name}: {e}")
        return []

def load_and_split_documents(file_paths):
    """Încarcă și împarte documentele folosind procesare paralelă"""
    print("[2/4] Încărcăm și împărțim fișierele (paralel)...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    
    documents = []
    load_fn = partial(load_document, text_splitter=text_splitter)
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(load_fn, path) for path in file_paths]
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Procesare documente"):
            documents.extend(future.result())
    
    return documents

def process_document_batch(docs_batch, embeddings, faiss_db=None):
    """Procesează un batch de documente și le adaugă la indexul FAISS"""
    if not docs_batch:
        return faiss_db
    
    try:
        batch_db = FAISS.from_documents(docs_batch, embeddings)
        
        if faiss_db is None:
            return batch_db
        else:
            faiss_db.merge_from(batch_db)
            return faiss_db
    except Exception as e:
        print(f"    ⚠️ Eroare la procesarea unui batch: {e}")
        # În caz de eroare, încercăm să procesăm documentele individual
        if len(docs_batch) > 1:
            print("    ℹ️ Încercăm procesarea individuală a documentelor...")
            half = len(docs_batch) // 2
            first_half = process_document_batch(docs_batch[:half], embeddings, faiss_db)
            return process_document_batch(docs_batch[half:], embeddings, first_half)
        else:
            print(f"    ⚠️ Document problematic ignorat")
            return faiss_db

def build_faiss_index(docs, embeddings):
    """Construiește indexul FAISS folosind procesare în batch"""
    print(f"[3/4] Construim index FAISS (în batch-uri de {BATCH_SIZE} documente)...")
    
    # Afișăm dimensiunea totală a datelor pentru a estima memoria necesară
    total_docs = len(docs)
    print(f"    ℹ️ Total documente de procesat: {total_docs}")
    
    # Procesăm documentele în batch-uri pentru a reduce utilizarea memoriei
    faiss_db = None
    
    # Împărțim lista în batch-uri
    batch_count = (total_docs + BATCH_SIZE - 1) // BATCH_SIZE  # ceiling division
    for i in tqdm(range(0, total_docs, BATCH_SIZE), total=batch_count, desc="Procesare batch-uri FAISS"):
        batch = docs[i:i + BATCH_SIZE]
        faiss_db = process_document_batch(batch, embeddings, faiss_db)
        
        # Eliberăm memoria explicit după fiecare batch
        if i % (BATCH_SIZE * 10) == 0 and i > 0:
            import gc
            gc.collect()
    
    # Salvăm baza FAISS
    FAISS_FOLDER.mkdir(parents=True, exist_ok=True)
    faiss_db.save_local(str(FAISS_FOLDER))
    print(f"[4/4] ✅ FAISS salvat în: {FAISS_FOLDER}")

# === MAIN ===
def main():
    start_time = time.time()
    print(f"📁 Căutăm fișiere .txt în: {BASE_FOLDER}")
    
    all_txt_files = find_txt_files(BASE_FOLDER)
    file_count = len(all_txt_files)
    print(f"✅ Găsite {file_count} fișiere .txt.")
    
    if file_count == 0:
        print(f"⚠️ Nu s-au găsit fișiere .txt în {BASE_FOLDER}. Verifică calea și încearcă din nou.")
        return
    
    unique_files = remove_exact_duplicates(all_txt_files)
    
    documents = load_and_split_documents(unique_files)
    doc_count = len(documents)
    print(f"✅ Documente împărțite: {doc_count} bucăți de text.")
    
    if doc_count == 0:
        print("⚠️ Nu s-au putut încărca sau împărți documente. Verifică fișierele și încearcă din nou.")
        return
    
    print("🔧 Inițializăm embeddings...")
    # Încercăm noua versiune a HuggingFaceEmbeddings
    try:
        from langchain_huggingface import HuggingFaceEmbeddings as HFEmbeddings
        embeddings = HFEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
            model_kwargs={'device': 'cuda' if os.environ.get('USE_CUDA', '0') == '1' else 'cpu'}
        )
        print("    ✅ Folosim langchain_huggingface (versiunea nouă)")
    except ImportError:
        # Fallback la versiunea veche
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-MiniLM-L3-v2",
            model_kwargs={'device': 'cuda' if os.environ.get('USE_CUDA', '0') == '1' else 'cpu'}
        )
        print("    ⚠️ Folosim langchain_community.embeddings (deprecated) - consideră actualizarea la langchain_huggingface")
    
    build_faiss_index(documents, embeddings)
    
    total_time = time.time() - start_time
    minutes = total_time / 60
    hours = minutes / 60
    
    if hours >= 1:
        time_str = f"{round(total_time, 2)} secunde ({round(minutes, 2)} minute / {round(hours, 2)} ore)"
    else:
        time_str = f"{round(total_time, 2)} secunde ({round(minutes, 2)} minute)"
    
    print(f"⏱️ Timp total: {time_str}")
    print("✅ Procesare completă!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Proces întrerupt de utilizator.")
    except Exception as e:
        print(f"\n❌ Eroare neașteptată: {e}")
        import traceback
        traceback.print_exc()