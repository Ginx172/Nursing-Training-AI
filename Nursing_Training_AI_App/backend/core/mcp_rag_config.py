"""
Configurație pentru serviciile MCP și RAG
"""

import os
from typing import Dict, Any

class MCPRAGConfig:
    """Configurație pentru serviciile MCP și RAG"""
    
    def __init__(self):
        self.mcp_endpoint = os.getenv("MCP_ENDPOINT", "http://localhost:8001")
        self.rag_endpoint = os.getenv("RAG_ENDPOINT", "http://localhost:8002")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        _project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.knowledge_base_path = os.getenv("KNOWLEDGE_BASE_PATH", os.path.join(_project_root, "Healthcare_Knowledge_Base"))
        self.rag_engine_path = os.getenv("RAG_ENGINE_PATH", os.path.join(_project_root, "Nursing_Interviews_AI_model", "rag_engine"))
        
        # Configurații pentru diferite specialități
        self.specialty_configs = {
            "amu": {
                "faiss_index": "AMU_MAU",
                "priority_topics": ["ABCDE", "NEWS2", "Sepsis", "Fluids", "Oxygen therapy"],
                "clinical_guidelines": ["NICE", "RCUK", "NHS"]
            },
            "icu": {
                "faiss_index": "ICU_Critical_Care",
                "priority_topics": ["Ventilation", "Hemodynamics", "Sedation", "Infection control"],
                "clinical_guidelines": ["SCCM", "ESICM", "NICE"]
            },
            "emergency": {
                "faiss_index": "Emergency_AE",
                "priority_topics": ["Trauma", "Resuscitation", "Triage", "Emergency protocols"],
                "clinical_guidelines": ["ATLS", "ALS", "NICE"]
            },
            "maternity": {
                "faiss_index": "Maternity",
                "priority_topics": ["Antenatal care", "Labour", "Postnatal care", "Complications"],
                "clinical_guidelines": ["NICE", "RCOG", "WHO"]
            },
            "mental_health": {
                "faiss_index": "Mental_Health",
                "priority_topics": ["Risk assessment", "Crisis intervention", "Medication management"],
                "clinical_guidelines": ["NICE", "NMC", "RCN"]
            },
            "pediatrics": {
                "faiss_index": "Pediatrics",
                "priority_topics": ["Growth", "Development", "Vaccination", "Emergency care"],
                "clinical_guidelines": ["NICE", "RCPCH", "WHO"]
            }
        }
    
    def get_specialty_config(self, specialty: str) -> Dict[str, Any]:
        """Returnează configurația pentru o specialitate specifică"""
        return self.specialty_configs.get(specialty, {
            "faiss_index": "General",
            "priority_topics": ["General nursing", "Patient care", "Safety"],
            "clinical_guidelines": ["NICE", "NMC"]
        })
    
    def get_mcp_query_template(self, specialty: str) -> str:
        """Returnează template-ul pentru query-urile MCP"""
        config = self.get_specialty_config(specialty)
        return f"""
        Context: Healthcare training evaluation for {specialty}
        Guidelines: {', '.join(config['clinical_guidelines'])}
        Priority topics: {', '.join(config['priority_topics'])}
        
        Query: {{query}}
        """

# Instanță globală
mcp_rag_config = MCPRAGConfig()
