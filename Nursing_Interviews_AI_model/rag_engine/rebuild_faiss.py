import os
import faiss
import pickle
import numpy as np
from tqdm import tqdm
from docx import Document
from sentence_transformers import SentenceTransformer
import torch

# === CONFIG ===
SOURCE_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\Private Nursing Homes\converted_txt"
DOCX_PATH = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\Private Nursing Homes\Clinical lead.docx"
DEST_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\elderly_care"
# ==============

os.makedirs(DEST_FOLDER, exist_ok=True)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# === LOAD TEXT FUNCTION ===
def load_all_texts(folder, extra_docx=None):
    texts = []

    # Load .txt files
    for fname in os.listdir(folder):
        if fname.lower().endswith(".txt"):
            path = os.path.join(folder, fname)
            with open(path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
                paragraphs = [p.strip() for p in content.split("\n") if len(p.strip()) > 30]
                texts.extend(paragraphs)

    # Load optional Word document
    if extra_docx and os.path.exists(extra_docx):
        doc = Document(extra_docx)
        doc_paragraphs = [p.text.strip() for p in doc.paragraphs if len(p.text.strip()) > 30]
        texts.extend(doc_paragraphs)
        print(f"📝 {len(doc_paragraphs)} paragrafe adăugate din {os.path.basename(extra_docx)}")

    return texts

# === EXECUTION ===
print("📂 Citim fișierele...")
texts = load_all_texts(SOURCE_FOLDER, extra_docx=DOCX_PATH)
print(f"✅ {len(texts)} fragmente de text încărcate.")

# Embeddings
print("🔍 Calculăm embeddings...")
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

# FAISS build
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings).astype("float32"))

# Save index + texts
faiss.write_index(index, os.path.join(DEST_FOLDER, "index.faiss"))
with open(os.path.join(DEST_FOLDER, "index.pkl"), "wb") as f:
    pickle.dump(texts, f)

print(f"\n✅ FAISS salvat în: {DEST_FOLDER}")
