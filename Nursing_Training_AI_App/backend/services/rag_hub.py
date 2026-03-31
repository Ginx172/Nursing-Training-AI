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

        # Init FAISS (via existing rag_service)
        try:
            from services.rag_service import rag_service
            self._rag_service = rag_service
            self._faiss_available = rag_service.is_initialized
            if self._faiss_available:
                logger.info("RAG Hub: FAISS engine available")
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
        if source_filter in (None, "pdf") and self._faiss_available:
            try:
                from services.rag_service import RAGQuery
                faiss_query = RAGQuery(query=query, top_k=k, min_score=0.5)
                if specialty:
                    faiss_query.specialty = specialty
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Suntem deja in async context - nu putem folosi run_until_complete
                    # FAISS search e sync intern, apelam direct
                    faiss_results = self._search_faiss_sync(query, k, specialty)
                else:
                    faiss_results = loop.run_until_complete(
                        self._rag_service.search(faiss_query)
                    )
                for r in faiss_results:
                    results.append({
                        "content": r.content if hasattr(r, "content") else r.get("content", ""),
                        "score": r.score if hasattr(r, "score") else r.get("score", 0),
                        "source": r.source if hasattr(r, "source") else r.get("source", ""),
                        "source_type": "pdf",
                        "metadata": r.metadata if hasattr(r, "metadata") else r.get("metadata", {}),
                    })
            except Exception as e:
                logger.warning(f"RAG Hub: FAISS search failed: {e}")

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
            # Acces direct la indexul FAISS fara async wrapper
            if not _embed_available or _embedder is None:
                return []
            query_embedding = _embedder.encode([query])[0]
            all_results = []
            for index_name, index_data in self._rag_service.indexes.items():
                faiss_index = index_data.get("index")
                chunks = index_data.get("chunks", [])
                if faiss_index is None or not chunks:
                    continue
                import numpy as np
                query_vec = np.array([query_embedding]).astype("float32")
                distances, indices = faiss_index.search(query_vec, min(k, len(chunks)))
                for dist, idx in zip(distances[0], indices[0]):
                    if idx < 0 or idx >= len(chunks):
                        continue
                    chunk = chunks[idx]
                    score = max(0, 1 - dist / 2)
                    all_results.append({
                        "content": chunk.get("content", ""),
                        "score": float(score),
                        "source": chunk.get("source", index_name),
                        "metadata": chunk.get("metadata", {}),
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

        if self._faiss_available and self._rag_service:
            for name, data in getattr(self._rag_service, "indexes", {}).items():
                chunks = data.get("chunks", [])
                stats["faiss"]["indexes"][name] = {"chunks": len(chunks)}

        return stats


# Singleton - initializat lazy la primul import
rag_hub = RAGHub()
