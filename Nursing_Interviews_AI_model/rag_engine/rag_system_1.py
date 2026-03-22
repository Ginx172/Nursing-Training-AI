import os
from typing import List, Dict, Any, Optional
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from langchain.embeddings.openai import OpenAIEmbeddings
import qdrant_client
import openai

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Sistem RAG (Retrieval-Augmented Generation) pentru interviuri medicale
    """
    def __init__(self, collection_name: str = "nursing_interviews"):
        """
        Inițializarea sistemului RAG
        
        Args:
            collection_name: Numele colecției în Qdrant
        """
        # Verificare chei API
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY nu este setată în fișierul .env")
            
        if not self.anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY nu este setată. Funcționalitățile Anthropic nu vor fi disponibile.")
        
        # Configurare OpenAI
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Definirea colecției
        self.collection_name = collection_name
        
        # Configurare Qdrant
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_client = qdrant_client.QdrantClient(url=self.qdrant_url)
        
        # Inițializare text_splitter pentru procesarea documentelor
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        
        # Configurare embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model="text-embedding-ada-002"
        )
        
        # Inițializare vectorstore
        try:
            self.vector_store = Qdrant(
                client=self.qdrant_client,
                collection_name=self.collection_name,
                embeddings=self.embeddings,
            )
            logger.info(f"Conectat la colecția Qdrant: {self.collection_name}")
        except Exception as e:
            logger.error(f"Eroare la conectarea la Qdrant: {e}")
            self.vector_store = None
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Caută documente relevante pentru query
        
        Args:
            query: Întrebarea sau query-ul
            top_k: Numărul de rezultate de returnat
            
        Returns:
            Lista de documente relevante cu scoruri
        """
        if not self.vector_store:
            logger.error("Vector store nu este inițializat")
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Eroare la căutare: {e}")
            return []
    
    def generate_with_rag(self, 
                          query: str, 
                          top_k: int = 5, 
                          model: str = "gpt-4",
                          temperature: float = 0.7,
                          system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generează răspuns folosind RAG
        
        Args:
            query: Întrebarea utilizatorului
            top_k: Numărul de rezultate de returnat
            model: Modelul LLM de folosit
            temperature: Temperatura pentru generare
            system_prompt: Prompt de sistem personalizat
            
        Returns:
            Răspunsul generat și contextul
        """
        # Căutare documente relevante
        search_results = self.search(query, top_k=top_k)
        
        if not search_results:
            logger.warning("Nu s-au găsit rezultate relevante pentru query")
        
        # Construire context din rezultatele căutării
        context = "\n\n".join([doc["content"] for doc in search_results])
        
        # Prompt de sistem implicit dacă nu este furnizat unul personalizat
        if not system_prompt:
            system_prompt = """
            Ești un asistent specializat în interviuri medicale pentru asistenți medicali.
            Folosește contextul furnizat pentru a răspunde întrebărilor despre practicile
            și procedurile din domeniul medical. Dacă nu știi răspunsul sau nu ai suficiente
            informații în context, spune acest lucru clar. Nu inventa informații!
            """
        
        # Construire prompt complet
        prompt = f"""
        Context:
        {context}
        
        Întrebare: {query}
        
        Răspunde la întrebare bazându-te doar pe informațiile din context.
        """
        
        try:
            # Generare răspuns cu OpenAI sau Anthropic (în funcție de modelul specificat)
            if model.startswith("claude"):
                # Implementare pentru Anthropic Claude
                if not self.anthropic_api_key:
                    return {
                        "answer": "Cheia API Anthropic nu este configurată.",
                        "context": search_results,
                        "model": model,
                        "error": "API key missing"
                    }
                
                # Cod pentru API Anthropic (exemplu)
                import anthropic
                client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                response = client.messages.create(
                    model=model,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1024,
                    temperature=temperature
                )
                answer = response.content[0].text
            else:
                # Generare răspuns cu OpenAI
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                )
                
                answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "context": search_results,
                "model": model,
                "usage": getattr(response, "usage", None)
            }
        except Exception as e:
            logger.error(f"Eroare la generarea răspunsului: {e}")
            return {
                "answer": f"Eroare la generarea răspunsului: {str(e)}",
                "context": search_results,
                "model": model,
                "error": str(e)
            }

    # Metodele pentru încărcare și indexare documente sunt definite în rag_with_llm.py pentru simplificare
