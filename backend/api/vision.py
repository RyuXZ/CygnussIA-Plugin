from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import ollama
import config

router = APIRouter(prefix="/api/vision", tags=["Vision"])

class VisionRequest(BaseModel):
    prompt: str
    image_b64: str
    model: str = config.DEFAULT_VISION_MODEL

@router.post("/")
async def analyze_image(request: VisionRequest):
    try:
        result = ollama.analyze_vision(request.prompt, request.image_b64, request.model)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))