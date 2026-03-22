import os
import time
import hashlib
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import gc

# === CONFIG ===
MODULE_NAME = "training_clinic_merged"
SOURCE_FOLDER = Path("sorted_by_module") / MODULE_NAME / "converted_txt"
FAISS_FOLDER = Path("faiss_indexes") / MODULE_NAME
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"

# === FUNCȚII ===
def find_txt_files(folder):
    return list(folder.rglob("*.txt"))

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def remove_exact_duplicates(file_paths):
    hashes = {}
    unique = []
    for path in tqdm(file_paths, desc="[1/4] Eliminăm duplicate exacte"):
        file_hash = hash_file(path)
        if file_hash not in hashes:
            hashes[file_hash] = path
            unique.append(path)
        else:
            print(f"⚠️  Duplicat: {path.name} ≈ {hashes[file_hash].name}")
    return unique

def load_and_split_documents(file_paths):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    documents = []
    for path in tqdm(file_paths, desc="[2/4] Încărcăm fișierele"):
        try:
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            documents.extend(text_splitter.split_documents(docs))
        except Exception as e:
            print(f"    ⚠️ Eroare la {path.name}: {e}")
    return documents

def build_faiss_index(docs, embeddings):
    print("[3/4] Construim FAISS index...")
    db = FAISS.from_documents(docs, embeddings)
    FAISS_FOLDER.mkdir(parents=True, exist_ok=True)
    db.save_local(str(FAISS_FOLDER))
    print(f"[4/4] ✅ FAISS salvat în: {FAISS_FOLDER}")

# === EXECUȚIE ===
def main():
    start = time.time()
    print(f"📁 Căutăm fișiere .txt în: {SOURCE_FOLDER}")
    all_txt_files = find_txt_files(SOURCE_FOLDER)
    print(f"✅ Găsite {len(all_txt_files)} fișiere .txt.")

    unique_files = remove_exact_duplicates(all_txt_files)
    docs = load_and_split_documents(unique_files)
    print(f"✅ Total bucăți text: {len(docs)}")

    print("🔧 Inițializăm HuggingFaceEmbeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    build_faiss_index(docs, embeddings)

    print(f"⏱️ Timp total: {round(time.time() - start, 2)} secunde")

if __name__ == "__main__":
    main()
