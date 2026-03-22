"""
🔍 RAG (Retrieval-Augmented Generation) Service
Serviciu pentru căutare semantică în Knowledge Base-ul medical
"""

import os
import pickle
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import asyncio
import logging
from dataclasses import dataclass
import numpy as np

# Import pentru FAISS (va fi adăugat în requirements.txt)
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available. Install with: pip install faiss-cpu")

# Import pentru Sentence Transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("Sentence Transformers not available. Install with: pip install sentence-transformers")

from core.config import settings
from core.mcp_rag_config import mcp_rag_config

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Rezultatul unei căutări RAG"""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any]
    chunk_id: int

@dataclass
class RAGQuery:
    """Query pentru serviciul RAG"""
    query_text: str
    specialty: str
    band: str
    max_results: int = 5
    min_score: float = 0.7
    include_metadata: bool = True

class RAGService:
    """Serviciul principal RAG pentru căutare în Knowledge Base"""
    
    def __init__(self):
        self.knowledge_base_path = Path(mcp_rag_config.knowledge_base_path)
        # Adaugă și path-ul către rag_engine (unde sunt indexes-urile mari)
        self.rag_engine_path = Path(mcp_rag_config.rag_engine_path) if hasattr(mcp_rag_config, 'rag_engine_path') else None
        self.faiss_indexes = {}
        self.chunks_data = {}
        self.embedder = None
        self.is_initialized = False
        
        # Configurații
        self.embedding_model = settings.RAG_EMBEDDING_MODEL
        self.chunk_size = settings.RAG_CHUNK_SIZE
        self.chunk_overlap = settings.RAG_CHUNK_OVERLAP
        
        # Cache pentru embeddings
        self.embedding_cache = {}
        
    async def initialize(self):
        """Inițializează serviciul RAG"""
        try:
            logger.info("🚀 Initializing RAG Service...")
            
            # Inițializează embedder-ul
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedder = SentenceTransformer(self.embedding_model)
                logger.info(f"✅ Embedder loaded: {self.embedding_model}")
            else:
                logger.error("❌ Sentence Transformers not available")
                return False
            
            # Încarcă indexurile FAISS existente
            await self._load_faiss_indexes()
            
            # Încarcă chunks data
            await self._load_chunks_data()
            
            self.is_initialized = True
            logger.info("✅ RAG Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing RAG Service: {str(e)}")
            return False
    
    async def _load_faiss_indexes(self):
        """Încarcă indexurile FAISS existente"""
        try:
            # Încarcă din ambele locații
            faiss_paths = [
                self.knowledge_base_path / "FAISS_Indexes",
            ]
            
            # Adaugă și Healthcare_Knowledge_Base din Nursing_Interviews_AI_model
            if self.rag_engine_path:
                # Path către Healthcare_Knowledge_Base din rag_engine parent
                alt_kb_path = self.rag_engine_path.parent / "Healthcare_Knowledge_Base" / "FAISS_Indexes"
                if alt_kb_path.exists():
                    faiss_paths.append(alt_kb_path)
            
            indexes_loaded = 0
            
            for faiss_path in faiss_paths:
                if not faiss_path.exists():
                    logger.warning(f"⚠️ FAISS_Indexes directory not found: {faiss_path}")
                    continue
                
                logger.info(f"📂 Checking FAISS indexes in: {faiss_path}")
                
                # Încarcă indexurile pentru fiecare specialitate
                specialty_configs = mcp_rag_config.specialty_configs
                
                for specialty, config in specialty_configs.items():
                    # Skip dacă deja avem index pentru această specialitate
                    if specialty in self.faiss_indexes:
                        continue
                    
                    faiss_index_name = config.get("faiss_index", "General")
                    index_file = faiss_path / f"{faiss_index_name}_materials.index"
                    chunks_file = faiss_path / f"{faiss_index_name}_chunks.pkl"
                    
                    if index_file.exists() and chunks_file.exists():
                        try:
                            # Încarcă indexul FAISS
                            if FAISS_AVAILABLE:
                                index = faiss.read_index(str(index_file))
                                self.faiss_indexes[specialty] = index
                                indexes_loaded += 1
                                logger.info(f"✅ Loaded FAISS index for {specialty} from {faiss_path}")
                            else:
                                logger.warning(f"⚠️ FAISS not available, skipping {specialty}")
                                
                        except Exception as e:
                            logger.error(f"❌ Error loading FAISS index for {specialty}: {str(e)}")
                
                # Încearcă să încarci și indexes-urile generale (healthcare_materials, Band5, Band6, etc)
                general_indexes = [
                    ("healthcare", "healthcare_materials"),
                    ("band5", "Band5_materials"),
                    ("band6", "Band6_materials"),
                    ("june25_full", "june25_full"),
                ]
                
                for index_name, file_prefix in general_indexes:
                    if index_name in self.faiss_indexes:
                        continue
                    
                    index_file = faiss_path / f"{file_prefix}.index"
                    chunks_file = faiss_path / f"{file_prefix.replace('_materials', '_chunks')}.pkl"
                    
                    if index_file.exists():
                        try:
                            if FAISS_AVAILABLE:
                                index = faiss.read_index(str(index_file))
                                self.faiss_indexes[index_name] = index
                                indexes_loaded += 1
                                logger.info(f"✅ Loaded general FAISS index: {index_name}")
                        except Exception as e:
                            logger.error(f"❌ Error loading {index_name}: {str(e)}")
            
            if indexes_loaded > 0:
                logger.info(f"🎉 Total FAISS indexes loaded: {indexes_loaded}")
            else:
                logger.warning("⚠️ No FAISS indexes found in any location")
                    
        except Exception as e:
            logger.error(f"❌ Error loading FAISS indexes: {str(e)}")
    
    async def _load_chunks_data(self):
        """Încarcă datele chunks pentru fiecare specialitate"""
        try:
            # Încarcă din ambele locații
            faiss_paths = [
                self.knowledge_base_path / "FAISS_Indexes",
            ]
            
            # Adaugă și Healthcare_Knowledge_Base din Nursing_Interviews_AI_model
            if self.rag_engine_path:
                alt_kb_path = self.rag_engine_path.parent / "Healthcare_Knowledge_Base" / "FAISS_Indexes"
                if alt_kb_path.exists():
                    faiss_paths.append(alt_kb_path)
            
            chunks_loaded = 0
            
            for faiss_path in faiss_paths:
                if not faiss_path.exists():
                    continue
                
                specialty_configs = mcp_rag_config.specialty_configs
                
                for specialty, config in specialty_configs.items():
                    # Skip dacă deja avem chunks pentru această specialitate
                    if specialty in self.chunks_data:
                        continue
                    
                    faiss_index_name = config.get("faiss_index", "General")
                    chunks_file = faiss_path / f"{faiss_index_name}_chunks.pkl"
                    
                    if chunks_file.exists():
                        try:
                            with open(chunks_file, 'rb') as f:
                                chunks_data = pickle.load(f)
                                self.chunks_data[specialty] = chunks_data
                                chunks_loaded += 1
                                logger.info(f"✅ Loaded chunks data for {specialty}: {len(chunks_data)} chunks")
                        except Exception as e:
                            logger.error(f"❌ Error loading chunks data for {specialty}: {str(e)}")
                
                # Încarcă și chunks-urile generale
                general_chunks = [
                    ("healthcare", "healthcare_chunks"),
                    ("band5", "Band5_chunks"),
                    ("band6", "Band6_chunks"),
                    ("june25_full", "june25_full_chunks"),
                ]
                
                for chunk_name, file_name in general_chunks:
                    if chunk_name in self.chunks_data:
                        continue
                    
                    chunks_file = faiss_path / f"{file_name}.pkl"
                    if chunks_file.exists():
                        try:
                            with open(chunks_file, 'rb') as f:
                                chunks_data = pickle.load(f)
                                self.chunks_data[chunk_name] = chunks_data
                                chunks_loaded += 1
                                logger.info(f"✅ Loaded general chunks: {chunk_name} - {len(chunks_data)} chunks")
                        except Exception as e:
                            logger.error(f"❌ Error loading {chunk_name} chunks: {str(e)}")
            
            if chunks_loaded > 0:
                logger.info(f"🎉 Total chunks loaded: {chunks_loaded} files")
            else:
                logger.warning("⚠️ No chunks data found in any location")
                    
        except Exception as e:
            logger.error(f"❌ Error loading chunks data: {str(e)}")
    
    async def search(self, query: RAGQuery) -> List[SearchResult]:
        """Caută în Knowledge Base folosind RAG"""
        try:
            if not self.is_initialized:
                logger.error("❌ RAG Service not initialized")
                return []
            
            if not self.embedder:
                logger.error("❌ Embedder not available")
                return []
            
            # Verifică dacă specialitatea există
            # Dacă nu găsim index specific, folosim indexes-urile generale
            index_key = query.specialty
            chunks_key = query.specialty
            
            if query.specialty not in self.faiss_indexes:
                # Încearcă să folosești indexes-urile generale
                if "healthcare" in self.faiss_indexes:
                    logger.info(f"⚠️ No specific index for {query.specialty}, using general healthcare index")
                    index_key = "healthcare"
                    chunks_key = "healthcare"
                elif "june25_full" in self.faiss_indexes:
                    logger.info(f"⚠️ No specific index for {query.specialty}, using june25_full index")
                    index_key = "june25_full"
                    chunks_key = "june25_full"
                elif f"band{query.band[-1]}" in self.faiss_indexes:
                    band_key = f"band{query.band[-1]}"
                    logger.info(f"⚠️ No specific index for {query.specialty}, using {band_key} index")
                    index_key = band_key
                    chunks_key = band_key
                else:
                    logger.warning(f"⚠️ No FAISS index found for specialty: {query.specialty}")
                    return []
            
            # Generează embedding pentru query
            query_embedding = await self._get_embedding(query.query_text)
            if query_embedding is None:
                return []
            
            # Caută în indexul FAISS
            faiss_index = self.faiss_indexes[index_key]
            chunks_data = self.chunks_data.get(chunks_key, [])
            
            if not chunks_data:
                logger.warning(f"⚠️ No chunks data found for specialty: {query.specialty}")
                return []
            
            # Caută cele mai similare chunks
            scores, indices = faiss_index.search(
                query_embedding.reshape(1, -1), 
                min(query.max_results, len(chunks_data))
            )
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= len(chunks_data) or score < query.min_score:
                    continue
                
                chunk = chunks_data[idx]
                
                # Creează rezultatul
                result = SearchResult(
                    content=chunk.get('content', ''),
                    source=chunk.get('source', 'Unknown'),
                    score=float(score),
                    metadata=chunk.get('metadata', {}),
                    chunk_id=idx
                )
                
                results.append(result)
            
            logger.info(f"🔍 Found {len(results)} results for query: {query.query_text[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in RAG search: {str(e)}")
            return []
    
    async def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generează embedding pentru text"""
        try:
            # Verifică cache-ul
            if text in self.embedding_cache:
                return self.embedding_cache[text]
            
            # Generează embedding
            embedding = self.embedder.encode([text])
            
            # Salvează în cache
            self.embedding_cache[text] = embedding[0]
            
            return embedding[0]
            
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {str(e)}")
            return None
    
    async def get_context_for_question(self, question: str, specialty: str, band: str) -> str:
        """Obține context relevant pentru o întrebare"""
        try:
            query = RAGQuery(
                query_text=question,
                specialty=specialty,
                band=band,
                max_results=3,
                min_score=0.6
            )
            
            results = await self.search(query)
            
            if not results:
                return "No relevant context found."
            
            # Construiește contextul
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"Context {i} (Score: {result.score:.2f}):\n{result.content}")
                if result.metadata:
                    context_parts.append(f"Source: {result.source}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error getting context: {str(e)}")
            return "Error retrieving context."
    
    async def get_recommendations(self, question: str, specialty: str, band: str) -> List[Dict[str, str]]:
        """Obține recomandări de studiu bazate pe întrebare"""
        try:
            query = RAGQuery(
                query_text=f"study recommendations for {question}",
                specialty=specialty,
                band=band,
                max_results=5,
                min_score=0.5
            )
            
            results = await self.search(query)
            
            recommendations = []
            for result in results:
                if result.metadata:
                    rec = {
                        "title": result.metadata.get("title", "Study Recommendation"),
                        "summary": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                        "source": result.source,
                        "relevance_score": result.score
                    }
                    recommendations.append(rec)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {str(e)}")
            return []
    
    async def get_topics(self) -> List[str]:
        """Return a list of all available topics from the loaded chunks."""
        topics = set()
        for specialty, chunks in self.chunks_data.items():
            for chunk in chunks:
                # Chunks from build_rag_index.py have 'topic' key
                if isinstance(chunk, dict) and 'topic' in chunk:
                    topics.add(chunk['topic'])
        
        # Add basic topics if none found (fallback)
        if not topics:
            topics = {"General", "Anatomy", "Pharmacology", "Patient Care"}
            
        return sorted(list(topics))

    async def get_knowledge_graph(self) -> Dict[str, Any]:
        """Generate a simple knowledge graph structure for visualization."""
        nodes = []
        edges = []
        
        topics = await self.get_topics()
        topic_id_map = {}
        
        # Add Topic Nodes
        for i, topic in enumerate(topics):
            node_id = f"topic_{i}"
            topic_id_map[topic] = node_id
            nodes.append({
                "id": node_id,
                "label": topic,
                "type": "topic",
                "color": "#4a90e2" # Blue for topics
            })
            
        # Add Document Nodes (deduplicated and linked to topics)
        doc_count = 0
        seen_docs = set()
        
        # Limit nodes to avoid frontend performance issues
        MAX_DOC_NODES = 50 
        
        for specialty, chunks in self.chunks_data.items():
            if doc_count >= MAX_DOC_NODES:
                break
                
            for chunk in chunks:
                if doc_count >= MAX_DOC_NODES:
                    break
                
                if not isinstance(chunk, dict):
                    continue
                    
                source = chunk.get('source', 'Unknown')
                topic = chunk.get('topic', 'General')
                
                if source not in seen_docs:
                    seen_docs.add(source)
                    doc_id = f"doc_{doc_count}"
                    
                    nodes.append({
                        "id": doc_id,
                        "label": source,
                        "type": "document",
                        "color": "#e24a4a" # Red for docs
                    })
                    
                    # Edge from Topic to Document
                    if topic in topic_id_map:
                        edges.append({
                            "id": f"e{len(edges)}",
                            "source": topic_id_map[topic],
                            "target": doc_id,
                            "animated": True
                        })
                    
                    doc_count += 1
                    
        return {"nodes": nodes, "edges": edges}

    async def generate_quiz(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate a quiz based on a specific topic using RAG content"""
        # Placeholder for quiz generation using LLM + RAG content
        # In a real implementation, this would query the LLM with context from the topic
        
        return {
            "topic": topic,
            "questions": [
                {
                    "id": 1,
                    "question": f"What is a key concept in {topic} regarding patient safety?",
                    "options": ["Hand Hygiene", "Speed", "Documentation", "None"],
                    "correctAnswer": "Hand Hygiene"
                },
                {
                    "id": 2,
                    "question": f"In {topic}, which of the following is crucial?",
                    "options": ["Ignoring symptoms", "Assessment", "Leaving early", "Paperwork"],
                    "correctAnswer": "Assessment"
                }
            ]
        }

    async def health_check(self) -> Dict[str, Any]:
        """Verifică starea serviciului RAG"""
        return {
            "initialized": self.is_initialized,
            "embedder_available": self.embedder is not None,
            "faiss_available": FAISS_AVAILABLE,
            "sentence_transformers_available": SENTENCE_TRANSFORMERS_AVAILABLE,
            "loaded_indexes": list(self.faiss_indexes.keys()),
            "loaded_chunks": {k: len(v) for k, v in self.chunks_data.items()},
            "cache_size": len(self.embedding_cache)
        }

# Instanță globală a serviciului
rag_service = RAGService()
