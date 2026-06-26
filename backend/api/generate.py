from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama
import config

router = APIRouter(prefix="/api/generate", tags=["Generate"])

class TextRequest(BaseModel):
    prompt: str
    model: str = config.DEFAULT_TEXT_MODEL

@router.post("/")
async def generate_text(request: TextRequest):
    try:
        result = ollama.generate_text(request.prompt, request.model)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))