from fastapi import FastAPI, APIRouter

# Crear una instancia de FastAPI con prefijo /api
app = FastAPI(
    title="VecindApp API",
    description="API para la aplicación VecindApp",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Crear un router para las rutas de la API
api_router = APIRouter(prefix="/api")

# Endpoint básico que retorna "Hola mundo"
@api_router.get("/")
async def hola_mundo():
    """
    Endpoint que retorna un saludo básico
    """
    return {"mensaje": "Hola mundoo"}

# Endpoint adicional para probar la API
@api_router.get("/saludo/{nombre}")
async def saludo_personalizado(nombre: str):
    """
    Endpoint que retorna un saludo personalizado
    """
    return {"mensaje": f"Hola {nombre}, bienvenido a VecindApp"}

# Endpoint de salud de la API
@api_router.get("/health")
async def health_check():
    """
    Endpoint para verificar el estado de la API
    """
    return {"estado": "OK", "mensaje": "API funcionando correctamente"}

# Incluir el router en la aplicación
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
