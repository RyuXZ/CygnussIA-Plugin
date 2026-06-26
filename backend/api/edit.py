from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import image_processing

router = APIRouter(prefix="/api/edit", tags=["Edit"])

class EditRequest(BaseModel):
    image_b64: str
    action: str
    algorithm: str = "default" # Nuevo parámetro para definir el modelo/algoritmo a usar
    parameters: Optional[Dict] = None

@router.post("/")
async def edit_image(request: EditRequest):
    try:
        img = image_processing.decode_b64(request.image_b64)
        
        # Enrutamos la imagen al algoritmo correspondiente
        if request.action == "optimize_texture":
            img = image_processing.optimize_textures(img, method=request.algorithm)
            
        elif request.action == "adjust_pose":
            img = image_processing.adjust_pose_structure(img, target_model=request.algorithm)
            
        else:
            raise ValueError(f"Acción de edición no válida: {request.action}")
            
        result_b64 = image_processing.encode_b64(img)
        return {"status": "success", "result_b64": result_b64}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))