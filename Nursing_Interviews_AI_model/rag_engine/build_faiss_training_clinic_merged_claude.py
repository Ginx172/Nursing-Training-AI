import os
import time
import hashlib
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import gc
import argparse

# === CONFIG ===
MODULE_NAME = "training_clinic_merged"
SOURCE_FOLDER = Path("sorted_by_module") / MODULE_NAME
FAISS_FOLDER = Path("faiss_indexes") / MODULE_NAME
CHECKPOINT_DIR = Path("checkpoints") / MODULE_NAME
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MODEL_NAME = "sentence-transformers/paraphrase-MiniLM-L3-v2"
BATCH_SIZE = 50  # Number of files to process before saving checkpoint

# === FUNCTIONS ===
def create_checkpoint_dir():
    """Create checkpoint directory if it doesn't exist"""
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    
def save_checkpoint(stage, data, index=None):
    """Save checkpoint for current stage"""
    create_checkpoint_dir()
    
    # Save progress info
    progress = {
        'stage': stage,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'completed': index if index is not None else True
    }
    
    with open(CHECKPOINT_DIR / "progress.json", "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)
    
    # Save stage data
    if stage == "find_files":
        with open(CHECKPOINT_DIR / "files.pkl", "wb") as f:
            pickle.dump(data, f)
    elif stage == "unique_files":
        with open(CHECKPOINT_DIR / "unique_files.pkl", "wb") as f:
            pickle.dump(data, f)
    elif stage == "documents":
        with open(CHECKPOINT_DIR / "documents.pkl", "wb") as f:
            pickle.dump(data, f)
    elif stage == "processed_files":
        with open(CHECKPOINT_DIR / "processed_files.pkl", "wb") as f:
            pickle.dump(data, f)
    
    print(f"✅ Checkpoint saved: {stage}" + (f" (index: {index})" if index is not None else ""))

def load_checkpoint():
    """Load latest checkpoint if available"""
    if not (CHECKPOINT_DIR / "progress.json").exists():
        return None, None
    
    with open(CHECKPOINT_DIR / "progress.json", "r", encoding="utf-8") as f:
        progress = json.load(f)
    
    stage = progress['stage']
    completed = progress['completed']
    
    if stage == "find_files" and (CHECKPOINT_DIR / "files.pkl").exists():
        with open(CHECKPOINT_DIR / "files.pkl", "rb") as f:
            data = pickle.load(f)
    elif stage == "unique_files" and (CHECKPOINT_DIR / "unique_files.pkl").exists():
        with open(CHECKPOINT_DIR / "unique_files.pkl", "rb") as f:
            data = pickle.load(f)
    elif stage == "documents" and (CHECKPOINT_DIR / "documents.pkl").exists():
        with open(CHECKPOINT_DIR / "documents.pkl", "rb") as f:
            data = pickle.load(f)
    elif stage == "processed_files" and (CHECKPOINT_DIR / "processed_files.pkl").exists():
        with open(CHECKPOINT_DIR / "processed_files.pkl", "rb") as f:
            data = pickle.load(f)
    else:
        return None, None
        
    return stage, data
def estimate_time(start_time, current_index, total_items):
    """Estimate remaining time based on elapsed time and progress"""
    elapsed = time.time() - start_time
    if current_index == 0:
        return "Calculating..."
    
    items_per_second = current_index / elapsed
    remaining_items = total_items - current_index
    remaining_seconds = remaining_items / items_per_second if items_per_second > 0 else 0
    
    remaining_time = timedelta(seconds=int(remaining_seconds))
    return str(remaining_time)

def find_txt_files(folder):
    """Find all .txt files in the given folder"""
    # Check if folder exists
    if not folder.exists():
        raise FileNotFoundError(f"Source folder not found: {folder}")
    return list(folder.rglob("*.txt"))

def hash_file(path):
    """Generate MD5 hash for a file"""
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def remove_exact_duplicates(file_paths):
    """Remove duplicate files based on MD5 hash"""
    hashes = {}
    unique = []
    
    for i, path in enumerate(tqdm(file_paths, desc="[1/4] Eliminarea duplicatelor exacte")):
        file_hash = hash_file(path)
        if file_hash not in hashes:
            hashes[file_hash] = path
            unique.append(path)
        else:
            print(f"⚠️  Duplicat: {path.name} ≈ {hashes[file_hash].name}")
        
        # Save checkpoint after each batch
        if (i + 1) % BATCH_SIZE == 0 or i == len(file_paths) - 1:
            save_checkpoint("processed_files", unique, i)
            
    return unique

def load_and_split_documents(file_paths, start_idx=0):
    """Load and split text documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    documents = []
    start_time = time.time()
    total_files = len(file_paths)
    
    # Continue from where we left off
    if start_idx > 0:
        print(f"Resuming from file {start_idx} of {total_files}")
    
    for i, path in enumerate(file_paths[start_idx:], start_idx):
        try:
            # Show progress percentage and estimated time
            progress_pct = (i / total_files) * 100
            eta = estimate_time(start_time, i, total_files)
            
            desc = f"[2/4] Încărcarea fișierelor: {progress_pct:.1f}% | ETA: {eta}"
            tqdm.write(f"\r{desc}", end="")
            
            loader = TextLoader(path, encoding="utf-8")
            docs = loader.load()
            split_docs = text_splitter.split_documents(docs)
            documents.extend(split_docs)
            
            # Save checkpoint after batch processing
            if (i + 1) % BATCH_SIZE == 0 or i == len(file_paths) - 1:
                save_checkpoint("documents", documents, i)
                
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                loader = TextLoader(path, encoding="latin-1")
                docs = loader.load()
                split_docs = text_splitter.split_documents(docs)
                documents.extend(split_docs)
            except Exception as e:
                print(f"\n    ⚠️ Eroare la {path.name}: {e}")
        except Exception as e:
            print(f"\n    ⚠️ Eroare la {path.name}: {e}")
    
    print(f"\n✅ Procesate {len(documents)} fragmente de text din {len(file_paths)} fișiere")
    return documents

def build_faiss_index(docs, embeddings):
    """Build FAISS index from documents and embeddings"""
    if not docs:
        raise ValueError("Nu există documente pentru indexare. Verificați fișierele sursă.")
        
    print("[3/4] Construirea indexului FAISS...")
    
    # Create smaller batches for processing to avoid memory issues
    batch_size = 500  # Process 500 documents at a time
    total_docs = len(docs)
    
    # Initialize empty index for first batch
    if total_docs > 0:
        print(f"Procesăm primul lot de {min(batch_size, total_docs)} documente")
        first_batch = docs[:min(batch_size, total_docs)]
        db = FAISS.from_documents(first_batch, embeddings)
        
        # Process remaining documents in batches
        for i in range(batch_size, total_docs, batch_size):
            end_idx = min(i + batch_size, total_docs)
            batch = docs[i:end_idx]
            print(f"Procesăm lotul {i//batch_size + 1}: documentele {i}-{end_idx} din {total_docs}")
            
            # Create temporary index and merge
            temp_db = FAISS.from_documents(batch, embeddings)
            db.merge_from(temp_db)
            
            # Force garbage collection
            del temp_db
            gc.collect()
            
            # Save intermediate index
            checkpoint_path = CHECKPOINT_DIR / f"faiss_checkpoint_{end_idx}"
            checkpoint_path.mkdir(parents=True, exist_ok=True)
            db.save_local(str(checkpoint_path))
            print(f"✅ Checkpoint indexare salvat: {checkpoint_path}")
    
    # Save final index
    FAISS_FOLDER.mkdir(parents=True, exist_ok=True)
    db.save_local(str(FAISS_FOLDER))
    print(f"[4/4] ✅ Index FAISS salvat în: {FAISS_FOLDER}")
    
    # Save completion checkpoint
    save_checkpoint("completed", None)
    
    return db

# === EXECUTION ===
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Build FAISS index with checkpoint support")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--restart", action="store_true", help="Restart process from beginning")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, 
                        help=f"Number of files to process before checkpoint (default: {BATCH_SIZE})")
    return parser.parse_args()

def main():
    args = parse_arguments()
    global BATCH_SIZE
    BATCH_SIZE = args.batch_size
    
    start = time.time()
    
    # Handle resume vs restart
    checkpoint_stage = None
    checkpoint_data = None
    
    if args.restart:
        print("Restarting process from beginning...")
    elif args.resume:
        checkpoint_stage, checkpoint_data = load_checkpoint()
        if checkpoint_stage:
            print(f"Resuming from checkpoint: {checkpoint_stage}")
        else:
            print("No valid checkpoint found. Starting from beginning.")
    else:
        # Check if checkpoint exists
        potential_stage, _ = load_checkpoint()
        if potential_stage:
            print(f"Checkpoints detected. Use --resume to continue or --restart to start over.")
            return
    
    # Track overall progress
    all_txt_files = []
    unique_files = []
    docs = []
    last_processed_idx = 0
    
    # Stage 1: Find files (if not resuming or resuming from beginning)
    if checkpoint_stage is None or checkpoint_stage == "find_files":
        # Ensure SOURCE_FOLDER exists
        if not SOURCE_FOLDER.exists():
            print(f"❌ Eroare: Folderul sursă nu există: {SOURCE_FOLDER}")
            print("Verificați calea și încercați din nou.")
            return
            
        print(f"📁 Căutăm fișiere .txt în: {SOURCE_FOLDER}")
        all_txt_files = find_txt_files(SOURCE_FOLDER)
        
        if not all_txt_files:
            print(f"❌ Nu s-au găsit fișiere .txt în {SOURCE_FOLDER}")
            return
            
        print(f"✅ Găsite {len(all_txt_files)} fișiere .txt.")
        save_checkpoint("find_files", all_txt_files)
        
        # Move to next stage
        checkpoint_stage = "unique_files"
    else:
        # Load all_txt_files if needed for next stages
        if checkpoint_stage in ["unique_files", "documents", "processed_files"]:
            with open(CHECKPOINT_DIR / "files.pkl", "rb") as f:
                all_txt_files = pickle.load(f)
    
    # Stage 2: Remove duplicates
    if checkpoint_stage == "unique_files":
        if checkpoint_data:
            unique_files = checkpoint_data
        else:
            unique_files = remove_exact_duplicates(all_txt_files)
        
        if not unique_files:
            print("❌ Nu s-au găsit fișiere unice după deduplicare.")
            return
            
        save_checkpoint("unique_files", unique_files)
        
        # Move to next stage
        checkpoint_stage = "documents"
    elif checkpoint_stage in ["documents", "processed_files"]:
        with open(CHECKPOINT_DIR / "unique_files.pkl", "rb") as f:
            unique_files = pickle.load(f)
    
    # Stage 3: Load and split documents
    if checkpoint_stage == "documents":
        if checkpoint_data:
            docs = checkpoint_data
            # Find last processed index
            with open(CHECKPOINT_DIR / "progress.json", "r") as f:
                progress = json.load(f)
                last_processed_idx = progress.get("completed", 0) + 1  # Start from next file
        else:
            last_processed_idx = 0
            
        docs = load_and_split_documents(unique_files, last_processed_idx)
        
        if not docs:
            print("❌ Nu s-au încărcat și segmentat documente.")
            return
            
        save_checkpoint("documents", docs)
        
        # Move to next stage
        checkpoint_stage = "embeddings"
    elif checkpoint_stage == "processed_files":
        # Load documents directly from checkpoint
        with open(CHECKPOINT_DIR / "documents.pkl", "rb") as f:
            docs = pickle.load(f)
    
    # If we're here for first time or continuing from documents stage
    if checkpoint_stage == "embeddings" or checkpoint_stage == "processed_files":
        print(f"✅ Total fragmente de text: {len(docs)}")

        print("🔧 Inițializarea HuggingFaceEmbeddings...")
        try:
            embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        except Exception as e:
            print(f"❌ Eroare la inițializarea embeddings: {e}")
            print("Verificați dacă modelul este instalat și încercați din nou.")
            return

        try:
            build_faiss_index(docs, embeddings)
        except Exception as e:
            print(f"❌ Eroare la construirea indexului FAISS: {e}")
            return

        # Clear memory
        del docs
        del embeddings
        gc.collect()

    print(f"⏱️ Timp total: {round(time.time() - start, 2)} secunde")
    
    # Cleanup intermediate checkpoints if process completed successfully
    if checkpoint_stage == "completed":
        print("Procesare completă! Doriți să ștergeți checkpoint-urile intermediare? (y/n)")
        if input().lower() == 'y':
            import shutil
            shutil.rmtree(CHECKPOINT_DIR)
            print("Checkpoint-uri șterse.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcesul a fost întrerupt de utilizator.")
        print("Folosiți --resume pentru a continua de la ultimul checkpoint.")
    except Exception as e:
        print(f"\n\n❌ Eroare neașteptată: {e}")
        print("Folosiți --resume pentru a continua de la ultimul checkpoint.")
