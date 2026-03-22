import os
import time
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# Configurații
BATCH_FOLDER = "batches_clinical_governance/batch_001"
INDEX_SAVE_PATH = "faiss_indexes/clinical_governance_merged_batch_001"
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"

# ⁣Inițializăm embeddărul
print("Inițializăm HuggingFaceEmbeddings...")
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

# ⁣Căutăm fișiere .txt
print(f"\ud83d\udd0d Căutăm fișiere .txt în: {BATCH_FOLDER}")
txt_files = [os.path.join(BATCH_FOLDER, f) for f in os.listdir(BATCH_FOLDER) if f.endswith(".txt")]
print(f"\u2705 Găsite {len(txt_files)} fișiere .txt.")

if not txt_files:
    raise ValueError("Nu s-au găsit fișiere .txt pentru procesare.")

# ⁣Încărcăm și împreăm documentele
all_documents = []
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

print("\ud83d\udcc4 Procesăm fișiere:")
for file_path in tqdm(txt_files):
    try:
        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        split_docs = text_splitter.split_documents(docs)
        all_documents.extend(split_docs)
    except Exception as e:
        print(f"\u26a0\ufe0f Eroare la procesarea {file_path}: {e}")

# ⁣Construim FAISS index
print(f"\u2699\ufe0f Construim FAISS index cu {len(all_documents)} bucăți de text...")
start_time = time.time()
db = FAISS.from_documents(all_documents, embeddings)
db.save_local(INDEX_SAVE_PATH)

print(f"\u2705 Index FAISS salvat în {INDEX_SAVE_PATH}")
print(f"\u23f1\ufe0f Timp total: {time.time() - start_time:.2f} secunde")
