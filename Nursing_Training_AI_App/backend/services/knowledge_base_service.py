"""
📚 Knowledge Base Service
Serviciu pentru managementul și integrarea Knowledge Base-ului medical
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import aiofiles
import sqlite3
from datetime import datetime

from core.config import settings
from core.mcp_rag_config import mcp_rag_config

logger = logging.getLogger(__name__)

@dataclass
class DocumentInfo:
    """Informații despre un document din Knowledge Base"""
    file_path: str
    specialty: str
    band: str
    title: str
    file_type: str
    size: int
    last_modified: datetime
    indexed: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class SearchResult:
    """Rezultatul unei căutări în Knowledge Base"""
    document: DocumentInfo
    relevance_score: float
    matched_content: str
    page_number: Optional[int] = None

class KnowledgeBaseService:
    """Serviciul principal pentru Knowledge Base"""
    
    def __init__(self):
        self.knowledge_base_path = Path(mcp_rag_config.knowledge_base_path)
        self.db_path = self.knowledge_base_path / "download_tracker.db"
        self.is_initialized = False
        self.documents = {}
        self.specialty_indexes = {}
        
    async def initialize(self):
        """Inițializează serviciul Knowledge Base"""
        try:
            logger.info("🚀 Initializing Knowledge Base Service...")
            
            # Verifică dacă Knowledge Base-ul există
            if not self.knowledge_base_path.exists():
                logger.error(f"❌ Knowledge Base path not found: {self.knowledge_base_path}")
                return False
            
            # Încarcă documentele existente
            await self._load_documents()
            
            # Creează indexurile pe specialități
            await self._create_specialty_indexes()
            
            self.is_initialized = True
            logger.info("✅ Knowledge Base Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing Knowledge Base Service: {str(e)}")
            return False
    
    async def _load_documents(self):
        """Încarcă toate documentele din Knowledge Base"""
        try:
            logger.info("📚 Loading documents from Knowledge Base...")
            
            # Parcurge structura Knowledge Base-ului
            for specialty_dir in self.knowledge_base_path.iterdir():
                if specialty_dir.is_dir() and specialty_dir.name != "FAISS_Indexes":
                    await self._load_specialty_documents(specialty_dir)
            
            logger.info(f"✅ Loaded {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"❌ Error loading documents: {str(e)}")
    
    async def _load_specialty_documents(self, specialty_dir: Path):
        """Încarcă documentele pentru o specialitate"""
        try:
            specialty_name = specialty_dir.name.lower()
            
            # Parcurge subdirectoarele (band-uri)
            for band_dir in specialty_dir.iterdir():
                if band_dir.is_dir():
                    band_name = band_dir.name.lower()
                    
                    # Parcurge subdirectoarele (tipuri de documente)
                    for doc_type_dir in band_dir.iterdir():
                        if doc_type_dir.is_dir():
                            doc_type = doc_type_dir.name.lower()
                            
                            # Încarcă fișierele PDF
                            for pdf_file in doc_type_dir.glob("*.pdf"):
                                doc_info = DocumentInfo(
                                    file_path=str(pdf_file),
                                    specialty=specialty_name,
                                    band=band_name,
                                    title=pdf_file.stem,
                                    file_type="pdf",
                                    size=pdf_file.stat().st_size,
                                    last_modified=datetime.fromtimestamp(pdf_file.stat().st_mtime),
                                    indexed=False,
                                    metadata={
                                        "specialty": specialty_name,
                                        "band": band_name,
                                        "doc_type": doc_type,
                                        "file_name": pdf_file.name
                                    }
                                )
                                
                                doc_id = f"{specialty_name}_{band_name}_{pdf_file.stem}"
                                self.documents[doc_id] = doc_info
                                
        except Exception as e:
            logger.error(f"❌ Error loading specialty documents: {str(e)}")
    
    async def _create_specialty_indexes(self):
        """Creează indexurile pe specialități"""
        try:
            for doc_id, doc_info in self.documents.items():
                specialty = doc_info.specialty
                
                if specialty not in self.specialty_indexes:
                    self.specialty_indexes[specialty] = []
                
                self.specialty_indexes[specialty].append(doc_id)
            
            logger.info(f"✅ Created indexes for {len(self.specialty_indexes)} specialties")
            
        except Exception as e:
            logger.error(f"❌ Error creating specialty indexes: {str(e)}")
    
    async def search_documents(self, query: str, specialty: str, band: Optional[str] = None) -> List[SearchResult]:
        """Caută documente în Knowledge Base"""
        try:
            if not self.is_initialized:
                logger.error("❌ Knowledge Base Service not initialized")
                return []
            
            results = []
            query_lower = query.lower()
            
            # Filtrează documentele pe specialitate
            if specialty not in self.specialty_indexes:
                logger.warning(f"⚠️ No documents found for specialty: {specialty}")
                return []
            
            doc_ids = self.specialty_indexes[specialty]
            
            # Filtrează pe band dacă este specificat
            if band:
                doc_ids = [doc_id for doc_id in doc_ids 
                          if self.documents[doc_id].band == band.lower()]
            
            # Caută în documente
            for doc_id in doc_ids:
                doc_info = self.documents[doc_id]
                
                # Caută în titlu
                title_score = self._calculate_relevance_score(query_lower, doc_info.title.lower())
                
                # Caută în metadata
                metadata_score = 0
                if doc_info.metadata:
                    for key, value in doc_info.metadata.items():
                        if isinstance(value, str):
                            metadata_score += self._calculate_relevance_score(query_lower, value.lower())
                
                # Calculează scorul total
                total_score = (title_score * 0.7) + (metadata_score * 0.3)
                
                if total_score > 0.1:  # Threshold minim
                    result = SearchResult(
                        document=doc_info,
                        relevance_score=total_score,
                        matched_content=doc_info.title,
                        page_number=None
                    )
                    results.append(result)
            
            # Sortează după relevanță
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            logger.info(f"🔍 Found {len(results)} documents for query: {query}")
            return results[:10]  # Limitează la 10 rezultate
            
        except Exception as e:
            logger.error(f"❌ Error searching documents: {str(e)}")
            return []
    
    def _calculate_relevance_score(self, query: str, text: str) -> float:
        """Calculează scorul de relevanță între query și text"""
        try:
            if not query or not text:
                return 0.0
            
            # Caută exact match
            if query in text:
                return 1.0
            
            # Caută cuvinte cheie
            query_words = query.split()
            text_words = text.split()
            
            matches = 0
            for word in query_words:
                if word in text_words:
                    matches += 1
            
            if matches == 0:
                return 0.0
            
            return matches / len(query_words)
            
        except Exception as e:
            logger.error(f"❌ Error calculating relevance score: {str(e)}")
            return 0.0
    
    async def get_document_info(self, doc_id: str) -> Optional[DocumentInfo]:
        """Obține informații despre un document"""
        return self.documents.get(doc_id)
    
    async def get_specialty_documents(self, specialty: str, band: Optional[str] = None) -> List[DocumentInfo]:
        """Obține toate documentele pentru o specialitate"""
        try:
            if specialty not in self.specialty_indexes:
                return []
            
            doc_ids = self.specialty_indexes[specialty]
            
            if band:
                doc_ids = [doc_id for doc_id in doc_ids 
                          if self.documents[doc_id].band == band.lower()]
            
            return [self.documents[doc_id] for doc_id in doc_ids]
            
        except Exception as e:
            logger.error(f"❌ Error getting specialty documents: {str(e)}")
            return []
    
    async def get_band_documents(self, band: str) -> List[DocumentInfo]:
        """Obține toate documentele pentru un band"""
        try:
            results = []
            for doc_info in self.documents.values():
                if doc_info.band == band.lower():
                    results.append(doc_info)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error getting band documents: {str(e)}")
            return []
    
    async def get_available_specialties(self) -> List[str]:
        """Obține lista specialităților disponibile"""
        return list(self.specialty_indexes.keys())
    
    async def get_available_bands(self) -> List[str]:
        """Obține lista band-urilor disponibile"""
        bands = set()
        for doc_info in self.documents.values():
            bands.add(doc_info.band)
        return sorted(list(bands))
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obține statistici despre Knowledge Base"""
        try:
            total_docs = len(self.documents)
            specialty_counts = {k: len(v) for k, v in self.specialty_indexes.items()}
            
            # Calculează dimensiunea totală
            total_size = sum(doc.size for doc in self.documents.values())
            
            # Calculează distribuția pe band-uri
            band_counts = {}
            for doc_info in self.documents.values():
                band = doc_info.band
                band_counts[band] = band_counts.get(band, 0) + 1
            
            return {
                "total_documents": total_docs,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "specialty_counts": specialty_counts,
                "band_counts": band_counts,
                "available_specialties": list(self.specialty_indexes.keys()),
                "available_bands": sorted(band_counts.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {str(e)}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifică starea serviciului Knowledge Base"""
        return {
            "initialized": self.is_initialized,
            "knowledge_base_path": str(self.knowledge_base_path),
            "knowledge_base_exists": self.knowledge_base_path.exists(),
            "total_documents": len(self.documents),
            "specialty_indexes": len(self.specialty_indexes),
            "db_exists": self.db_path.exists() if self.db_path else False
        }

# Instanță globală a serviciului
knowledge_base_service = KnowledgeBaseService()
