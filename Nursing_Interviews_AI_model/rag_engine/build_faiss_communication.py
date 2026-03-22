import os
import time
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import hashlib

# === CONFIG ===
MODULE_NAME = "communication"
BASE_FOLDER = Path("sorted_by_module") / MODULE_NAME
FAISS_FOLDER = Path("faiss_indexes") / MODULE_NAME

# === UTILITY FUNCTIONS ===
def find_txt_files(folder):
    return list(folder.rglob("*.txt"))

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def remove_exact_duplicates(file_paths):
    hashes = {}
    unique_files = []
    for path in tqdm(file_paths, desc="[1/4] Eliminăm duplicate exacte"):
        file_hash = hash_file(path)
        if file_hash not in hashes:
            hashes[file_hash] = path
            unique_files.append(path)
        else:
            print(f"    ⚠️  Duplicat eliminat: {path.name} (duplicat cu {hashes[file_hash].name})")
            path.unlink()
    return unique_files

def load_and_split_documents(file_paths):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []
    for path in tqdm(file_paths, desc="[2/4] Încărcăm fișierele"):
        try:
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            documents.extend(text_splitter.split_documents(docs))
        except Exception as e:
            print(f"    ⚠️  Eroare la încărcarea {path.name}: {e}")
    return documents

def build_faiss_index(docs, embeddings):
    print("[3/4] Construim FAISS index...")
    db = FAISS.from_documents(docs, embeddings)
    FAISS_FOLDER.mkdir(parents=True, exist_ok=True)
    db.save_local(str(FAISS_FOLDER))
    print(f"[4/4] ✅ Index FAISS salvat în: {FAISS_FOLDER}")

# === EXECUTION ===
start_time = time.time()
print(f"📁 Căutăm fișiere .txt în: {BASE_FOLDER}")

if not BASE_FOLDER.exists():
    print(f"❌ Folderul nu există: {BASE_FOLDER}")
    exit()

all_txt_files = find_txt_files(BASE_FOLDER)
if not all_txt_files:
    print("❌ Nu s-au găsit fișiere .txt pentru procesare.")
    exit()

print(f"✅ Găsite {len(all_txt_files)} fișiere .txt.")
unique_files = remove_exact_duplicates(all_txt_files)
documents = load_and_split_documents(unique_files)
print(f"✅ Documente împărțite în {len(documents)} bucăți de text.")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
build_faiss_index(documents, embeddings)

print(f"⏱️ Timp total: {round(time.time() - start_time, 2)} secunde")
