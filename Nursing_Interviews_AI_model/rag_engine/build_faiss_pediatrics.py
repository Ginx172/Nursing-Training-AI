import os
import time
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# === CONFIG ===
MODULE_NAME = "Pediatrics"
BASE_FOLDER = Path("sorted_by_module") / MODULE_NAME
FAISS_FOLDER = Path("faiss_indexes") / MODULE_NAME
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"

# === FUNCTIONS ===
def find_txt_files(folder):
    return list(folder.rglob("*.txt"))

def load_and_split_documents(file_paths):
    print("[1/2] Loading and splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []
    for path in tqdm(file_paths):
        try:
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            documents.extend(text_splitter.split_documents(docs))
        except Exception as e:
            print(f"    ⚠️ Error processing {path.name}: {e}")
    print(f"✅ Split into {len(documents)} chunks.")
    return documents

def build_faiss_index(docs, embeddings):
    print("[2/2] Building FAISS index...")
    db = FAISS.from_documents(docs, embeddings)
    FAISS_FOLDER.mkdir(parents=True, exist_ok=True)
    db.save_local(str(FAISS_FOLDER))
    print(f"✅ FAISS index saved to: {FAISS_FOLDER}")

# === RUN ===
start = time.time()
print(f"📁 Looking for .txt files in: {BASE_FOLDER}")
all_txt_files = find_txt_files(BASE_FOLDER)
print(f"✅ Found {len(all_txt_files)} .txt files.")

documents = load_and_split_documents(all_txt_files)

print("🔧 Initializing embeddings...")
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
build_faiss_index(documents, embeddings)

print(f"⏱️ Total time: {round(time.time() - start, 2)} seconds")
