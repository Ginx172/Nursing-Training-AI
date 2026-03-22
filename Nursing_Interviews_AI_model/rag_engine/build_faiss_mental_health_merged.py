import os
import time
from pathlib import Path
from tqdm import tqdm
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# === CONFIG ===
MODULE_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\mental_health_merged"
INDEX_OUTPUT_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\mental_health_merged"
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"

# === START ===
start_time = time.time()
print("[INFO] Inițializăm HuggingFaceEmbeddings...")
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

print(f"[INFO] Căutăm fișiere .txt în: {MODULE_FOLDER}")
txt_files = list(Path(MODULE_FOLDER).glob("*.txt"))
print(f"[INFO] Găsite {len(txt_files)} fișiere .txt.")

all_documents = []
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

print("[INFO] Procesăm fișiere:")
for file_path in tqdm(txt_files, desc="Procesare fișiere", unit="file"):
    try:
        loader = TextLoader(str(file_path), encoding="utf-8")
        documents = loader.load()
        split_docs = text_splitter.split_documents(documents)
        all_documents.extend(split_docs)
    except Exception as e:
        print(f"[WARN] Eroare la procesarea fișierului {file_path.name}: {e}")

print(f"[INFO] Construim FAISS index cu {len(all_documents)} bucăți de text...")
db = FAISS.from_documents(all_documents, embeddings)
os.makedirs(INDEX_OUTPUT_FOLDER, exist_ok=True)
db.save_local(INDEX_OUTPUT_FOLDER)

elapsed = time.time() - start_time
print(f"✅ Index FAISS salvat în {INDEX_OUTPUT_FOLDER}")
print(f"⏱️ Timp total: {elapsed:.2f} secunde")
