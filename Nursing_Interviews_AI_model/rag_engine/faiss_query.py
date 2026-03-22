import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

BASE_PATH = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes"

def load_index(category):
    index_path = os.path.join(BASE_PATH, category, "index.faiss")
    pkl_path = os.path.join(BASE_PATH, category, "index.pkl")

    index = faiss.read_index(index_path)

    with open(pkl_path, "rb") as f:
        texts = pickle.load(f)

    return index, texts

def query_faiss(category, question, top_k=5):
    index, texts = load_index(category)
    embedding = model.encode([question])
    distances, indices = index.search(np.array(embedding).astype("float32"), top_k)
    results = [texts[i] for i in indices[0]]
    return results
