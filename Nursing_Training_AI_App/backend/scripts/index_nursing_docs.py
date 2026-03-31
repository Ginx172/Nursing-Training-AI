"""
Document Indexing Pipeline - Indexeaza toate documentele de nursing in FAISS
Proceseaza PDF-uri si DOCX-uri din E-Books, extrage text, chunk-uieste, embedded, indexeaza.

Usage:
    python scripts/index_nursing_docs.py [--source-dir "J:/E-Books/........................._nursing"]
    python scripts/index_nursing_docs.py --dry-run  (doar numara fisierele)
"""

import os
import sys
import json
import pickle
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ---- Config ----
DEFAULT_SOURCE = r"J:\E-Books\........................._nursing"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "..", "Healthcare_Knowledge_Base", "FAISS_Indexes")
CHUNK_SIZE = 400  # words per chunk
CHUNK_OVERLAP = 50  # words overlap
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 256  # embeddings per batch
INDEX_NAME = "nursing_docs_full"


def extract_text_pdf(filepath: str) -> str:
    """Extrage text dintr-un PDF"""
    try:
        import pypdf
        reader = pypdf.PdfReader(filepath)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        return "\n".join(text_parts)
    except Exception as e:
        print(f"  WARN: PDF failed {Path(filepath).name}: {e}")
        return ""


def extract_text_docx(filepath: str) -> str:
    """Extrage text dintr-un DOCX"""
    try:
        import docx
        doc = docx.Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        print(f"  WARN: DOCX failed {Path(filepath).name}: {e}")
        return ""


def extract_text_doc(filepath: str) -> str:
    """Extrage text dintr-un DOC (legacy) - best effort"""
    try:
        # antiword sau textract nu sunt disponibile pe Windows
        # Incercam sa citim ca text brut
        with open(filepath, 'rb') as f:
            raw = f.read()
        # Extrage doar printable ASCII/UTF-8
        text = raw.decode('utf-8', errors='ignore')
        # Filtreaza junk
        lines = []
        for line in text.split('\n'):
            clean = ''.join(c for c in line if c.isprintable() or c in '\n\t')
            if len(clean.strip()) > 20:
                lines.append(clean.strip())
        return "\n".join(lines)
    except Exception as e:
        print(f"  WARN: DOC failed {Path(filepath).name}: {e}")
        return ""


def chunk_text(text: str, source: str, folder: str) -> List[Dict]:
    """Imparte textul in chunks cu overlap"""
    words = text.split()
    if len(words) < 20:
        return []

    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
        chunk_words = words[i:i + CHUNK_SIZE]
        if len(chunk_words) < 20:
            continue
        chunk_text = " ".join(chunk_words)
        chunks.append({
            "text": chunk_text,
            "source": source,
            "folder": folder,
            "metadata": {
                "filename": source,
                "folder": folder,
                "chunk_index": len(chunks),
                "word_count": len(chunk_words),
            }
        })
    return chunks


def find_documents(source_dir: str) -> List[Dict]:
    """Gaseste toate documentele procesabile"""
    docs = []
    for root, dirs, files in os.walk(source_dir):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        rel_folder = os.path.relpath(root, source_dir)

        for f in files:
            ext = f.lower().rsplit('.', 1)[-1] if '.' in f else ''
            if ext in ('pdf', 'docx', 'doc'):
                filepath = os.path.join(root, f)
                # Skip temp files
                if f.startswith('~$'):
                    continue
                docs.append({
                    "path": filepath,
                    "name": f,
                    "ext": ext,
                    "folder": rel_folder,
                })
    return docs


def main():
    parser = argparse.ArgumentParser(description="Index nursing documents into FAISS")
    parser.add_argument("--source-dir", default=DEFAULT_SOURCE, help="Source directory")
    parser.add_argument("--dry-run", action="store_true", help="Only count files, don't process")
    parser.add_argument("--limit", type=int, default=0, help="Process only N files (0=all)")
    args = parser.parse_args()

    source_dir = args.source_dir
    print(f"=== Nursing Document Indexing Pipeline ===")
    print(f"Source: {source_dir}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # Find documents
    docs = find_documents(source_dir)
    print(f"Found {len(docs)} documents:")
    by_ext = {}
    for d in docs:
        by_ext[d['ext']] = by_ext.get(d['ext'], 0) + 1
    for ext, count in sorted(by_ext.items()):
        print(f"  .{ext}: {count}")

    if args.dry_run:
        print("\n[DRY RUN] Exiting without processing.")
        return

    if args.limit > 0:
        docs = docs[:args.limit]
        print(f"\nLimited to {args.limit} documents")

    # Load embedding model
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Model loaded.")

    # Process documents
    all_chunks = []
    processed = 0
    failed = 0
    start_time = time.time()

    for i, doc in enumerate(docs):
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed
            eta = (len(docs) - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1}/{len(docs)}] {processed} processed, {failed} failed, "
                  f"{len(all_chunks)} chunks, ETA: {eta/60:.1f} min")

        try:
            if doc['ext'] == 'pdf':
                text = extract_text_pdf(doc['path'])
            elif doc['ext'] == 'docx':
                text = extract_text_docx(doc['path'])
            elif doc['ext'] == 'doc':
                text = extract_text_doc(doc['path'])
            else:
                continue

            if not text or len(text.split()) < 30:
                failed += 1
                continue

            chunks = chunk_text(text, doc['name'], doc['folder'])
            all_chunks.extend(chunks)
            processed += 1

        except Exception as e:
            failed += 1
            print(f"  ERROR: {doc['name']}: {e}")

    elapsed = time.time() - start_time
    print(f"\n=== Extraction Complete ===")
    print(f"Processed: {processed}/{len(docs)} documents")
    print(f"Failed: {failed}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Time: {elapsed:.1f}s")

    if not all_chunks:
        print("No chunks to index. Exiting.")
        return

    # Generate embeddings
    print(f"\nGenerating embeddings ({len(all_chunks)} chunks, batch_size={BATCH_SIZE})...")
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, batch_size=BATCH_SIZE, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    # Build FAISS index
    print(f"\nBuilding FAISS index (dim={embeddings.shape[1]})...")
    index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner Product = cosine after normalization
    index.add(embeddings)

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    index_path = os.path.join(OUTPUT_DIR, f"{INDEX_NAME}.index")
    chunks_path = os.path.join(OUTPUT_DIR, f"{INDEX_NAME}_chunks.pkl")

    faiss.write_index(index, index_path)
    with open(chunks_path, "wb") as f:
        pickle.dump(all_chunks, f)

    # Stats
    stats = {
        "index_name": INDEX_NAME,
        "source_dir": source_dir,
        "documents_processed": processed,
        "documents_failed": failed,
        "total_chunks": len(all_chunks),
        "embedding_dim": embeddings.shape[1],
        "index_size_mb": round(os.path.getsize(index_path) / 1024 / 1024, 1),
        "chunks_size_mb": round(os.path.getsize(chunks_path) / 1024 / 1024, 1),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_seconds": round(elapsed, 1),
    }
    stats_path = os.path.join(OUTPUT_DIR, f"{INDEX_NAME}_stats.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\n=== DONE ===")
    print(f"Index: {index_path} ({stats['index_size_mb']} MB)")
    print(f"Chunks: {chunks_path} ({stats['chunks_size_mb']} MB)")
    print(f"Stats: {stats_path}")
    print(f"Total time: {elapsed/60:.1f} minutes")


if __name__ == "__main__":
    main()
