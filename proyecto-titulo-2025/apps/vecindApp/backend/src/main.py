from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.auth_routes import router as auth_router
from src.api.routes.user_routes import router as user_router

# Crear una instancia de FastAPI con prefijo /api
app = FastAPI(
    title="VecindApp API",
    description="API para la aplicación VecindApp - Sistema de gestión de juntas de vecinos",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # URL del frontend Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear un router para las rutas de la API
api_router = APIRouter(prefix="/api")

# Endpoint de salud de la API
@api_router.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API
    """
    return {"estado": "OK", "mensaje": "API funcionando correctamente"}

# Endpoint básico que retorna información de la API
@api_router.get("/")
async def api_info():
    """
    Endpoint que retorna información básica de la API
    """
    return {
        "mensaje": "Bienvenido a VecindApp API",
        "version": "1.0.0",
        "descripcion": "Sistema de gestión de juntas de vecinos",
        "documentacion": "/api/docs"
    }

# Incluir las rutas de autenticación y usuarios
api_router.include_router(auth_router)
api_router.include_router(user_router)

# Incluir el router en la aplicación
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
