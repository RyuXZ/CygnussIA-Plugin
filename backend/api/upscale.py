from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import image_processing

router = APIRouter(prefix="/api/upscale", tags=["Upscale"])

class UpscaleRequest(BaseModel):
    image_b64: str
    target_resolution: str

@router.post("/")
async def upscale_image(request: UpscaleRequest):
    try:
        img = image_processing.decode_b64(request.image_b64)
        if request.target_resolution in ["4K", "8K"]:
            upscaled_img = image_processing.upscale_resolution(img, request.target_resolution)
        else:
            raise ValueError("Resolución no soportada.")
        result_b64 = image_processing.encode_b64(upscaled_img)
        return {"status": "success", "result_b64": result_b64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))