import os
import time
import pickle
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import hashlib
import gc

# === CONFIG ===
MODULE_NAME = "interview_nhs"
SOURCE_FOLDER = Path("sorted_by_module") / MODULE_NAME
SAVE_PATH = Path("faiss_indexes") / MODULE_NAME
CHECKPOINT_FILE = Path("checkpoints") / f"{MODULE_NAME}_checkpoint.pkl"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64

# === SETUP ===
SAVE_PATH.mkdir(parents=True, exist_ok=True)
Path("checkpoints").mkdir(exist_ok=True)

# === UTILS ===
def find_txt_files(folder):
    return list(folder.rglob("*.txt"))

def hash_file(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_documents(file_paths):
    docs = []
    seen_hashes = set()
    for path in tqdm(file_paths, desc="[1/5] Încărcăm fișierele"):
        try:
            file_hash = hash_file(path)
            if file_hash in seen_hashes:
                continue
            seen_hashes.add(file_hash)
            loader = TextLoader(str(path), encoding="utf-8")
            docs.extend(loader.load())
        except Exception as e:
            print(f"⚠️ {path.name}: {e}")
    return docs

def split_documents(docs):
    print("[2/5] Segmentăm fișierele...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_documents(docs)

def save_checkpoint(chunks, i):
    with open(CHECKPOINT_FILE, "wb") as f:
        pickle.dump((chunks, i), f)

def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "rb") as f:
            return pickle.load(f)
    return [], 0

def embed_chunks(chunks, model):
    print("[3/5] Generăm embeddings...")
    texts = [doc.page_content for doc in chunks]
    embeddings = []
    total = len(texts)
    start = time.time()

    for i in tqdm(range(0, total, BATCH_SIZE), desc="[4/5] Embedding batch-uri"):
        batch = texts[i:i+BATCH_SIZE]
        emb = model.encode(batch, show_progress_bar=False)
        embeddings.extend(emb)
        save_checkpoint(chunks, i + BATCH_SIZE)
        gc.collect()

        elapsed = time.time() - start
        pct = min((i + BATCH_SIZE) / total, 1.0)
        remaining = (elapsed / pct) - elapsed
        print(f" ⏱️ Progres: {pct*100:.2f}% | Timp rămas estimat: {int(remaining // 60)}m {int(remaining % 60)}s")

    return embeddings

def build_faiss_index():
    print("🚀 Începem construcția FAISS (CPU)...")
    model = SentenceTransformer(MODEL_NAME)

    all_files = find_txt_files(SOURCE_FOLDER)
    documents = load_documents(all_files)
    chunks = split_documents(documents)

    saved_chunks, start_index = load_checkpoint()
    chunks = chunks if not saved_chunks else saved_chunks
    embeddings = embed_chunks(chunks[start_index:], model)

    print("[5/5] Salvăm indexul FAISS...")
    vectorstore = FAISS.from_embeddings(embeddings, chunks[start_index:], model)
    vectorstore.save_local(str(SAVE_PATH))
    print(f"✅ Index FAISS salvat în: {SAVE_PATH}")

if __name__ == "__main__":
    start_time = time.time()
    build_faiss_index()
    print(f"⏱️ Timp total: {round(time.time() - start_time, 2)} secunde")
