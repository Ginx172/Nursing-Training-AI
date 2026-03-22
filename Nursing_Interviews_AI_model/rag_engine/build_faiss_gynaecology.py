import os
import time
import shutil
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import hashlib

# === CONFIGURARE ===
MODULE_NAME = "Gynaecology"
BASE_FOLDER = Path("sorted_by_module") / MODULE_NAME
FAISS_FOLDER = Path("faiss_indexes") / MODULE_NAME

# === FUNCȚII UTILE ===
def find_txt_files(folder):
    return list(folder.rglob("*.txt"))

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def remove_fast_duplicates(file_paths):
    print("[1/5] Eliminăm duplicate rapide (exacte + hashuri parțiale)...")
    seen = {}
    unique_files = []
    for path in tqdm(file_paths):
        try:
            size = os.path.getsize(path)
            with open(path, "rb") as f:
                content = f.read(10000)  # doar începutul fișierului
            hash_val = hashlib.md5(content + str(size).encode()).hexdigest()
            if hash_val not in seen:
                seen[hash_val] = path
                unique_files.append(path)
            else:
                print(f"    ⚠️  Duplicat rapid: {path.name} — șters")
                path.unlink()
        except Exception as e:
            print(f"    ⚠️  Eroare la citirea {path.name}: {e}")
    return unique_files

def load_documents(file_paths):
    print("[2/5] Încărcăm fișierele și le împărțim...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []
    for path in tqdm(file_paths):
        try:
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            documents.extend(text_splitter.split_documents(docs))
        except Exception as e:
            print(f"    ⚠️  Eroare la procesarea {path.name}: {e}")
    return documents

def build_faiss_index(docs, embeddings):
    print("[3/5] Construim FAISS index...")
    db = FAISS.from_documents(docs, embeddings)
    FAISS_FOLDER.mkdir(parents=True, exist_ok=True)
    db.save_local(str(FAISS_FOLDER))
    print(f"[4/5] ✅ Index FAISS salvat în: {FAISS_FOLDER}")

# === EXECUȚIE ===
start = time.time()
print(f"📁 Căutăm fișiere .txt în: {BASE_FOLDER}")
all_txt_files = find_txt_files(BASE_FOLDER)
print(f"✅ Găsite {len(all_txt_files)} fișiere .txt.")

unique_files = remove_fast_duplicates(all_txt_files)
documents = load_documents(unique_files)
print(f"✅ Documente împărțite în {len(documents)} bucăți de text.")

print("[5/5] Inițializăm embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
build_faiss_index(documents, embeddings)

print(f"⏱️ Timp total: {round(time.time() - start, 2)} secunde")
