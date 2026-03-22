import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Any, Optional
import time
import argparse

class RAGSystem:
    """Sistem RAG performant care utilizează multiple indexuri FAISS"""
    
    def __init__(self, base_folder: str = ".", model_name: str = "all-MiniLM-L6-v2"):
        """
        Inițializează sistemul RAG cu multiple indexuri FAISS
        
        Args:
            base_folder: Directorul de bază care conține toate folderele cu indexuri
            model_name: Modelul sentence-transformer pentru embedding-uri
        """
        self.base_folder = base_folder
        self.domains = [
            "training_clinic_merged", 
            "pediatrics", 
            "obstetrics_gyn", 
            "mental_health", 
            "leadership_training", 
            "interview_nhs", 
            "emergency_care", 
            "elderly_care", 
            "communication_skills", 
            "clinical_governance"
        ]
        
        # Încarcă modelul de embedding
        print(f"Încărcare model de embedding {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"Model de embedding încărcat: {self.model.get_sentence_embedding_dimension()} dimensiuni")
        
        # Inițializare dicționare pentru indexuri și mapări
        self.indexes = {}
        self.mappings = {}
        self.doc_contents = {}
        
        # Încarcă toate indexurile
        self._load_all_indexes()
    
    def _load_all_indexes(self):
        """Încarcă toate indexurile FAISS și mapările corespunzătoare"""
        for domain in self.domains:
            faiss_path = os.path.join(self.base_folder, domain, "index.faiss")
            pkl_path = os.path.join(self.base_folder, domain, "index.pkl")
            
            if not os.path.exists(faiss_path) or not os.path.exists(pkl_path):
                print(f"⚠️ Domeniul {domain} nu are fișierele index necesare. Se ignoră.")
                continue
            
            try:
                # Încarcă indexul FAISS
                print(f"Încărcare index FAISS pentru {domain}...")
                index = faiss.read_index(faiss_path)
                self.indexes[domain] = index
                
                # Încarcă maparea din index.pkl
                with open(pkl_path, "rb") as f:
                    mapping_data = pickle.load(f)
                
                # Verifică formatul mapării
                if isinstance(mapping_data, dict):
                    if "index_to_docstore_id" in mapping_data and "documents" in mapping_data:
                        # Format complex
                        self.mappings[domain] = mapping_data["index_to_docstore_id"]
                        self.doc_contents[domain] = mapping_data["documents"]
                    else:
                        # Format simplu
                        self.mappings[domain] = mapping_data
                else:
                    print(f"⚠️ Structura index.pkl pentru {domain} nu este recunoscută.")
                    continue
                
                print(f"✅ Index {domain} încărcat: {index.ntotal} vectori")
            
            except Exception as e:
                print(f"❌ Eroare la încărcarea indexului pentru {domain}: {str(e)}")
                continue
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generează embedding pentru interogare
        
        Args:
            query: Interogarea text
        
        Returns:
            Embedding-ul normalizat ca np.ndarray
        """
        query_embedding = self.model.encode([query])[0]
        # Normalizare L2 pentru compatibilitate FAISS
        faiss.normalize_L2(np.array([query_embedding], dtype=np.float32))
        return query_embedding
    
    def search(self, query: str, k: int = 5, domains: Optional[List[str]] = None, 
               threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Caută în toate indexurile disponibile
        
        Args:
            query: Interogarea text
            k: Numărul de rezultate per domeniu
            domains: Lista domeniilor în care să se caute (default: toate)
            threshold: Pragul minim pentru scorul de similaritate (0-1)
            
        Returns:
            Lista de documente găsite, ordonate după relevanță
        """
        if domains is None:
            domains = list(self.indexes.keys())
        else:
            # Filtrează doar domeniile valide
            domains = [d for d in domains if d in self.indexes]
            if not domains:
                print("❌ Niciun domeniu valid specificat pentru căutare.")
                return []
        
        query_embedding = self.embed_query(query)
        all_results = []
        
        for domain in domains:
            # Convertește embedding-ul la formatul corect pentru FAISS
            xq = np.array([query_embedding], dtype=np.float32)
            
            # Caută în index
            distances, indices = self.indexes[domain].search(xq, k)
            
            # Procesează rezultatele
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                # Convertește distanța la scor de similaritate (0-1)
                # În FAISS, distanța mai mică = similaritate mai mare
                similarity = 1.0 - (dist / 2.0)  # Pentru distanțe L2 normalizate
                
                # Verifică pragul de similaritate
                if similarity < threshold or idx == -1:
                    continue
                
                # Obține ID-ul documentului din mapare
                doc_id = self.mappings[domain].get(int(idx))
                if doc_id is None:
                    continue
                
                # Obține conținutul documentului dacă este disponibil
                document_content = None
                if domain in self.doc_contents and doc_id in self.doc_contents[domain]:
                    document_content = self.doc_contents[domain][doc_id]
                
                # Adaugă rezultatul în lista completă
                result = {
                    "domain": domain,
                    "doc_id": doc_id,
                    "similarity": float(similarity),
                    "rank_in_domain": i + 1,
                    "content": document_content
                }
                all_results.append(result)
        
        # Sortează toate rezultatele după scorul de similaritate
        all_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return all_results
    
    def retrieve_context(self, query: str, k_per_domain: int = 3, 
                         max_results: int = 10, domains: Optional[List[str]] = None,
                         threshold: float = 0.65) -> str:
        """
        Recuperează contextul din documente relevante pentru interogare
        
        Args:
            query: Interogarea text
            k_per_domain: Numărul de rezultate per domeniu
            max_results: Numărul maxim de rezultate total
            domains: Lista domeniilor în care să se caute (default: toate)
            threshold: Pragul minim pentru scorul de similaritate (0-1)
            
        Returns:
            Contextul combinat ca text
        """
        results = self.search(query, k=k_per_domain, domains=domains, threshold=threshold)
        
        # Limitează numărul total de rezultate
        results = results[:max_results]
        
        if not results:
            return "Nu am găsit informații relevante pentru această interogare."
        
        # Construiește contextul din rezultate
        context_parts = []
        for i, result in enumerate(results):
            domain = result["domain"]
            doc_id = result["doc_id"]
            similarity = result["similarity"]
            
            context_part = f"[{i+1}] Domeniu: {domain}, Document: {doc_id}, Relevanță: {similarity:.2f}\n"
            
            # Adaugă conținut dacă este disponibil
            if result.get("content"):
                if isinstance(result["content"], dict) and "text" in result["content"]:
                    # Format complex cu text și metadata
                    context_part += result["content"]["text"]
                else:
                    # Altfel adaugă conținutul așa cum este
                    context_part += str(result["content"])
            else:
                context_part += f"(ID Document: {doc_id})"
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    def generate_answer(self, query: str, context: str, verbose: bool = False) -> str:
        """
        Generează un răspuns bazat pe context
        
        În implementarea reală, aici s-ar integra un LLM pentru a genera răspunsul.
        Pentru acest script, vom returna doar un placeholder.
        
        Args:
            query: Interogarea originală
            context: Contextul recuperat
            verbose: Dacă să se afișeze contextul complet
            
        Returns:
            Răspunsul generat
        """
        # În implementarea reală, aici ai integra un LLM
        # De exemplu, OpenAI, Claude Anthropic, LLama, etc.
        
        if verbose:
            print("\n--- CONTEXT RECUPERAT ---")
            print(context[:500] + "..." if len(context) > 500 else context)
            print("------------------------\n")
        
        # Placeholder pentru răspuns
        # Într-o implementare reală, acesta ar fi generat de un LLM
        response = (
            f"Aici ar fi răspunsul generat de un LLM bazat pe contextul recuperat. "
            f"Pentru o implementare completă, integrează API-ul preferat pentru un LLM, "
            f"cum ar fi OpenAI GPT-4, Claude Anthropic, sau un model open-source."
        )
        
        return response

def main():
    parser = argparse.ArgumentParser(description="Sistem RAG performant pentru multiple domenii medicale")
    parser.add_argument("--query", type=str, help="Interogarea pentru sistem")
    parser.add_argument("--base_folder", type=str, default="faiss_indexes", help="Directorul de bază pentru indexuri")
    parser.add_argument("--model", type=str, default="all-MiniLM-L6-v2", help="Modelul SentenceTransformer")
    parser.add_argument("--k", type=int, default=3, help="Număr de rezultate per domeniu")
    parser.add_argument("--max_results", type=int, default=10, help="Număr maxim de rezultate totale")
    parser.add_argument("--threshold", type=float, default=0.65, help="Prag minim de similaritate (0-1)")
    parser.add_argument("--domains", type=str, nargs="+", help="Domeniile specifice pentru căutare")
    parser.add_argument("--verbose", action="store_true", help="Afișează informații detaliate")
    
    args = parser.parse_args()
    
    # Inițializează sistemul RAG
    rag_system = RAGSystem(base_folder=args.base_folder, model_name=args.model)
    
    # Dacă nu este specificată o interogare, rulează în mod interactiv
    if not args.query:
        print("\n=== Sistem RAG Medical Interactiv ===")
        print("Introdu o întrebare sau 'exit' pentru a ieși.")
        
        while True:
            query = input("\nÎntrebare: ")
            if query.lower() in ["exit", "quit", "ieșire"]:
                break
            
            start_time = time.time()
            
            # Recuperează contextul
            context = rag_system.retrieve_context(
                query, 
                k_per_domain=args.k,
                max_results=args.max_results,
                domains=args.domains,
                threshold=args.threshold
            )
            
            # Generează răspunsul
            answer = rag_system.generate_answer(query, context, verbose=args.verbose)
            
            end_time = time.time()
            
            print(f"\nRăspuns:\n{answer}")
            print(f"\nTimp total: {end_time - start_time:.2f} secunde")
    else:
        # Execută o singură interogare
        start_time = time.time()
        
        context = rag_system.retrieve_context(
            args.query, 
            k_per_domain=args.k,
            max_results=args.max_results,
            domains=args.domains,
            threshold=args.threshold
        )
        
        answer = rag_system.generate_answer(args.query, context, verbose=args.verbose)
        
        end_time = time.time()
        
        print(f"\nRăspuns:\n{answer}")
        print(f"\nTimp total: {end_time - start_time:.2f} secunde")

if __name__ == "__main__":
    main()