
import os
import time
from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"
BATCH_FOLDER = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/batches_clinical_governance/batch_001")
OUTPUT_INDEX = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/faiss_indexes/clinical_governance_merged_batch_001")

print(f"[INFO] Inițializăm HuggingFaceEmbeddings...")
embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

print(f"[INFO] Căutăm fișiere .txt în: {BATCH_FOLDER}")
txt_files = list(BATCH_FOLDER.glob("*.txt"))
print(f"[INFO] Găsite {len(txt_files)} fișiere .txt.")

if not txt_files:
    raise ValueError("Nu s-au găsit fișiere .txt în folderul specificat.")

all_documents = []
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

start_time = time.time()

for file in tqdm(txt_files, desc="[INFO] Procesăm fișiere"):
    try:
        loader = TextLoader(file, encoding="utf-8")
        documents = loader.load()
        chunks = splitter.split_documents(documents)
        all_documents.extend(chunks)
    except Exception as e:
        print(f"[AVERTISMENT] Eroare la procesarea fișierului {file.name}: {e}")

print(f"[INFO] Construim FAISS index cu {len(all_documents)} bucăți de text...")
db = FAISS.from_documents(all_documents, embeddings)
db.save_local(str(OUTPUT_INDEX))

duration = time.time() - start_time
print(f"[INFO] FAISS index salvat în {OUTPUT_INDEX}")
print(f"[INFO] Timp total: {duration:.2f} secunde")
