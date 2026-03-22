import os
import glob
import time
import torch
import logging
import numpy as np
import gc
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Optional
from dataclasses import dataclass

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer

# Configurare logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build_index.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurare parametri
@dataclass
class Config:
    # Directoare
    SOURCE_FOLDER: str = "sorted_by_module/interview_nhs"
    SAVE_PATH: str = "faiss_indexes/interview_nhs"
    
    # Parametri de procesare text
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Parametri pentru GPU
    BATCH_SIZE: int = 64  # Pentru GPU NVIDIA 1070 8GB
    MAX_SEQ_LENGTH: int = 384  # Limită pentru a evita OOM errors
    
    # Model
    MODEL_NAME: str = "all-MiniLM-L6-v2"

# Inițializăm configurația
config = Config()

def get_gpu_info() -> Dict:
    """
    Obține informații despre GPU-ul disponibil.
    
    Returns:
        Dict: Informații despre GPU
    """
    if torch.cuda.is_available():
        gpu_count = torch.cuda.device_count()
        current_device = torch.cuda.current_device()
        device_name = torch.cuda.get_device_name(current_device)
        total_memory = torch.cuda.get_device_properties(current_device).total_memory / 1024**3  # GB
        allocated_memory = torch.cuda.memory_allocated(current_device) / 1024**3  # GB
        
        return {
            "available": True,
            "count": gpu_count,
            "current_device": current_device,
            "name": device_name,
            "total_memory_gb": round(total_memory, 2),
            "allocated_memory_gb": round(allocated_memory, 2),
            "free_memory_gb": round(total_memory - allocated_memory, 2)
        }
    else:
        return {"available": False}

def get_device() -> str:
    """
    Detectează și returnează dispozitivul disponibil (CUDA sau CPU).
    
    Returns:
        str: "cuda" sau "cpu"
    """
    if torch.cuda.is_available():
        device = "cuda"
        gpu_info = get_gpu_info()
        logger.info(f"GPU detectat: {gpu_info['name']} cu {gpu_info['total_memory_gb']} GB VRAM")
        
        # Optimizăm batch size în funcție de memoria disponibilă
        free_memory = gpu_info["free_memory_gb"]
        if free_memory < 4:
            config.BATCH_SIZE = 32
            logger.info(f"Memorie GPU limitată. Batch size optimizat la {config.BATCH_SIZE}")
        elif free_memory > 6:
            config.BATCH_SIZE = 128
            logger.info(f"Memorie GPU generoasă. Batch size optimizat la {config.BATCH_SIZE}")
    else:
        device = "cpu"
        logger.info("GPU nedisponibil. Se folosește CPU.")
        config.BATCH_SIZE = 16  # Batch size mai mic pentru CPU
    
    return device

def optimize_for_gpu():
    """
    Optimizează resursele pentru GPU.
    """
    if torch.cuda.is_available():
        # Eliberăm memoria GPU
        torch.cuda.empty_cache()
        gc.collect()
        
        # Setăm modul deterministic pentru reproductibilitate
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def load_txt_documents(folder_path: str) -> List[Document]:
    """
    Încarcă toate documentele text dintr-un director.
    
    Args:
        folder_path: Calea către directorul cu fișiere text
        
    Returns:
        List[Document]: Lista documentelor încărcate
    """
    path = Path(folder_path)
    if not path.exists():
        logger.error(f"Directorul {folder_path} nu există!")
        return []
    
    documents = []
    file_paths = list(path.glob("*.txt"))
    
    if not file_paths:
        logger.warning(f"Nu s-au găsit fișiere .txt în {folder_path}")
        return []
    
    # Folosim tqdm pentru progres vizual    
    for file_path in tqdm(file_paths, desc="📄 Încărcare fișiere"):
        try:
            # Încercăm mai multe codificări
            encodings = ["utf-8", "latin-1", "cp1252"]
            loaded = False
            
            for encoding in encodings:
                try:
                    loader = TextLoader(str(file_path), encoding=encoding)
                    file_docs = loader.load()
                    documents.extend(file_docs)
                    loaded = True
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"Eroare la {file_path.name}: {str(e)}")
                    break
                    
            if not loaded:
                logger.warning(f"⚠️ Nu s-a putut citi {file_path.name} cu nicio codificare cunoscută")
                
        except Exception as e:
            logger.error(f"⚠️ Eroare generală la {file_path.name}: {str(e)}")
    
    return documents

def split_documents(documents: List[Document]) -> List[Document]:
    """
    Împarte documentele în fragmente mai mici folosind RecursiveCharacterTextSplitter.
    
    Args:
        documents: Lista documentelor de împărțit
        
    Returns:
        List[Document]: Lista fragmentelor rezultate
    """
    if not documents:
        logger.warning("Nu există documente de împărțit")
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )
    
    chunks = splitter.split_documents(documents)
    return chunks

def initialize_embedding_model(device: str) -> HuggingFaceEmbeddings:
    """
    Inițializează modelul de embedding cu optimizări pentru GPU.
    
    Args:
        device: Dispozitivul pe care rulează modelul ("cuda" sau "cpu")
        
    Returns:
        HuggingFaceEmbeddings: Modelul de embedding inițializat
    """
    model_kwargs = {
        "device": device
    }
    
    # Pentru GPU, adăugăm optimizări suplimentare
    if device == "cuda":
        model_kwargs.update({
            "use_auth_token": False,
            "trust_remote_code": True,
        })
    
    embedding_model = HuggingFaceEmbeddings(
        model_name=config.MODEL_NAME,
        model_kwargs=model_kwargs,
        encode_kwargs={
            "normalize_embeddings": True,  # Normalizare pentru FAISS
            "batch_size": config.BATCH_SIZE,
            "max_length": config.MAX_SEQ_LENGTH,
            "show_progress_bar": False  # Folosim propriul nostru progress bar
        }
    )
    
    # Încărcăm modelul direct ca SentenceTransformer pentru a accesa mai multe opțiuni
    # embedding_model.client = SentenceTransformer(config.MODEL_NAME, device=device)
    
    return embedding_model

def batched_embedding_with_gpu_optimization(
    embedding_model: HuggingFaceEmbeddings, 
    chunks: List[Document],
    batch_size: int
) -> tuple:
    """
    Generează embeddings pe loturi cu optimizări pentru GPU.
    
    Args:
        embedding_model: Modelul de embedding
        chunks: Documentele de procesat
        batch_size: Dimensiunea lotului
        
    Returns:
        tuple: (embeddings, chunks procesate)
    """
    all_embeddings = []
    processed_chunks = []
    
    # Extragem conținutul textual din documente
    texts = [doc.page_content for doc in chunks]
    
    # Procesăm pe loturi pentru a evita supraîncărcarea memoriei GPU
    for i in tqdm(range(0, len(texts), batch_size), desc="🧠 Generare embeddings"):
        batch_texts = texts[i:i + batch_size]
        batch_chunks = chunks[i:i + batch_size]
        
        try:
            # Generăm embeddings pentru lot
            batch_embeddings = embedding_model.embed_documents(batch_texts)
            
            # Adăugăm la rezultate
            all_embeddings.extend(batch_embeddings)
            processed_chunks.extend(batch_chunks)
            
            # Dacă folosim GPU, eliberăm cache-ul pentru a evita memory leaks
            if torch.cuda.is_available() and i % (batch_size * 10) == 0:
                torch.cuda.empty_cache()
                
        except Exception as e:
            logger.error(f"Eroare la generarea embeddings pentru lotul {i}-{i+batch_size}: {str(e)}")
            logger.error(f"Se omite acest lot și se continuă cu următorul")
    
    return all_embeddings, processed_chunks

def validate_index(index_path: str, embedding_model: HuggingFaceEmbeddings) -> bool:
    """
    Validează că indexul FAISS a fost creat corect.
    
    Args:
        index_path: Calea către index
        embedding_model: Modelul de embedding
        
    Returns:
        bool: True dacă indexul este valid
    """
    try:
        # Încărcăm indexul
        vectorstore = FAISS.load_local(index_path, embedding_model)
        
        # Verificăm dacă indexul are vectori
        if hasattr(vectorstore, 'index') and vectorstore.index.ntotal > 0:
            logger.info(f"✅ Index valid cu {vectorstore.index.ntotal} vectori")
            
            # Test simplu de căutare
            test_query = "nursing interview"
            results = vectorstore.similarity_search(test_query, k=1)
            if results:
                logger.info("✅ Căutare de test reușită")
                return True
            else:
                logger.warning("⚠️ Căutarea de test nu a returnat rezultate")
                return False
        else:
            logger.warning("⚠️ Indexul pare gol!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Eroare la validarea indexului: {str(e)}")
        return False

def build_index():
    """
    Construiește indexul FAISS cu optimizări pentru GPU.
    """
    start_time = time.time()
    
    try:
        logger.info("=" * 50)
        logger.info("🚀 START CONSTRUIRE INDEX FAISS")
        logger.info("=" * 50)
        
        # Detectăm dispozitivul și optimizăm pentru GPU
        device = get_device()
        logger.info(f"🖥️ Folosim dispozitivul: {device.upper()}")
        
        if device == "cuda":
            optimize_for_gpu()
            gpu_info = get_gpu_info()
            logger.info(f"GPU: {gpu_info['name']} | VRAM: {gpu_info['total_memory_gb']} GB | Liber: {gpu_info['free_memory_gb']} GB")
        
        # Pasul 1: Încărcăm documentele
        logger.info("📥 Încărcăm documentele...")
        raw_docs = load_txt_documents(config.SOURCE_FOLDER)
        if not raw_docs:
            logger.error("❌ Nu s-au putut încărca documentele. Procesul se oprește.")
            return
        logger.info(f"✅ {len(raw_docs)} documente încărcate")
        
        # Pasul 2: Împărțim documentele în fragmente
        logger.info("✂️ Segmentăm documentele...")
        chunks = split_documents(raw_docs)
        if not chunks:
            logger.error("❌ Nu s-au putut genera fragmente. Procesul se oprește.")
            return
        logger.info(f"✅ {len(chunks)} fragmente de text generate")
        
        # Pasul 3: Inițializăm modelul de embedding
        logger.info("🔎 Inițializăm modelul de embedding...")
        embedding_model = initialize_embedding_model(device)
        logger.info(f"✅ Model inițializat: {config.MODEL_NAME} pe {device}")
        
        # Pasul 4: Generăm embeddings pe loturi
        logger.info("📡 Generăm embeddings și construim indexul FAISS...")
        all_embeddings, processed_chunks = batched_embedding_with_gpu_optimization(
            embedding_model, 
            chunks, 
            config.BATCH_SIZE
        )
        
        if not all_embeddings or len(all_embeddings) == 0:
            logger.error("❌ Nu s-au putut genera embeddings. Procesul se oprește.")
            return
        
        logger.info(f"✅ Generate {len(all_embeddings)} embeddings")
        
        # Pasul 5: Construim și salvăm indexul FAISS
        save_path = Path(config.SAVE_PATH)
        save_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"💾 Construim și salvăm indexul FAISS în {save_path}...")
        try:
            vectorstore = FAISS.from_embeddings(
                text_embeddings=all_embeddings,
                texts=processed_chunks,
                embedding=embedding_model
            )
            vectorstore.save_local(str(save_path))
            logger.info(f"✅ Index FAISS salvat în: {save_path}")
        except Exception as e:
            logger.error(f"❌ Eroare la salvarea indexului: {str(e)}")
            return
        
        # Pasul 6: Validăm indexul
        if validate_index(str(save_path), embedding_model):
            logger.info("✅ Indexul a fost validat cu succes!")
        else:
            logger.warning("⚠️ Validarea indexului a eșuat!")
        
        # Eliberăm memoria
        if device == "cuda":
            torch.cuda.empty_cache()
            gc.collect()
        
        # Calculăm timpul de execuție
        end_time = time.time()
        elapsed_time = end_time - start_time
        mins, secs = divmod(elapsed_time, 60)
        logger.info(f"⏱️ Timp total: {int(mins)} minute și {int(secs)} secunde")
        logger.info("=" * 50)
        logger.info("🏁 FINAL CONSTRUIRE INDEX FAISS")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Eroare neașteptată: {str(e)}")
        logger.exception("Detalii excepție:")

if __name__ == "__main__":
    build_index()
