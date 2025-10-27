import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.core.logging import configure_logging
from src.api.routes.auth_routes import router as auth_router
from src.api.routes.user_routes import router as user_router
from src.api.routes.news_routes import router as news_router
from src.api.routes.certificado_routes import router as certificado_router
from src.api.routes.directiva_routes import router as directiva_router
from src.api.routes.webpay_routes import router as webpay_router
from src.api.routes.junta_routes import router as junta_router
from src.api.routes.espacio_routes import router as espacio_router
from src.api.routes.reserva_routes import router as reserva_router
from src.api.routes.master_routes import router as master_router
from src.api.routes.reporte_routes import router as reporte_router
from src.api.routes.admin_routes import router as admin_router

# Configurar logging
configure_logging()

# Crear una instancia de FastAPI con prefijo /api
app = FastAPI(
    title="VecindApp API",
    description="API para la aplicación VecindApp - Sistema de gestión de juntas de vecinos",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configurar CORS para permitir requests desde el frontend y app móvil
# Se obtienen los orígenes permitidos desde variables de entorno
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

# Agregar orígenes por defecto para desarrollo y Capacitor
default_origins = [
    "http://localhost:4200",
    "http://localhost:8100",  # Ionic/Capacitor dev
    "capacitor://localhost",  # Capacitor Android
    "ionic://localhost",      # Capacitor iOS
    "http://localhost",       # Web local
]

# Combinar todos los orígenes sin duplicados
all_origins = list(set(allowed_origins + default_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
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
        "documentacion": "/api/docs",
    }


# Incluir las rutas de autenticación, usuarios, noticias, certificados, directivos, juntas, espacios, reservas, pagos, administración y tablas maestras
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(news_router)
api_router.include_router(certificado_router)
api_router.include_router(directiva_router)
api_router.include_router(junta_router)
api_router.include_router(espacio_router)
api_router.include_router(reserva_router)
api_router.include_router(webpay_router)
api_router.include_router(admin_router)
api_router.include_router(master_router)
api_router.include_router(reporte_router)

# Incluir el router en la aplicación
app.include_router(api_router)

# Montar archivos estáticos para servir imágenes subidas
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
