import os
import time
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# === CONFIG ===
MODULE_NAME = "Leadership"
BASE_FOLDER = Path("sorted_by_module") / MODULE_NAME
FAISS_FOLDER = Path("faiss_indexes") / MODULE_NAME

# === UTILITY FUNCTIONS ===
def find_txt_files(folder):
    return list(folder.rglob("*.txt"))

def load_and_split_documents(file_paths):
    print("[1/2] Loading and splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = []

    for path in tqdm(file_paths, desc="    Processing"):
        try:
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            documents.extend(text_splitter.split_documents(docs))
        except Exception as e:
            print(f"    ⚠️ Error processing {path.name}: {e}")
    return documents

def build_faiss_index(docs, embeddings):
    print("[2/2] Building FAISS index...")
    db = FAISS.from_documents(docs, embeddings)
    FAISS_FOLDER.mkdir(parents=True, exist_ok=True)
    db.save_local(str(FAISS_FOLDER))
    print(f"✅ FAISS index saved to: {FAISS_FOLDER}")

# === MAIN EXECUTION ===
start = time.time()
print(f"📁 Scanning for .txt files in: {BASE_FOLDER}")
txt_files = find_txt_files(BASE_FOLDER)
print(f"✅ Found {len(txt_files)} .txt files.")

documents = load_and_split_documents(txt_files)
print(f"✅ Split into {len(documents)} chunks.")

print("🔧 Initializing embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
build_faiss_index(documents, embeddings)

print(f"⏱️ Total time: {round(time.time() - start, 2)} seconds")
