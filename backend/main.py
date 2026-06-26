from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config

# Importar los routers de la carpeta api
from api import generate, upscale, edit, vision, models

app = FastAPI(title="Photoshop-Ollama Backend", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(models.router)
app.include_router(generate.router)
app.include_router(upscale.router)
app.include_router(edit.router)
app.include_router(vision.router)

@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "message": "Puente Photoshop <-> Ollama funcionando correctamente."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)