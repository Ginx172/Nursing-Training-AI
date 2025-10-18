"""
Text-to-Speech Service - Enterprise Grade
Ultra-realistic voices using ElevenLabs, Azure Neural TTS, and Google WaveNet
"""

from typing import Dict, Optional, List, BinaryIO
from datetime import datetime
import os
import hashlib
import httpx
from enum import Enum
import base64

class TTSProvider(str, Enum):
    ELEVENLABS = "elevenlabs"      # Best quality, most natural
    AZURE_NEURAL = "azure_neural"   # Excellent British voices
    GOOGLE_WAVENET = "google_wavenet" # Good alternative
    EXPO_SPEECH = "expo_speech"     # Fallback for mobile

class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class BritishAccent(str, Enum):
    RECEIVED_PRONUNCIATION = "rp"   # Standard British (BBC English)
    ESTUARY = "estuary"              # London/Southeast
    NORTHERN = "northern"            # Manchester, Yorkshire
    SCOTTISH = "scottish"
    WELSH = "welsh"

class TTSService:
    """Service for premium Text-to-Speech"""
    
    def __init__(self):
        # ElevenLabs configuration (BEST quality)
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.elevenlabs_url = "https://api.elevenlabs.io/v1"
        
        # Azure Neural TTS
        self.azure_speech_key = os.getenv("AZURE_SPEECH_KEY", "")
        self.azure_speech_region = os.getenv("AZURE_SPEECH_REGION", "uksouth")
        
        # Google Cloud TTS
        self.google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        
        # Audio cache directory
        self.cache_dir = "audio_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    # ========================================
    # ELEVENLABS (PREMIUM - Most Natural)
    # ========================================
    
    ELEVENLABS_VOICES = {
        # British Female Voices
        "british_female_young": "EXAVITQu4vr4xnSDxMaL",  # Sarah - Young professional
        "british_female_mature": "ThT5KcBeYPX3keUQqHPh",  # Dorothy - Mature, authoritative
        "british_female_warm": "MF3mGyEYCl7XYWbV9V6O",  # Elli - Warm, friendly
        
        # British Male Voices  
        "british_male_professional": "VR6AewLTigWG4xSOukaG",  # Arnold - Professional
        "british_male_authoritative": "pNInz6obpgDQGcFmaJgB",  # Adam - Deep, authoritative
        "british_male_young": "yoZ06aMxZJJ28mfd3POQ",  # Sam - Young, energetic
        
        # Scottish
        "scottish_female": "XB0fDUnXU5powFXDhCwa",  # Charlotte - Scottish
        "scottish_male": "cgSgspJ2msm6clMCkdW9",  # James - Scottish
    }
    
    async def generate_speech_elevenlabs(
        self,
        text: str,
        voice_id: str = "british_female_young",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> bytes:
        """
        Generate ultra-realistic speech using ElevenLabs
        
        Args:
            text: Text to convert to speech
            voice_id: Voice identifier (see ELEVENLABS_VOICES)
            stability: Voice stability (0-1, lower = more expressive)
            similarity_boost: Voice clarity (0-1, higher = clearer)
            style: Style exaggeration (0-1)
            use_speaker_boost: Enhance voice similarity
        
        Returns:
            Audio bytes (MP3)
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(text, voice_id, "elevenlabs")
            cached_audio = self._get_cached_audio(cache_key)
            if cached_audio:
                return cached_audio
            
            # Get actual voice ID
            actual_voice_id = self.ELEVENLABS_VOICES.get(voice_id, voice_id)
            
            url = f"{self.elevenlabs_url}/text-to-speech/{actual_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Best model
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "style": style,
                    "use_speaker_boost": use_speaker_boost
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                audio_bytes = response.content
                
                # Cache audio
                self._cache_audio(cache_key, audio_bytes)
                
                return audio_bytes
        
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            # Fallback to Azure
            return await self.generate_speech_azure(text)
    
    # ========================================
    # AZURE NEURAL TTS (Excellent British Voices)
    # ========================================
    
    AZURE_BRITISH_VOICES = {
        # Female voices
        "british_female_rp": "en-GB-SoniaNeural",           # RP, Professional
        "british_female_southern": "en-GB-LibbyNeural",     # Southern English
        "british_female_young": "en-GB-MiaNeural",          # Young, friendly
        
        # Male voices
        "british_male_rp": "en-GB-RyanNeural",              # RP, Authoritative
        "british_male_northern": "en-GB-ThomasNeural",      # Northern accent
        
        # Regional
        "scottish_female": "en-GB-AbbiNeural",              # Scottish
        "welsh_male": "en-GB-NiaNeural",                    # Welsh
    }
    
    async def generate_speech_azure(
        self,
        text: str,
        voice_name: str = "british_female_rp",
        speaking_rate: float = 1.0,  # 0.5 - 2.0
        pitch: str = "0%"  # -50% to +50%
    ) -> bytes:
        """
        Generate speech using Azure Neural TTS
        
        Args:
            text: Text to convert
            voice_name: Voice identifier
            speaking_rate: Speed (1.0 = normal)
            pitch: Pitch adjustment
        
        Returns:
            Audio bytes (MP3)
        """
        try:
            # Check cache
            cache_key = self._generate_cache_key(text, voice_name, "azure")
            cached_audio = self._get_cached_audio(cache_key)
            if cached_audio:
                return cached_audio
            
            # Get actual voice name
            actual_voice = self.AZURE_BRITISH_VOICES.get(voice_name, voice_name)
            
            # Build SSML (Speech Synthesis Markup Language)
            ssml = f"""
            <speak version='1.0' xml:lang='en-GB'>
                <voice name='{actual_voice}'>
                    <prosody rate='{speaking_rate}' pitch='{pitch}'>
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            url = f"https://{self.azure_speech_region}.tts.speech.microsoft.com/cognitiveservices/v1"
            
            headers = {
                "Ocp-Apim-Subscription-Key": self.azure_speech_key,
                "Content-Type": "application/ssml+xml",
                "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, content=ssml, headers=headers)
                response.raise_for_status()
                
                audio_bytes = response.content
                
                # Cache
                self._cache_audio(cache_key, audio_bytes)
                
                return audio_bytes
        
        except Exception as e:
            print(f"Azure TTS error: {e}")
            raise
    
    # ========================================
    # GOOGLE CLOUD TTS WAVENET
    # ========================================
    
    GOOGLE_BRITISH_VOICES = {
        "british_female_a": "en-GB-Wavenet-A",  # Female
        "british_female_c": "en-GB-Wavenet-C",  # Female
        "british_female_f": "en-GB-Wavenet-F",  # Female
        "british_male_b": "en-GB-Wavenet-B",    # Male
        "british_male_d": "en-GB-Wavenet-D",    # Male
    }
    
    async def generate_speech_google(
        self,
        text: str,
        voice_name: str = "british_female_a",
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> bytes:
        """Generate speech using Google Cloud TTS WaveNet"""
        try:
            # Check cache
            cache_key = self._generate_cache_key(text, voice_name, "google")
            cached_audio = self._get_cached_audio(cache_key)
            if cached_audio:
                return cached_audio
            
            from google.cloud import texttospeech
            
            client = texttospeech.TextToSpeechClient()
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            actual_voice = self.GOOGLE_BRITISH_VOICES.get(voice_name, voice_name)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-GB",
                name=actual_voice,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
                effects_profile_id=['headphone-class-device']
            )
            
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            audio_bytes = response.audio_content
            
            # Cache
            self._cache_audio(cache_key, audio_bytes)
            
            return audio_bytes
        
        except Exception as e:
            print(f"Google TTS error: {e}")
            raise
    
    # ========================================
    # SMART VOICE SELECTION
    # ========================================
    
    async def generate_speech_smart(
        self,
        text: str,
        preferences: Optional[Dict] = None
    ) -> bytes:
        """
        Smart voice generation with automatic provider selection
        
        preferences = {
            "provider": "elevenlabs",  # or "azure", "google", "auto"
            "gender": "female",
            "accent": "rp",
            "age": "young",  # young, mature
            "speaking_rate": 1.0
        }
        """
        try:
            prefs = preferences or {}
            provider = prefs.get("provider", "auto")
            
            # Auto-select best provider
            if provider == "auto":
                # Priority: ElevenLabs (if has API key) > Azure > Google
                if self.elevenlabs_api_key:
                    provider = "elevenlabs"
                elif self.azure_speech_key:
                    provider = "azure_neural"
                else:
                    provider = "google_wavenet"
            
            # Select appropriate voice
            voice_id = self._select_voice(
                provider=provider,
                gender=prefs.get("gender", "female"),
                accent=prefs.get("accent", "rp"),
                age=prefs.get("age", "young")
            )
            
            # Generate speech
            if provider == "elevenlabs":
                return await self.generate_speech_elevenlabs(
                    text=text,
                    voice_id=voice_id,
                    stability=0.4,  # More expressive for medical content
                    similarity_boost=0.85  # Very clear
                )
            
            elif provider == "azure_neural":
                return await self.generate_speech_azure(
                    text=text,
                    voice_name=voice_id,
                    speaking_rate=prefs.get("speaking_rate", 0.95)  # Slightly slower
                )
            
            elif provider == "google_wavenet":
                return await self.generate_speech_google(
                    text=text,
                    voice_name=voice_id
                )
        
        except Exception as e:
            print(f"Smart TTS error: {e}")
            raise
    
    def _select_voice(
        self,
        provider: str,
        gender: str,
        accent: str,
        age: str
    ) -> str:
        """Select appropriate voice based on preferences"""
        
        if provider == "elevenlabs":
            # Select ElevenLabs voice
            if gender == "female" and age == "young":
                return "british_female_young"
            elif gender == "female" and age == "mature":
                return "british_female_mature"
            elif gender == "male" and age == "young":
                return "british_male_young"
            elif gender == "male":
                return "british_male_professional"
            
            # Accent-specific
            if accent == "scottish":
                return "scottish_female" if gender == "female" else "scottish_male"
            
            return "british_female_young"  # Default
        
        elif provider == "azure_neural":
            # Select Azure voice
            if gender == "female":
                if accent == "rp":
                    return "british_female_rp"
                elif accent == "scottish":
                    return "scottish_female"
                return "british_female_southern"
            else:
                if accent == "rp":
                    return "british_male_rp"
                return "british_male_northern"
        
        elif provider == "google_wavenet":
            return "british_female_a" if gender == "female" else "british_male_b"
        
        return "british_female_young"
    
    # ========================================
    # AUDIO CACHING
    # ========================================
    
    def _generate_cache_key(self, text: str, voice: str, provider: str) -> str:
        """Generate cache key for audio"""
        data = f"{text}:{voice}:{provider}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """Get cached audio if exists"""
        try:
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    def _cache_audio(self, cache_key: str, audio_bytes: bytes):
        """Cache audio for future use"""
        try:
            cache_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            with open(cache_path, 'wb') as f:
                f.write(audio_bytes)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    # ========================================
    # BATCH PROCESSING
    # ========================================
    
    async def generate_batch_audio(
        self,
        texts: List[str],
        voice_preferences: Optional[Dict] = None
    ) -> List[bytes]:
        """Generate audio for multiple texts (batch processing)"""
        try:
            audio_results = []
            
            for text in texts:
                audio = await self.generate_speech_smart(text, voice_preferences)
                audio_results.append(audio)
            
            return audio_results
        except Exception as e:
            print(f"Batch audio generation error: {e}")
            raise
    
    async def pre_generate_question_audio(
        self,
        sector: str,
        specialty: str,
        band: str,
        bank_number: int
    ) -> Dict:
        """
        Pre-generate audio for entire question bank (background job)
        This improves mobile offline experience
        """
        try:
            # TODO: Load questions from database
            questions = []  # Placeholder
            
            results = {
                "bank_id": f"{sector}_{specialty}_{band}_{bank_number}",
                "total_questions": len(questions),
                "audio_generated": 0,
                "failed": 0,
                "cache_keys": []
            }
            
            for question in questions:
                try:
                    audio = await self.generate_speech_smart(
                        text=question["question_text"],
                        preferences={"provider": "elevenlabs"}
                    )
                    
                    cache_key = self._generate_cache_key(
                        question["question_text"],
                        "british_female_young",
                        "elevenlabs"
                    )
                    
                    results["audio_generated"] += 1
                    results["cache_keys"].append(cache_key)
                
                except Exception as e:
                    results["failed"] += 1
                    print(f"Failed to generate audio for question {question.get('id')}: {e}")
            
            return results
        except Exception as e:
            print(f"Pre-generation error: {e}")
            raise
    
    # ========================================
    # VOICE CUSTOMIZATION (ElevenLabs Professional)
    # ========================================
    
    async def clone_voice_elevenlabs(
        self,
        organization_id: str,
        voice_name: str,
        audio_samples: List[bytes]
    ) -> Dict:
        """
        Clone custom voice for organization (Enterprise feature)
        Requires ElevenLabs Professional plan
        
        Use case: Clone organization's training manager voice
        """
        try:
            url = f"{self.elevenlabs_url}/voices/add"
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key
            }
            
            # Prepare files
            files = []
            for i, audio_sample in enumerate(audio_samples):
                files.append(("files", (f"sample_{i}.mp3", audio_sample)))
            
            data = {
                "name": voice_name,
                "description": f"Custom voice for {organization_id}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    data=data,
                    files=files
                )
                response.raise_for_status()
                
                result = response.json()
                
                return {
                    "organization_id": organization_id,
                    "voice_id": result["voice_id"],
                    "voice_name": voice_name,
                    "status": "ready",
                    "created_at": datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"Voice cloning error: {e}")
            raise
    
    # ========================================
    # VOICE LIBRARY MANAGEMENT
    # ========================================
    
    async def list_available_voices(self) -> Dict:
        """List all available voices across providers"""
        voices = {
            "elevenlabs": {
                "provider": "ElevenLabs",
                "quality": "Ultra-realistic (Best)",
                "cost": "£0.30 per 1,000 characters",
                "voices": list(self.ELEVENLABS_VOICES.keys())
            },
            "azure_neural": {
                "provider": "Azure Neural TTS",
                "quality": "Excellent",
                "cost": "£4 per 1M characters",
                "voices": list(self.AZURE_BRITISH_VOICES.keys())
            },
            "google_wavenet": {
                "provider": "Google Cloud TTS WaveNet",
                "quality": "Very Good",
                "cost": "£12 per 1M characters",
                "voices": list(self.GOOGLE_BRITISH_VOICES.keys())
            }
        }
        
        return voices
    
    async def get_voice_sample(
        self,
        provider: str,
        voice_id: str
    ) -> bytes:
        """Generate sample audio for voice preview"""
        sample_text = """
        Welcome to Nursing Training AI. This is a sample of this voice reading 
        a typical clinical question. A patient presents with acute shortness of breath 
        and chest pain. What is your first priority?
        """
        
        if provider == "elevenlabs":
            return await self.generate_speech_elevenlabs(sample_text, voice_id)
        elif provider == "azure_neural":
            return await self.generate_speech_azure(sample_text, voice_id)
        elif provider == "google_wavenet":
            return await self.generate_speech_google(sample_text, voice_id)
    
    # ========================================
    # STREAMING AUDIO (For long text)
    # ========================================
    
    async def stream_speech_elevenlabs(
        self,
        text: str,
        voice_id: str = "british_female_young"
    ):
        """
        Stream audio for long text (reduces latency)
        Returns chunks of audio as they're generated
        """
        try:
            actual_voice_id = self.ELEVENLABS_VOICES.get(voice_id, voice_id)
            
            url = f"{self.elevenlabs_url}/text-to-speech/{actual_voice_id}/stream"
            
            headers = {
                "Accept": "audio/mpeg",
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
        
        except Exception as e:
            print(f"Streaming error: {e}")
            raise

# Singleton instance
tts_service = TTSService()

