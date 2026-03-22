"""
Script pentru construirea indexului RAG din surse externe (E-Books).
Acesta scanează directorul specificat în EXTERNAL_KNOWLEDGE_BASE_PATH,
extrage textul din PDF/Text, generează embeddings și salvează indexul FAISS local.
"""

import os
import sys
import glob
import pickle
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
from tqdm import tqdm

# Adaugă calea către backend pentru importuri
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

# Configurare logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Încearcă să imporți bibliotecile necesare
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import pypdf
except ImportError as e:
    logger.error(f"Lipsesc biblioteci necesare: {e}")
    logger.error("Te rog rulează: pip install sentence-transformers faiss-cpu pypdf")
    sys.exit(1)

# Configurare
EXTERNAL_PATH = r"J:\E-Books\........................._nursing"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Nursing_Interviews_AI_model", "Healthcare_Knowledge_Base", "FAISS_Indexes")
MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def ensure_dirs():
    """Asigură că directoarele de output există"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"Creat director output: {OUTPUT_DIR}")

def extract_text_from_pdf(file_path: str) -> str:
    """Extrage text din fișier PDF"""
    try:
        text = ""
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.warning(f"Eroare la citirea PDF {file_path}: {e}")
        return ""

def extract_text_from_file(file_path: str) -> str:
    """Extrage text din fișier text/markdown"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Eroare la citirea fișierului {file_path}: {e}")
        return ""

def create_chunks(text: str, source: str, topic: str, metadata: Dict = None) -> List[Dict]:
    """Împarte textul în chunks"""
    chunks = []
    if not text:
        return chunks
        
    words = text.split()
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk_words = words[i : i + CHUNK_SIZE]
        chunk_text = " ".join(chunk_words)
        
        if len(chunk_text) < 50:  # Ignoră chunks prea mici
            continue
            
        chunks.append({
            "content": chunk_text,
            "source": source,
            "topic": topic,
            "metadata": metadata or {}
        })
    return chunks

def build_index():
    """Funcția principală de construire a indexului"""
    ensure_dirs()
    
    logger.info(f"🚀 Începere scanare director: {EXTERNAL_PATH}")
    
    if not os.path.exists(EXTERNAL_PATH):
        logger.error(f"❌ Calea externă nu există: {EXTERNAL_PATH}")
        return

    # Inițializare model
    logger.info(f"⏳ Încărcare model embedding: {MODEL_NAME}...")
    embedder = SentenceTransformer(MODEL_NAME)
    
    all_chunks = []
    
    # Scanare recursivă
    # Folosim os.walk pentru a naviga prin subfoldere (Topics)
    for root, dirs, files in os.walk(EXTERNAL_PATH):
        # Determină topicul din numele folderului
        rel_path = os.path.relpath(root, EXTERNAL_PATH)
        topic = "General"
        if rel_path != ".":
            # Folosește primul nivel de folder ca Topic principal
            topic = rel_path.split(os.sep)[0]
            
        # Skip directoare irelevante
        if topic.startswith("."): 
            continue
            
        logger.info(f"📂 Procesare Topic: {topic} ({len(files)} fișiere)")
        
        for file in files:
            file_path = os.path.join(root, file)
            ext = file.lower().split('.')[-1]
            
            text = ""
            if ext == 'pdf':
                text = extract_text_from_pdf(file_path)
            elif ext in ['txt', 'md', 'docx']: # Docx suport ar necesita python-docx, dar lăsăm txt momentan
                text = extract_text_from_file(file_path)
            else:
                continue
                
            if text:
                chunks = create_chunks(
                    text, 
                    source=file, 
                    topic=topic, 
                    metadata={"path": file_path, "filename": file}
                )
                all_chunks.extend(chunks)

    logger.info(f"✅ Total chunks generate: {len(all_chunks)}")
    
    if not all_chunks:
        logger.warning("⚠️ Nu s-au găsit date pentru indexare.")
        return

    # Generare embeddings
    logger.info("⏳ Generare embeddings (poate dura)...")
    
    # Procesare în batch-uri pentru a nu umple memoria
    batch_size = 32
    embeddings = []
    
    for i in tqdm(range(0, len(all_chunks), batch_size)):
        batch_chunks = [c["content"] for c in all_chunks[i : i + batch_size]]
        batch_embeddings = embedder.encode(batch_chunks)
        embeddings.append(batch_embeddings)
        
    embeddings_np = np.vstack(embeddings)
    
    # Creare index FAISS
    logger.info("⏳ Creare index FAISS...")
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    
    # Salvare
    index_path = os.path.join(OUTPUT_DIR, "healthcare_materials.index")
    chunks_path = os.path.join(OUTPUT_DIR, "healthcare_chunks.pkl")
    
    faiss.write_index(index, index_path)
    with open(chunks_path, 'wb') as f:
        pickle.dump(all_chunks, f)
        
    logger.info(f"🎉 Index salvat cu succes la:\n  - {index_path}\n  - {chunks_path}")

if __name__ == "__main__":
    build_index()
