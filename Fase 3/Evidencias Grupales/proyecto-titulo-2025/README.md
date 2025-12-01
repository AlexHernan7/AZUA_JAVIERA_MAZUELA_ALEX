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
npx nx generate @nx/angular:component src/app/components/nombre_componente/nombre_componente

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

## 📱 Aplicación Móvil (Android con Capacitor)

El proyecto está configurado para ejecutarse como aplicación móvil en Android usando Capacitor.

### **Inicio Rápido - Android**

```bash
# 1. Construir la aplicación Angular
npm run build:mobile

# 2. Abrir en Android Studio
npm run android:dev
```

### **Documentación Completa**

Para información detallada sobre cómo configurar y ejecutar en Android:

- 📖 **[Guía Completa de Android](CAPACITOR_ANDROID_GUIDE.md)** - Configuración, requisitos, troubleshooting
- 🚀 **[Próximos Pasos](PROXIMOS_PASOS_ANDROID.md)** - Checklist rápido para empezar

### **Requisitos para Android**

- ☕ Java Development Kit (JDK) 17+
- 🤖 Android Studio con Android SDK
- 📱 Emulador Android o dispositivo físico

### **Scripts para Desarrollo Móvil**

| Comando | Descripción |
|---------|-------------|
| `npm run build:mobile` | Construir app para móvil |
| `npm run cap:sync:android` | Sincronizar con Android |
| `npm run cap:open:android` | Abrir Android Studio |
| `npm run cap:run:android` | Ejecutar en dispositivo |
| `npm run android:dev` | Build + Sync + Open (recomendado) |

### **Plugins de Capacitor Instalados**

- 📱 App - Ciclo de vida de la aplicación
- 📸 Camera - Cámara y galería
- 💾 Filesystem - Sistema de archivos
- ⌨️ Keyboard - Control del teclado
- 🌐 Network - Estado de la red
- 🎨 Splash Screen - Pantalla de inicio
- 📊 Status Bar - Barra de estado

### **Servicio de Ejemplo**

Un servicio de ejemplo está disponible en:
`apps/vecindApp/frontend/src/app/services/capacitor-example.service.ts`

Este servicio muestra cómo usar los plugins de Capacitor en tu código Angular.

---

## 🚀 Deployment y Producción

### **Backend en Railway**

El backend está preparado para ser desplegado en Railway con soporte para PostgreSQL.

**Inicio Rápido**:
```bash
# 1. Crear cuenta en Railway (https://railway.app)
# 2. Conectar repositorio GitHub
# 3. Configurar Root Directory: apps/vecindApp/backend
# 4. Agregar PostgreSQL
# 5. Configurar variables de entorno
```

📖 **Guía Completa**: [DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md)

**Archivos de configuración incluidos**:
- ✅ `requirements.txt` - Dependencias
- ✅ `Procfile` - Comando de inicio
- ✅ `railway.json` - Config Railway
- ✅ `nixpacks.toml` - Builder
- ✅ `ENV_VARIABLES_RAILWAY.md` - Variables requeridas

### **Conectar Frontend al Backend en Railway**

Una vez desplegado el backend:

1. **Actualizar URL de producción**:
   - Edita `apps/vecindApp/frontend/src/environments/environment.prod.ts`
   - Agrega la URL de Railway: `https://tu-backend.up.railway.app/api`

2. **Reconstruir la app**:
   ```bash
   npm run build:mobile
   npm run cap:sync:android
   ```

📖 **Guía Completa**: [CONFIGURAR_API_URL.md](CONFIGURAR_API_URL.md)

### **Generar APK para Android**

Para distribuir tu app en dispositivos Android:

**APK Debug (Testing)**:
```bash
cd android
./gradlew assembleDebug
# APK en: android/app/build/outputs/apk/debug/
```

**APK Release (Producción)**:
```bash
# 1. Crear keystore (una sola vez)
keytool -genkey -v -keystore vecindapp-release-key.keystore -alias vecindapp -keyalg RSA -keysize 2048 -validity 10000

# 2. Configurar firma en android/app/build.gradle

# 3. Generar APK firmado
cd android
./gradlew assembleRelease
# APK en: android/app/build/outputs/apk/release/
```

📖 **Guía Completa**: [GENERAR_APK.md](GENERAR_APK.md)

### **Publicar en Google Play Store**

Para subir tu app a Play Store:

1. Crea cuenta de desarrollador ($25 USD)
2. Genera AAB en lugar de APK:
   ```bash
   cd android
   ./gradlew bundleRelease
   ```
3. Sigue los pasos en Play Console

📖 **Ver guía completa en**: [GENERAR_APK.md](GENERAR_APK.md) (sección "Subir a Google Play Store")

### **Documentación Completa de Deployment**

| Guía | Descripción |
|------|-------------|
| 📄 [RESUMEN_DEPLOYMENT.md](RESUMEN_DEPLOYMENT.md) | Resumen ejecutivo de todo el proceso |
| 🚀 [DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md) | Deployment del backend en Railway |
| 🔗 [CONFIGURAR_API_URL.md](CONFIGURAR_API_URL.md) | Configurar URLs de producción |
| 📦 [GENERAR_APK.md](GENERAR_APK.md) | Empaquetado y distribución Android |
| ⚙️ [ENV_VARIABLES_RAILWAY.md](apps/vecindApp/backend/ENV_VARIABLES_RAILWAY.md) | Variables de entorno necesarias |

---

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