from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import os
import httpx

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"
    format: Optional[str] = "mp3"  # mp3|wav|ogg

@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    # Accept common audio types
    allowed = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/ogg", "audio/webm", "audio/m4a"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

    # If OPENAI_API_KEY present, use Whisper API; otherwise return stub
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty audio file")

    if not OPENAI_API_KEY:
        # Safe stub
        return {"text": "[transcription unavailable in demo without OPENAI_API_KEY]"}

    try:
        # OpenAI Whisper transcription via REST (v1/audio/transcriptions)
        # Using multipart form per OpenAI spec
        api_url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        files = {
            "file": (file.filename or "audio.mp3", data, file.content_type or "audio/mpeg"),
            "model": (None, "whisper-1"),
            "response_format": (None, "json")
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(api_url, headers=headers, files=files)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail=f"STT provider error: {resp.text}")
            payload = resp.json()
            return {"text": payload.get("text", "")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")

@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    # If OPENAI_API_KEY present, use TTS; otherwise return simple WAV tone stub
    if not OPENAI_API_KEY:
        # Generate a tiny WAV header + silence stub
        # 8000 Hz mono PCM, 0.25s silence
        sample_rate = 8000
        duration = 0.25
        num_samples = int(sample_rate * duration)
        data_bytes = b"\x00\x00" * num_samples
        # WAV header
        import struct
        byte_rate = sample_rate * 2
        block_align = 2
        header = b"RIFF" + struct.pack('<I', 36 + len(data_bytes)) + b"WAVEfmt " + struct.pack('<I', 16) + struct.pack('<H', 1) + struct.pack('<H', 1) + struct.pack('<I', sample_rate) + struct.pack('<I', byte_rate) + struct.pack('<H', block_align) + struct.pack('<H', 16) + b"data" + struct.pack('<I', len(data_bytes))
        wav = header + data_bytes
        return Response(content=wav, media_type="audio/wav")

    # OpenAI TTS via v1/audio/speech
    try:
        api_url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        model = "gpt-4o-mini-tts"
        voice = req.voice or "alloy"
        audio_format = req.format or "mp3"
        payload = {"model": model, "voice": voice, "input": text, "format": audio_format}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(api_url, headers=headers, json=payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail=f"TTS provider error: {resp.text}")
            media_type = f"audio/{audio_format}"
            return Response(content=resp.content, media_type=media_type)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
