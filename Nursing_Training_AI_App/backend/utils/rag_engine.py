import os
import re
import hashlib
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import chromadb
from sentence_transformers import SentenceTransformer


class RAGEngine:
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 100
    COLLECTION_NAME = "nursing_knowledge"

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "data", "vectordb")
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        print("Loading embedding model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model ready.")

    def chunk_text(self, text, source=""):
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {3,}", " ", text)
        if len(text) < 50:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            if end < len(text):
                lp = text.rfind(".", start + self.CHUNK_SIZE // 2, end)
                ln = text.rfind("\n", start + self.CHUNK_SIZE // 2, end)
                bp = max(lp, ln)
                if bp > start:
                    end = bp + 1
            chunk = text[start:end].strip()
            if len(chunk) > 30:
                cid = hashlib.md5(f"{source}:{start}:{chunk[:50]}".encode()).hexdigest()
                chunks.append({"id": cid, "text": chunk, "source": source, "start_pos": start})
            start = end - self.CHUNK_OVERLAP
        return chunks

    def index_text(self, text, source, metadata=None):
        chunks = self.chunk_text(text, source)
        if not chunks:
            return 0
        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        embeddings = self.model.encode(documents).tolist()
        metadatas = []
        for c in chunks:
            m = {"source": c["source"], "start_pos": c["start_pos"]}
            if metadata:
                m.update(metadata)
            metadatas.append(m)
        bs = 100
        for i in range(0, len(ids), bs):
            self.collection.upsert(
                ids=ids[i:i+bs], documents=documents[i:i+bs],
                embeddings=embeddings[i:i+bs], metadatas=metadatas[i:i+bs]
            )
        return len(chunks)

    def index_file(self, file_path, metadata=None):
        from utils.document_reader import DocumentReader
        text = DocumentReader.read(file_path)
        if not text:
            return 0
        source = os.path.basename(file_path)
        fm = {"file_path": file_path}
        if metadata:
            fm.update(metadata)
        return self.index_text(text, source, fm)

    def index_directory(self, directory, metadata=None):
        from utils.document_reader import DocumentReader
        stats = {"files_indexed": 0, "total_chunks": 0, "errors": 0}
        path = Path(directory)
        files = sorted([
            f for f in path.rglob("*")
            if f.is_file() and f.suffix.lower() in DocumentReader.SUPPORTED_FORMATS
            and not f.name.startswith("~")
        ])
        print(f"Found {len(files)} supported files in {directory}")
        for i, file in enumerate(files, 1):
            try:
                rel = file.relative_to(path)
                topic = str(rel.parent) if str(rel.parent) != "." else "general"
                fm = {"topic": topic}
                if metadata:
                    fm.update(metadata)
                n = self.index_file(str(file), fm)
                if n > 0:
                    stats["files_indexed"] += 1
                    stats["total_chunks"] += n
                    if i % 10 == 0 or n > 50:
                        print(f"  [{i}/{len(files)}] {file.name} -> {n} chunks")
            except Exception as e:
                stats["errors"] += 1
                if "PyCryptodome" not in str(e):
                    print(f"  ERROR: {file.name}: {e}")
        return stats

    def search(self, query, n_results=5, topic=None):
        qe = self.model.encode([query]).tolist()
        wf = None
        if topic:
            wf = {"topic": {"$" + "eq": topic}}
        results = self.collection.query(
            query_embeddings=qe, n_results=n_results,
            where=wf, include=["documents", "metadatas", "distances"]
        )
        matches = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0]
            ):
                matches.append({
                    "text": doc, "source": meta.get("source", "unknown"),
                    "topic": meta.get("topic", "general"), "relevance": round(1 - dist, 4)
                })
        return matches

    def get_context_for_prompt(self, query, n_results=5):
        matches = self.search(query, n_results)
        if not matches:
            return "No relevant context found."
        parts = []
        for i, m in enumerate(matches, 1):
            parts.append(f"[Source {i}: {m['source']} | Topic: {m['topic']} | Relevance: {m['relevance']}]\n{m['text']}")
        return "\n\n---\n\n".join(parts)

    def get_stats(self):
        return {"total_chunks": self.collection.count(), "collection": self.COLLECTION_NAME}


if __name__ == "__main__":
    print("=" * 60)
    print("RAG Engine - Quick Test")
    print("=" * 60)
    rag = RAGEngine()
    stats = rag.get_stats()
    print(f"Current chunks in DB: {stats['total_chunks']}")
    test_file = r"J:\E-Books\........................._nursing\Nursing Interview\.....Questions_Ideal Answers on Nursing Interviews.DOCX"
    if os.path.exists(test_file):
        print("\nIndexing test file...")
        n = rag.index_file(test_file, {"topic": "interview"})
        print(f"Indexed {n} chunks")
        print("\nSearch: How to handle aggressive patient")
        results = rag.search("How to handle aggressive patient in A and E", n_results=3)
        for r in results:
            print(f"\n  [{r['relevance']}] {r['source']}")
            print(f"  {r['text'][:150]}...")
    print(f"\nFinal stats: {rag.get_stats()}")
