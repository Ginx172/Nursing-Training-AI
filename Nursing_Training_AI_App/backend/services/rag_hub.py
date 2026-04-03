"""
RAG Hub - Unified Search Engine
Combina FAISS (PDF knowledge) + ChromaDB (DB questions) intr-un singur API de search.
Indexeaza intrebarile din PostgreSQL in ChromaDB pentru cautare semantica.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.config import settings

logger = logging.getLogger(__name__)

# Embedding: incercam sentence-transformers, fallback la ChromaDB default
_embedder = None
_embed_available = False
try:
    from sentence_transformers import SentenceTransformer
    _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    _embed_available = True
except Exception:
    logger.warning("sentence-transformers unavailable, ChromaDB will use default embeddings")


class RAGHub:
    """Unified RAG engine: FAISS (PDFs) + ChromaDB (DB questions)"""

    def __init__(self):
        self._faiss_available = False
        self._chroma_available = False
        self._chroma_client = None
        self._questions_collection = None
        self._questions_indexed_count = 0

        # Init FAISS (via existing rag_service - initialized at startup in main.py lifespan)
        try:
            from services.rag_service import rag_service
            self._rag_service = rag_service
            self._faiss_available = rag_service.is_initialized
            logger.info(f"RAG Hub: FAISS engine {'available' if self._faiss_available else 'loaded (pending init)'}")
        except Exception as e:
            logger.warning(f"RAG Hub: FAISS unavailable: {e}")
            self._rag_service = None

        # Init ChromaDB
        try:
            db_path = os.path.abspath(settings.RAG_CHROMADB_PATH)
            os.makedirs(db_path, exist_ok=True)
            self._chroma_client = chromadb.PersistentClient(
                path=db_path,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            self._questions_collection = self._chroma_client.get_or_create_collection(
                name=settings.RAG_QUESTIONS_COLLECTION,
                metadata={"description": "NHS nursing training questions from PostgreSQL"},
            )
            self._chroma_available = True
            self._questions_indexed_count = self._questions_collection.count()
            logger.info(f"RAG Hub: ChromaDB available ({self._questions_indexed_count} documents)")
        except Exception as e:
            logger.warning(f"RAG Hub: ChromaDB unavailable: {e}")

        # nursing_docs_full FAISS index (lazy loaded - 178MB)
        self._docs_faiss_index = None
        self._docs_faiss_chunks = None
        self._docs_index_loaded = False

    def search(
        self,
        query: str,
        k: int = 5,
        source_filter: Optional[str] = None,
        specialty: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Cautare unificata in FAISS + ChromaDB. Returneaza rezultate sortate dupa relevanta."""
        results = []

        # FAISS search (PDF knowledge)
        if source_filter in (None, "pdf") and self._rag_service:
            try:
                # Check if initialized (done at startup in main.py)
                if not self._faiss_available:
                    self._faiss_available = self._rag_service.is_initialized

                if self._faiss_available:
                    faiss_results = self._search_faiss_sync(query, k, specialty)
                    for r in faiss_results:
                        results.append({
                            "content": r.get("content", ""),
                            "score": r.get("score", 0),
                            "source": r.get("source", ""),
                            "source_type": "pdf",
                            "metadata": r.get("metadata", {}),
                        })
            except Exception as e:
                logger.warning(f"RAG Hub: FAISS search failed: {e}")

        # Nursing docs FAISS search (books - 121k chunks)
        if source_filter in (None, "pdf", "books"):
            try:
                docs_results = self._search_docs_faiss(query, k)
                results.extend(docs_results)
            except Exception as e:
                logger.warning(f"RAG Hub: Docs FAISS search failed: {e}")

        # ChromaDB search (DB questions)
        if source_filter in (None, "questions") and self._chroma_available and self._questions_collection:
            try:
                chroma_results = self._search_chroma(query, k, specialty)
                results.extend(chroma_results)
            except Exception as e:
                logger.warning(f"RAG Hub: ChromaDB search failed: {e}")

        # Sort by score descending, deduplicate by content
        seen_content = set()
        unique_results = []
        for r in sorted(results, key=lambda x: x.get("score", 0), reverse=True):
            content_key = r.get("content", "")[:200]
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(r)

        return unique_results[:k]

    def _search_faiss_sync(self, query: str, k: int, specialty: Optional[str]) -> List[Dict]:
        """Search FAISS synchronously (pentru context async)"""
        if not self._rag_service or not self._rag_service.is_initialized:
            return []
        try:
            if not _embed_available or _embedder is None:
                return []
            query_embedding = _embedder.encode([query])[0]
            import numpy as np
            query_vec = np.array([query_embedding]).astype("float32")
            all_results = []

            faiss_indexes = getattr(self._rag_service, "faiss_indexes", {})
            chunks_data = getattr(self._rag_service, "chunks_data", {})

            for index_name, faiss_index in faiss_indexes.items():
                chunks = chunks_data.get(index_name, [])
                if faiss_index is None or not chunks:
                    continue
                n_search = min(k, faiss_index.ntotal)
                if n_search == 0:
                    continue
                scores, indices = faiss_index.search(query_vec, n_search)
                for score_val, idx in zip(scores[0], indices[0]):
                    if idx < 0 or idx >= len(chunks):
                        continue
                    chunk = chunks[idx]
                    # faiss IndexFlatIP returns cosine similarity (higher = better)
                    all_results.append({
                        "content": chunk.get("text", chunk.get("content", "")),
                        "score": float(max(0, score_val)),
                        "source": chunk.get("source", index_name),
                        "metadata": chunk.get("metadata", {"index": index_name}),
                    })
            return sorted(all_results, key=lambda x: x["score"], reverse=True)[:k]
        except Exception as e:
            logger.warning(f"RAG Hub: FAISS sync search failed: {e}")
            return []

    def _search_chroma(self, query: str, k: int, specialty: Optional[str] = None) -> List[Dict]:
        """Search ChromaDB"""
        where_filter = None
        if specialty:
            where_filter = {"specialty": specialty}

        query_params = {"query_texts": [query], "n_results": k}
        if _embed_available and _embedder is not None:
            embedding = _embedder.encode([query]).tolist()
            query_params = {"query_embeddings": embedding, "n_results": k}
        if where_filter:
            query_params["where"] = where_filter

        chroma_result = self._questions_collection.query(**query_params)

        results = []
        if chroma_result and chroma_result.get("documents"):
            docs = chroma_result["documents"][0]
            distances = chroma_result.get("distances", [[]])[0]
            metadatas = chroma_result.get("metadatas", [[]])[0]
            ids = chroma_result.get("ids", [[]])[0]

            for i, doc in enumerate(docs):
                dist = distances[i] if i < len(distances) else 1.0
                score = max(0, 1 - dist / 2)
                meta = metadatas[i] if i < len(metadatas) else {}
                results.append({
                    "content": doc,
                    "score": float(score),
                    "source": f"question_{meta.get('question_id', ids[i] if i < len(ids) else 'unknown')}",
                    "source_type": "question_bank",
                    "metadata": meta,
                })

        return results

    def _load_docs_index(self):
        """Lazy load nursing_docs_full FAISS index (178MB + 595MB chunks)"""
        if self._docs_index_loaded:
            return
        try:
            import faiss as _faiss
            import pickle
            from pathlib import Path

            base = Path(settings.KNOWLEDGE_BASE_PATH) if hasattr(settings, 'KNOWLEDGE_BASE_PATH') else Path("../Healthcare_Knowledge_Base")
            # Cauta in mai multe locatii
            for search_path in [
                base / "FAISS_Indexes",
                Path("../Healthcare_Knowledge_Base/FAISS_Indexes"),
                Path("../../Healthcare_Knowledge_Base/FAISS_Indexes"),
                Path("../Nursing_Training_AI_App/Healthcare_Knowledge_Base/FAISS_Indexes"),
            ]:
                idx_file = search_path / "nursing_docs_full.index"
                chunks_file = search_path / "nursing_docs_full_chunks.pkl"
                if idx_file.exists() and chunks_file.exists():
                    logger.info(f"RAG Hub: Loading nursing_docs_full from {search_path}...")
                    self._docs_faiss_index = _faiss.read_index(str(idx_file))
                    with open(chunks_file, "rb") as f:
                        self._docs_faiss_chunks = pickle.load(f)
                    self._docs_index_loaded = True
                    logger.info(f"RAG Hub: nursing_docs_full loaded ({len(self._docs_faiss_chunks)} chunks)")
                    return
            logger.warning("RAG Hub: nursing_docs_full index not found")
        except Exception as e:
            logger.warning(f"RAG Hub: Failed to load nursing_docs_full: {e}")

    def _search_docs_faiss(self, query: str, k: int) -> List[Dict]:
        """Search in nursing_docs_full FAISS index"""
        if not self._docs_index_loaded:
            self._load_docs_index()
        if not self._docs_faiss_index or not self._docs_faiss_chunks:
            return []
        try:
            if not _embed_available or _embedder is None:
                return []
            import numpy as np
            query_embedding = _embedder.encode([query])[0]
            query_vec = np.array([query_embedding]).astype("float32")
            import faiss as _faiss
            _faiss.normalize_L2(query_vec)

            n_search = min(k, self._docs_faiss_index.ntotal)
            scores, indices = self._docs_faiss_index.search(query_vec, n_search)
            results = []
            for score_val, idx in zip(scores[0], indices[0]):
                if idx < 0 or idx >= len(self._docs_faiss_chunks):
                    continue
                chunk = self._docs_faiss_chunks[idx]
                results.append({
                    "content": chunk.get("text", ""),
                    "score": float(max(0, score_val)),
                    "source": chunk.get("source", "nursing_docs"),
                    "source_type": "book",
                    "metadata": chunk.get("metadata", {}),
                })
            return results
        except Exception as e:
            logger.warning(f"RAG Hub: docs FAISS search failed: {e}")
            return []

    def build_context(self, query: str, specialty: Optional[str] = None, band: Optional[str] = None) -> str:
        """Construieste context text din rezultatele RAG pentru AI evaluation"""
        results = self.search(query, k=5, specialty=specialty)
        if not results:
            return "No relevant context found in knowledge base."

        context_parts = []
        for i, r in enumerate(results, 1):
            source_label = "Clinical Protocol" if r.get("source_type") == "pdf" else "Question Bank"
            context_parts.append(
                f"[{source_label} - relevance {r['score']:.2f}]\n{r['content'][:500]}"
            )
        return "\n\n---\n\n".join(context_parts)

    def index_db_questions(self, db_session, batch_size: int = 500) -> Dict[str, Any]:
        """Indexeaza intrebarile din PostgreSQL in ChromaDB"""
        if not self._chroma_available or not self._questions_collection:
            return {"success": False, "error": "ChromaDB not available"}

        from models.training import Question
        start_time = datetime.utcnow()

        questions = db_session.query(Question).filter(Question.is_active == True).all()
        total = len(questions)

        if total == 0:
            return {"success": True, "indexed": 0, "message": "No active questions in DB"}

        # Sterge colectia existenta si recreeaza
        try:
            self._chroma_client.delete_collection(settings.RAG_QUESTIONS_COLLECTION)
        except Exception:
            pass
        self._questions_collection = self._chroma_client.get_or_create_collection(
            name=settings.RAG_QUESTIONS_COLLECTION,
            metadata={"description": "NHS nursing training questions from PostgreSQL"},
        )

        indexed = 0
        errors = 0

        for i in range(0, total, batch_size):
            batch = questions[i:i + batch_size]
            ids = []
            documents = []
            metadatas = []
            embeddings = None

            for q in batch:
                doc_text = f"{q.title}\n{q.question_text}"
                if q.correct_answer:
                    doc_text += f"\nCorrect Answer: {q.correct_answer}"
                if q.explanation:
                    doc_text += f"\nExplanation: {q.explanation}"

                ids.append(f"q_{q.id}")
                documents.append(doc_text[:2000])
                metadatas.append({
                    "question_id": q.id,
                    "nhs_band": q.nhs_band or "",
                    "specialty": q.specialization or "",
                    "difficulty": q.difficulty_level.value if q.difficulty_level else "",
                    "question_type": q.question_type.value if q.question_type else "",
                })

            try:
                if _embed_available and _embedder is not None:
                    embeddings = _embedder.encode(documents).tolist()
                    self._questions_collection.add(
                        ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
                    )
                else:
                    self._questions_collection.add(
                        ids=ids, documents=documents, metadatas=metadatas
                    )
                indexed += len(batch)
            except Exception as e:
                errors += len(batch)
                logger.error(f"RAG Hub: batch indexing error: {e}")

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        self._questions_indexed_count = self._questions_collection.count()

        return {
            "success": True,
            "total_questions": total,
            "indexed": indexed,
            "errors": errors,
            "elapsed_seconds": round(elapsed, 1),
            "collection_count": self._questions_indexed_count,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Statistici despre indexurile disponibile"""
        stats = {
            "faiss": {"available": self._faiss_available, "indexes": {}},
            "chromadb": {
                "available": self._chroma_available,
                "questions_indexed": self._questions_indexed_count,
                "db_path": settings.RAG_CHROMADB_PATH,
            },
        }

        if self._rag_service and self._rag_service.is_initialized:
            stats["faiss"]["available"] = True
            chunks_data = getattr(self._rag_service, "chunks_data", {})
            faiss_indexes = getattr(self._rag_service, "faiss_indexes", {})
            for name in faiss_indexes:
                chunks = chunks_data.get(name, [])
                stats["faiss"]["indexes"][name] = {"chunks": len(chunks)}

        # nursing_docs_full stats
        stats["nursing_docs"] = {
            "loaded": self._docs_index_loaded,
            "chunks": len(self._docs_faiss_chunks) if self._docs_faiss_chunks else 0,
        }

        return stats


# Singleton - initializat lazy la primul import
rag_hub = RAGHub()
