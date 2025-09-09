# VecindApp - Proyecto Título 2025

## Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- [Docker](https://www.docker.com/) y Docker Compose
- [Poetry](https://python-poetry.org/) (para el backend Python)
- [Node.js](https://nodejs.org/) y npm (para el frontend Angular)
- [ngrok](https://ngrok.com/) (opcional, para compartir la base de datos)

## Configuración Inicial

### 1. Base de Datos

**Crear y levantar la base de datos PostgreSQL:**

```bash
# Ejecutar desde la raíz del proyecto (proyecto-titulo-2025)
docker-compose up postgres --build
```

> **Nota:** Este comando crea una base de datos vacía. La opción `--build` reconstruye la imagen si es necesario.

### 2. Backend (FastAPI + Python)

**Instalar dependencias:**

```bash
cd apps/vecindApp/backend
poetry install
```

**Ejecutar migraciones de base de datos:**

```bash
# Crear una nueva migración (cuando cambies modelos)
poetry run alembic -n vecindApp_dev revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones pendientes
poetry run alembic -n vecindApp_dev upgrade head
```

**Levantar el servidor backend:**

```bash
# Desde apps/vecindApp/backend
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info
```

El backend estará disponible en: `http://localhost:8000`

### 3. Frontend (Angular)

**Instalar dependencias:**

```bash
# Desde la raíz del proyecto
npm install
```

**Levantar el servidor de desarrollo:**

```bash
# Desde la raíz del proyecto
npx nx serve
```

El frontend estará disponible en: `http://localhost:4200`

## Herramientas Adicionales

### Compartir Base de Datos (Desarrollo)

Para compartir tu base de datos local con otros desarrolladores:

```bash
# Exponer el puerto 5432 de PostgreSQL
ngrok tcp 5432
```

> **⚠️ Advertencia de Seguridad:** Solo usa esto en entornos de desarrollo. No expongas bases de datos de producción.

## Flujo de Trabajo Recomendado

1. **Primera vez:**
   ```bash
   # 1. Levantar BD
   docker-compose up postgres --build
   
   # 2. Configurar backend
   cd apps/vecindApp/backend
   poetry install
   poetry run alembic -n vecindApp_dev upgrade head
   
   # 3. Instalar frontend
   cd ../../..
   npm install
   ```

2. **Desarrollo diario:**
   ```bash
   # Terminal 1: BD (si no está corriendo)
   docker-compose up postgres
   
   # Terminal 2: Backend
   cd apps/vecindApp/backend
   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info
   
   # Terminal 3: Frontend
   npx nx serve
   ```

## Estructura del Proyecto

```
proyecto-titulo-2025/
├── apps/
│   └── vecindApp/
│       ├── backend/          # API FastAPI + Python
│       └── frontend/         # App Angular
├── docker-compose.yaml       # Configuración de PostgreSQL
└── README.md
```

## Solución de Problemas

### Base de Datos
- **Error de conexión**: Verifica que Docker esté corriendo y el puerto 5432 esté libre
- **Migraciones fallan**: Asegúrate de que la BD esté corriendo antes de ejecutar migraciones

### Backend
- **ModuleNotFoundError**: Ejecuta `poetry install` desde la carpeta backend
- **Puerto ocupado**: Cambia el puerto en el comando uvicorn (ej: `--port 8001`)

### Frontend
- **Command not found**: Instala dependencias con `npm install`
- **Puerto ocupado**: Angular usará automáticamente el siguiente puerto disponible

## Desarrollo Frontend (Angular + Nx)

### Generar Componentes y Servicios

**Componentes:**
```bash
# Componente básico
npx nx generate @nx/angular:component nombre-componente --project=vecindApp

# Componente con módulo propio
npx nx generate @nx/angular:component apps/vecindApp/frontend/src/app/components/nombre_componente/nombre_componente

# Componente standalone (Angular 14+)
npx nx generate @nx/angular:component nombre-componente --project=vecindApp --standalone
```

**Servicios:**
```bash
# Servicio básico
npx nx generate @nx/angular:service services/nombre-servicio --project=vecindApp

# Servicio con providedIn root
npx nx generate @nx/angular:service services/nombre-servicio --project=vecindApp
```

**Otros elementos:**
```bash
# Guard
npx nx generate @nx/angular:guard guards/nombre-guard --project=vecindApp

# Pipe
npx nx generate @nx/angular:pipe pipes/nombre-pipe --project=vecindApp

# Directiva
npx nx generate @nx/angular:directive directives/nombre-directiva --project=vecindApp

# Módulo
npx nx generate @nx/angular:module modules/nombre-modulo --project=vecindApp
```

> **Tip:** Usa `--dry-run` para ver qué archivos se crearán sin ejecutar el comando.

## Comandos Útiles

**Base de Datos:**
```bash
# Ver logs de la base de datos
docker-compose logs postgres

# Reiniciar la base de datos
docker-compose restart postgres

# Ver estado de migraciones
cd apps/vecindApp/backend
poetry run alembic -n vecindApp_dev current
```

**Backend:**
```bash
# Linter y formato del backend
cd apps/vecindApp/backend
poetry run black src/
poetry run flake8 src/
```

**Frontend:**
```bash
# Build del frontend
npx nx build vecindApp

# Linting del frontend
npx nx lint vecindApp

# Ejecutar tests (cuando estén configurados)
npx nx test vecindApp

# Ver información del proyecto
npx nx show project vecindApp
```

---

**Desarrollado por:** [Tu Nombre]  
**Proyecto:** Título 2025  
**Tecnologías:** FastAPI, PostgreSQL, Angular, Docker