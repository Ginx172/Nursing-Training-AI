"""
🧠 MCP (Model Context Protocol) Service
Serviciu pentru managementul contextului și routing către modelele AI
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import httpx
from pathlib import Path

from core.config import settings
from core.mcp_rag_config import mcp_rag_config

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Tipurile de modele AI disponibile"""
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"
    CLAUDE = "claude-3"
    LOCAL = "local"

class ContextType(Enum):
    """Tipurile de context"""
    QUESTION_EVALUATION = "question_evaluation"
    FEEDBACK_GENERATION = "feedback_generation"
    RECOMMENDATION = "recommendation"
    CLINICAL_GUIDANCE = "clinical_guidance"

@dataclass
class MCPRequest:
    """Request pentru serviciul MCP"""
    query: str
    context_type: ContextType
    specialty: str
    band: str
    user_data: Optional[Dict[str, Any]] = None
    additional_context: Optional[str] = None

@dataclass
class MCPResponse:
    """Răspunsul de la serviciul MCP"""
    response: str
    model_used: str
    confidence: float
    context_used: Dict[str, Any]
    metadata: Dict[str, Any]

class ModelRouter:
    """Router pentru selectarea modelului potrivit"""
    
    def __init__(self):
        self.model_configs = {
            ModelType.GPT4: {
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_token": 0.03
            },
            ModelType.GPT35: {
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_token": 0.002
            },
            ModelType.CLAUDE: {
                "endpoint": "https://api.anthropic.com/v1/messages",
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_token": 0.015
            },
            ModelType.LOCAL: {
                "endpoint": "http://localhost:11434/api/generate",
                "max_tokens": 4000,
                "temperature": 0.3,
                "cost_per_token": 0.0
            }
        }
    
    def select_model(self, request: MCPRequest) -> ModelType:
        """Selectează modelul potrivit pentru request"""
        # Logică de selecție bazată pe context și band
        if request.context_type == ContextType.CLINICAL_GUIDANCE:
            return ModelType.GPT4  # Cel mai precis pentru ghiduri clinice
        
        if request.band in ["band_8a", "band_8b", "band_8c", "band_8d", "band_9"]:
            return ModelType.GPT4  # Modele superioare pentru banzile avansate
        
        if request.specialty in ["icu", "emergency"]:
            return ModelType.GPT4  # Critic pentru specialități critice
        
        return ModelType.GPT35  # Default pentru majoritatea cazurilor

class ContextManager:
    """Manager pentru contextul conversațiilor"""
    
    def __init__(self):
        self.context_storage = {}
        self.max_context_size = settings.MCP_CONTEXT_SIZE
    
    def get_context(self, request: MCPRequest) -> Dict[str, Any]:
        """Obține contextul pentru request"""
        context_key = f"{request.specialty}_{request.band}"
        
        # Context de bază
        base_context = {
            "specialty": request.specialty,
            "band": request.band,
            "context_type": request.context_type.value,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Adaugă context specific specialității
        specialty_config = mcp_rag_config.get_specialty_config(request.specialty)
        base_context.update({
            "priority_topics": specialty_config.get("priority_topics", []),
            "clinical_guidelines": specialty_config.get("clinical_guidelines", []),
            "faiss_index": specialty_config.get("faiss_index", "General")
        })
        
        # Adaugă context din conversația anterioară
        if context_key in self.context_storage:
            base_context["conversation_history"] = self.context_storage[context_key]
        
        # Adaugă context suplimentar
        if request.additional_context:
            base_context["additional_context"] = request.additional_context
        
        # Adaugă date utilizator
        if request.user_data:
            base_context["user_data"] = request.user_data
        
        return base_context
    
    def update_context(self, request: MCPRequest, response: MCPResponse):
        """Actualizează contextul cu răspunsul"""
        context_key = f"{request.specialty}_{request.band}"
        
        if context_key not in self.context_storage:
            self.context_storage[context_key] = []
        
        # Adaugă răspunsul la context
        self.context_storage[context_key].append({
            "query": request.query,
            "response": response.response,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Limitează dimensiunea contextului
        if len(self.context_storage[context_key]) > 10:
            self.context_storage[context_key] = self.context_storage[context_key][-10:]

class MCPService:
    """Serviciul principal MCP"""
    
    def __init__(self):
        self.model_router = ModelRouter()
        self.context_manager = ContextManager()
        self.openai_api_key = settings.OPENAI_API_KEY
        self.mcp_endpoint = settings.MCP_ENDPOINT
        self.is_initialized = False
    
    async def initialize(self):
        """Inițializează serviciul MCP"""
        try:
            logger.info("🚀 Initializing MCP Service...")
            
            # Verifică configurațiile
            if not self.openai_api_key:
                logger.warning("⚠️ OpenAI API key not configured")
            
            self.is_initialized = True
            logger.info("✅ MCP Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing MCP Service: {str(e)}")
            return False
    
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """Procesează un request MCP"""
        try:
            if not self.is_initialized:
                logger.error("❌ MCP Service not initialized")
                return self._create_error_response("Service not initialized")
            
            # Obține contextul
            context = self.context_manager.get_context(request)
            
            # Selectează modelul
            model_type = self.model_router.select_model(request)
            
            # Generează prompt-ul
            prompt = await self._generate_prompt(request, context, model_type)
            
            # Apelează modelul
            response = await self._call_model(prompt, model_type, context)
            
            # Actualizează contextul
            self.context_manager.update_context(request, response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing MCP request: {str(e)}")
            return self._create_error_response(f"Error processing request: {str(e)}")
    
    async def _generate_prompt(self, request: MCPRequest, context: Dict[str, Any], model_type: ModelType) -> str:
        """Generează prompt-ul pentru model"""
        try:
            # Template de bază
            base_template = mcp_rag_config.get_mcp_query_template(request.specialty)
            
            # Adaugă context specific
            context_info = f"""
Specialty: {request.specialty}
Band: {request.band}
Context Type: {request.context_type.value}
Priority Topics: {', '.join(context.get('priority_topics', []))}
Clinical Guidelines: {', '.join(context.get('clinical_guidelines', []))}
"""
            
            if request.additional_context:
                context_info += f"\nAdditional Context: {request.additional_context}"
            
            # Construiește prompt-ul final
            prompt = f"""
{base_template}

Context Information:
{context_info}

Query: {request.query}

Please provide a detailed, evidence-based response appropriate for a {request.band} nurse in {request.specialty} specialty.
"""
            
            return prompt
            
        except Exception as e:
            logger.error(f"❌ Error generating prompt: {str(e)}")
            return f"Error generating prompt: {str(e)}"
    
    async def _call_model(self, prompt: str, model_type: ModelType, context: Dict[str, Any]) -> MCPResponse:
        """Apelează modelul selectat"""
        try:
            model_config = self.model_router.model_configs[model_type]
            
            if model_type == ModelType.GPT4 or model_type == ModelType.GPT35:
                return await self._call_openai(prompt, model_type, model_config)
            elif model_type == ModelType.CLAUDE:
                return await self._call_claude(prompt, model_config)
            elif model_type == ModelType.LOCAL:
                return await self._call_local(prompt, model_config)
            else:
                return self._create_error_response(f"Unsupported model type: {model_type}")
                
        except Exception as e:
            logger.error(f"❌ Error calling model: {str(e)}")
            return self._create_error_response(f"Error calling model: {str(e)}")
    
    async def _call_openai(self, prompt: str, model_type: ModelType, config: Dict[str, Any]) -> MCPResponse:
        """Apelează OpenAI API"""
        try:
            if not self.openai_api_key:
                return self._create_error_response("OpenAI API key not configured")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["endpoint"],
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_type.value,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": config["max_tokens"],
                        "temperature": config["temperature"]
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return MCPResponse(
                        response=content,
                        model_used=model_type.value,
                        confidence=0.9,
                        context_used={"prompt_length": len(prompt)},
                        metadata={"tokens_used": data.get("usage", {}).get("total_tokens", 0)}
                    )
                else:
                    return self._create_error_response(f"OpenAI API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ Error calling OpenAI: {str(e)}")
            return self._create_error_response(f"OpenAI API error: {str(e)}")
    
    async def _call_claude(self, prompt: str, config: Dict[str, Any]) -> MCPResponse:
        """Apelează Claude API (placeholder)"""
        # Implementare pentru Claude API când va fi disponibil
        return self._create_error_response("Claude API not implemented yet")
    
    async def _call_local(self, prompt: str, config: Dict[str, Any]) -> MCPResponse:
        """Apelează modelul local"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["endpoint"],
                    json={
                        "model": "nursing-ai",
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("response", "")
                    
                    return MCPResponse(
                        response=content,
                        model_used="local",
                        confidence=0.8,
                        context_used={"prompt_length": len(prompt)},
                        metadata={"local_model": True}
                    )
                else:
                    return self._create_error_response(f"Local model error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ Error calling local model: {str(e)}")
            return self._create_error_response(f"Local model error: {str(e)}")
    
    def _create_error_response(self, error_message: str) -> MCPResponse:
        """Creează un răspuns de eroare"""
        return MCPResponse(
            response=f"Error: {error_message}",
            model_used="error",
            confidence=0.0,
            context_used={},
            metadata={"error": True, "error_message": error_message}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifică starea serviciului MCP"""
        return {
            "initialized": self.is_initialized,
            "openai_configured": bool(self.openai_api_key),
            "context_storage_size": len(self.context_manager.context_storage),
            "available_models": [model.value for model in ModelType],
            "mcp_endpoint": self.mcp_endpoint
        }

# Instanță globală a serviciului
mcp_service = MCPService()
