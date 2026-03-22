import os
import logging
import sys
import locale
from pathlib import Path
import pickle
from typing import List, Dict, Any, Optional
import time
from tqdm import tqdm

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# Setăm codificarea pentru consola Windows
if sys.platform == 'win32':
    # Forțăm codificarea UTF-8 pentru output
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configurare logging cu codificare UTF-8 explicită
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("build_index.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurare directoare utilizând Path pentru compatibilitate cross-platform
SOURCE_FOLDER = Path(r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\interview_nhs")
INDEX_SAVE_PATH = Path(r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\interview_nhs")

# Configurări parametri
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def initialize_embedding_model(model_name: str = EMBEDDING_MODEL) -> HuggingFaceEmbeddings:
    """
    Inițializează și returnează modelul de embedding.
    
    Args:
        model_name: Numele modelului de embedding
        
    Returns:
        Modelul de embedding inițializat
    """
    logger.info(f"Initializare model embedding: {model_name}")
    return HuggingFaceEmbeddings(model_name=model_name)

def load_txt_documents(folder_path: Path) -> List[Document]:
    """
    Încarcă toate documentele text din directorul specificat.
    
    Args:
        folder_path: Calea către directorul cu fișiere text
        
    Returns:
        Lista de documente încărcate
    """
    logger.info(f"Incarcare documente din: {folder_path}")
    docs = []
    
    # Verificare existență director
    if not folder_path.exists():
        logger.error(f"Directorul {folder_path} nu exista!")
        raise FileNotFoundError(f"Directorul {folder_path} nu exista!")
    
    # Obținem lista de fișiere
    files = [f for f in folder_path.glob("*.txt")]
    if not files:
        logger.warning(f"Nu s-au gasit fisiere .txt in {folder_path}")
        return []
    
    # Încărcăm fiecare fișier cu progres vizibil
    for file_path in tqdm(files, desc="Incarcare fisiere"):
        try:
            # Încercăm mai multe codificări
            encodings = ["utf-8", "latin-1", "cp1252"]
            for encoding in encodings:
                try:
                    text = file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    if encoding == encodings[-1]:  # Ultima încercare a eșuat
                        logger.warning(f"Nu s-a putut citi {file_path} cu nicio codificare cunoscuta")
                        continue
                except Exception as e:
                    logger.error(f"Eroare la citirea {file_path}: {str(e)}")
                    continue
            
            # Adăugăm mai multe metadate utile
            metadata = {
                "source": file_path.name,
                "path": str(file_path),
                "size_bytes": file_path.stat().st_size,
                "created": time.ctime(file_path.stat().st_ctime)
            }
            docs.append(Document(page_content=text, metadata=metadata))
            
        except Exception as e:
            logger.error(f"Eroare neasteptata la procesarea {file_path}: {str(e)}")
    
    logger.info(f"Incarcate {len(docs)} documente")
    return docs

def split_documents(documents: List[Document], chunk_size: int = CHUNK_SIZE, 
                   chunk_overlap: int = CHUNK_OVERLAP) -> List[Document]:
    """
    Împarte documentele în fragmente mai mici.
    
    Args:
        documents: Lista de documente de împărțit
        chunk_size: Dimensiunea fragmentelor
        chunk_overlap: Suprapunerea între fragmente
        
    Returns:
        Lista de fragmente rezultate
    """
    if not documents:
        logger.warning("Nu exista documente de impartit")
        return []
    
    logger.info(f"Impartire documente in fragmente (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False
    )
    
    chunks = splitter.split_documents(documents)
    logger.info(f"Documente impartite in {len(chunks)} fragmente")
    return chunks

def save_faiss_index(chunks: List[Document], path: Path, 
                    embedding_model: Optional[HuggingFaceEmbeddings] = None) -> None:
    """
    Generează și salvează indexul FAISS și metadata.
    
    Args:
        chunks: Lista de fragmente pentru indexare
        path: Calea unde va fi salvat indexul
        embedding_model: Modelul de embedding (optional)
    """
    if not chunks:
        logger.error("Nu exista fragmente pentru indexare")
        return
    
    if embedding_model is None:
        embedding_model = initialize_embedding_model()
    
    # Creare director dacă nu există
    path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Generare embeddings si construire index FAISS...")
    try:
        # Construim indexul cu progres vizibil folosind functionalitatea FAISS
        db = FAISS.from_documents(chunks, embedding_model)
        
        # Salvăm indexul
        db.save_local(str(path))
        logger.info(f"Index FAISS salvat in: {path}")
        
        # Salvăm și metadatele pentru referință ulterioară
        index_metadata = {
            "document_count": len(chunks),
            "embedding_model": EMBEDDING_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "created_at": time.ctime(),
            "documents": [doc.metadata for doc in chunks]
        }
        
        metadata_path = path / "index_metadata.pkl"
        with open(metadata_path, "wb") as f:
            pickle.dump(index_metadata, f)
            
        # Salvăm și fragmentele pentru referință
        chunks_path = path / "index_chunks.pkl"
        with open(chunks_path, "wb") as f:
            pickle.dump(chunks, f)
            
        logger.info(f"Metadate si fragmente salvate in: {path}")
        
    except Exception as e:
        logger.error(f"Eroare la generarea indexului FAISS: {str(e)}")
        raise

def validate_index(index_path: Path) -> bool:
    """
    Validează că indexul a fost creat corect și poate fi încărcat.
    
    Args:
        index_path: Calea către directorul cu indexul
        
    Returns:
        True dacă indexul este valid, False altfel
    """
    logger.info(f"Validare index in: {index_path}")
    try:
        # Încercăm să încărcăm indexul
        embedding_model = initialize_embedding_model()
        index = FAISS.load_local(str(index_path), embedding_model)
        
        # Verificăm dacă indexul are elemente
        if index.index.ntotal > 0:
            logger.info(f"Index valid cu {index.index.ntotal} vectori")
            return True
        else:
            logger.warning("Index gol!")
            return False
            
    except Exception as e:
        logger.error(f"Eroare la validarea indexului: {str(e)}")
        return False

def build_index():
    """
    Funcția principală care orchestrează construirea indexului.
    """
    start_time = time.time()
    
    try:
        logger.info("======== START CONSTRUIRE INDEX ========")
        
        # Pasul 1: Încărcare documente
        raw_docs = load_txt_documents(SOURCE_FOLDER)
        if not raw_docs:
            logger.error("Nu s-au putut incarca documentele. Procesul se opreste.")
            return
        
        # Pasul 2: Împărțire în fragmente
        chunks = split_documents(raw_docs, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            logger.error("Nu s-au putut genera fragmente. Procesul se opreste.")
            return
        
        # Pasul 3: Inițializare model embedding
        embedding_model = initialize_embedding_model(EMBEDDING_MODEL)
        
        # Pasul 4: Generare și salvare index
        save_faiss_index(chunks, INDEX_SAVE_PATH, embedding_model)
        
        # Pasul 5: Validare index
        if validate_index(INDEX_SAVE_PATH):
            logger.info("Index validat cu succes!")
        else:
            logger.warning("Validarea indexului a esuat!")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Proces finalizat in {elapsed_time:.2f} secunde")
        logger.info("======== FINAL CONSTRUIRE INDEX ========")
        
    except Exception as e:
        logger.error(f"Eroare neasteptata in procesul principal: {str(e)}")
        logger.exception("Detalii exceptie:")

if __name__ == "__main__":
    build_index()