from fastapi import APIRouter, HTTPException
import ollama

router = APIRouter(prefix="/api/models", tags=["Models"])

@router.get("/")
async def list_models():
    try:
        models = ollama.get_installed_models()
        return {"status": "success", "models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))