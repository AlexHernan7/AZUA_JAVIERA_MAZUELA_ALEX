# 🚀 Deployment del Backend en Railway

Esta guía te ayudará a desplegar el backend de **vecindApp** en Railway para que pueda ser accedido desde la app móvil y el frontend web.

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Preparar el Repositorio](#preparar-el-repositorio)
3. [Crear Cuenta en Railway](#crear-cuenta-en-railway)
4. [Desplegar Backend](#desplegar-backend)
5. [Configurar Base de Datos](#configurar-base-de-datos)
6. [Configurar Variables de Entorno](#configurar-variables-de-entorno)
7. [Ejecutar Migraciones](#ejecutar-migraciones)
8. [Verificar Deployment](#verificar-deployment)
9. [Conectar Frontend y App Móvil](#conectar-frontend-y-app-móvil)
10. [Troubleshooting](#troubleshooting)

---

## ✅ Requisitos Previos

- ✅ Cuenta de GitHub (para conectar el repositorio)
- ✅ Código del backend en un repositorio Git
- ✅ Tarjeta de crédito (Railway ofrece $5 gratis mensuales)

---

## 📂 Preparar el Repositorio

### 1. **Verificar que los archivos estén listos**

Los siguientes archivos ya están creados en `apps/vecindApp/backend/`:

- ✅ `requirements.txt` - Dependencias de Python
- ✅ `Procfile` - Comando de inicio
- ✅ `railway.json` - Configuración de Railway
- ✅ `nixpacks.toml` - Configuración del builder
- ✅ `runtime.txt` - Versión de Python
- ✅ `ENV_VARIABLES_RAILWAY.md` - Variables de entorno

### 2. **Commit y Push al repositorio**

```bash
git add .
git commit -m "Preparar backend para Railway deployment"
git push origin main  # o tu rama principal
```

---

## 🎯 Crear Cuenta en Railway

### 1. **Ir a Railway**
- Visita: https://railway.app/
- Haz clic en "Start a New Project"

### 2. **Iniciar sesión con GitHub**
- Selecciona "Login with GitHub"
- Autoriza a Railway a acceder a tus repositorios

### 3. **Crear un nuevo proyecto**
- Haz clic en "New Project"
- Selecciona "Deploy from GitHub repo"

---

## 🚀 Desplegar Backend

### **Paso 1: Seleccionar Repositorio**

1. Selecciona el repositorio `Proyecto_titulo` (o como se llame tu repo)
2. Railway detectará automáticamente el monorepo

### **Paso 2: Configurar Root Directory**

⚠️ **IMPORTANTE**: Railway necesita saber dónde está el backend en tu monorepo.

1. En tu proyecto de Railway, ve a "Settings"
2. Busca "Root Directory"
3. Cambia de `/` a: `apps/vecindApp/backend`
4. Guarda los cambios

### **Paso 3: Configurar Build**

Railway debería detectar automáticamente que es un proyecto Python, pero verifica:

1. Ve a "Settings" > "Build"
2. Verifica que:
   - Builder: `NIXPACKS`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

---

## 🗄️ Configurar Base de Datos

### **Opción A: PostgreSQL de Railway (Recomendado)**

1. En tu proyecto de Railway, haz clic en "+ New"
2. Selecciona "Database"
3. Selecciona "PostgreSQL"
4. Railway creará automáticamente una base de datos

### **Conectar BD al Backend**

1. Haz clic en el servicio PostgreSQL
2. Ve a "Connect"
3. Copia las variables de conexión
4. Ve al servicio del backend
5. Ve a "Variables"
6. Agrega las variables de BD (ver sección siguiente)

### **Opción B: Base de Datos Externa**

Si prefieres usar una BD externa:
- Configura las variables `DB_HOST_QP`, `DB_USER_QP`, etc. manualmente

---

## ⚙️ Configurar Variables de Entorno

### **Variables Obligatorias**

En tu servicio del backend, ve a "Variables" y agrega:

```bash
# Entorno
ENVIRONMENT=PRODUCTION
DEBUG=false

# Base de Datos (si usas PostgreSQL de Railway)
DB_USER_QP=${{Postgres.PGUSER}}
DB_PASSWORD_QP=${{Postgres.PGPASSWORD}}
DB_HOST_QP=${{Postgres.PGHOST}}
DB_PORT_QP=${{Postgres.PGPORT}}
DB_DATABASE_QP=${{Postgres.PGDATABASE}}
DB_SCHEMA=vecindapp

# API Settings
SECRET_KEY=tu_clave_super_segura_generada
ALGORITHM=HS256
```

### **Generar SECRET_KEY**

En tu terminal local:

**Linux/Mac:**
```bash
openssl rand -base64 32
```

**Windows PowerShell:**
```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

**Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### **Variables Opcionales**

```bash
# CORS - URLs permitidas (separadas por comas)
ALLOWED_ORIGINS=https://tu-frontend.com,https://tu-dominio.com

# Google OAuth (opcional)
GOOGLE_OAUTH_CLIENT_ID=tu_client_id
GOOGLE_OAUTH_CLIENT_SECRET=tu_client_secret
GOOGLE_OAUTH_REDIRECT_URI=https://tu-backend.up.railway.app/api/auth/google/callback

# Webpay - Transbank (producción)
WEBPAY_COMMERCE_CODE=tu_codigo_comercio
WEBPAY_API_KEY=tu_api_key
WEBPAY_ENVIRONMENT=production
WEBPAY_RETURN_URL=https://tu-backend.up.railway.app/api/payments/webpay/return
WEBPAY_FINAL_URL=https://tu-frontend.com/payment/success

# Email - Resend
RESEND_API_KEY=re_tu_api_key
RESEND_FROM_EMAIL=VecindApp <noreply@tudominio.com>
```

📄 **Ver detalle completo**: `apps/vecindApp/backend/ENV_VARIABLES_RAILWAY.md`

---

## 🔄 Ejecutar Migraciones

Una vez desplegado el backend y configurada la BD, necesitas ejecutar las migraciones.

### **Método 1: Desde Railway CLI (Recomendado)**

1. **Instalar Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Conectar al proyecto**:
   ```bash
   cd apps/vecindApp/backend
   railway link
   ```

4. **Ejecutar migraciones**:
   ```bash
   railway run alembic -n vecindApp_dev upgrade head
   ```

### **Método 2: Desde Terminal Railway**

1. En Railway, ve a tu servicio del backend
2. Haz clic en el menú (⋮) > "Terminal"
3. Ejecuta:
   ```bash
   cd /app
   alembic -n vecindApp_dev upgrade head
   ```

### **Método 3: Script de Inicialización**

Si prefieres ejecutar las migraciones automáticamente al desplegar:

1. Crea un script `start.sh` en `apps/vecindApp/backend/`:
   ```bash
   #!/bin/bash
   cd /app
   alembic -n vecindApp_dev upgrade head
   uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

2. Actualiza `railway.json`:
   ```json
   {
     "deploy": {
       "startCommand": "bash start.sh"
     }
   }
   ```

---

## ✅ Verificar Deployment

### **1. Obtener la URL**

1. En Railway, ve a tu servicio del backend
2. Ve a "Settings" > "Networking"
3. Haz clic en "Generate Domain"
4. Copia la URL generada (ej: `https://vecindapp-backend.up.railway.app`)

### **2. Probar la API**

Abre en tu navegador:

```
https://tu-backend.up.railway.app/api/health
```

Deberías ver:
```json
{
  "estado": "OK",
  "mensaje": "API funcionando correctamente"
}
```

### **3. Ver la Documentación**

```
https://tu-backend.up.railway.app/api/docs
```

Verás la documentación interactiva de Swagger.

### **4. Ver Logs**

En Railway:
1. Ve a tu servicio del backend
2. Haz clic en "Deployments"
3. Haz clic en el deployment activo
4. Verás los logs en tiempo real

---

## 🔗 Conectar Frontend y App Móvil

### **1. Actualizar Frontend (Angular)**

Crea o actualiza el archivo de entorno de producción:

**`apps/vecindApp/frontend/src/environments/environment.prod.ts`**:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://tu-backend.up.railway.app/api'
};
```

### **2. Actualizar Configuración de Capacitor**

**`capacitor.config.ts`**:
```typescript
const config: CapacitorConfig = {
  appId: 'com.vecindapp',
  appName: 'vecindApp',
  webDir: 'dist/apps/vecindApp/frontend',
  server: {
    androidScheme: 'https',
    cleartext: false,  // Cambiar a false en producción
    // Para desarrollo con live reload:
    // url: 'https://tu-backend.up.railway.app',
  },
  // ... resto de la configuración
};
```

### **3. Actualizar Variables de Entorno en Railway**

Agrega la URL de tu frontend a `ALLOWED_ORIGINS`:

```bash
ALLOWED_ORIGINS=https://tu-frontend.com,capacitor://localhost,ionic://localhost
```

### **4. Rebuild Frontend**

```bash
# Construir para producción
npm run build:mobile

# Sincronizar con Capacitor
npm run cap:sync:android
```

---

## 🛠️ Troubleshooting

### **Error: "ModuleNotFoundError"**

**Causa**: Falta una dependencia en `requirements.txt`

**Solución**:
1. Agrega la dependencia faltante a `requirements.txt`
2. Push al repositorio
3. Railway redesplegará automáticamente

### **Error: "Database connection failed"**

**Causa**: Variables de BD incorrectas

**Solución**:
1. Verifica las variables en Railway > Variables
2. Asegúrate de que la BD esté conectada al servicio
3. Verifica que el esquema `vecindapp` exista

### **Error: "Port already in use"**

**Causa**: No estás usando la variable `$PORT` de Railway

**Solución**:
Asegúrate de que el comando de inicio use `--port $PORT`:
```bash
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### **Error: CORS**

**Causa**: La URL de tu frontend no está en `ALLOWED_ORIGINS`

**Solución**:
1. Ve a Variables en Railway
2. Actualiza `ALLOWED_ORIGINS` con todas las URLs necesarias:
   ```bash
   ALLOWED_ORIGINS=https://tu-frontend.com,capacitor://localhost,ionic://localhost
   ```
3. Reinicia el servicio

### **Error: "No migrations to run"**

**Causa**: Las migraciones ya están aplicadas

**Solución**: Esto es normal, no es un error.

### **Logs muestran errores**

**Solución**:
1. Ve a Deployments en Railway
2. Revisa los logs completos
3. Busca el error específico
4. Ajusta las variables o código según el error

---

## 📊 Monitoreo

### **Ver Métricas**

En Railway puedes ver:
- CPU Usage
- Memory Usage
- Network Traffic
- Request Count

### **Configurar Alertas**

1. Ve a Settings > Notifications
2. Configura notificaciones por email o Discord
3. Recibirás alertas si el servicio falla

---

## 💰 Costos

Railway ofrece:
- **$5 USD gratis** mensuales
- Después: **$0.000231 USD** por GB-hora

**Ejemplo de costos típicos**:
- Backend pequeño: ~$5-10 USD/mes
- PostgreSQL: ~$5 USD/mes
- Total: ~$10-15 USD/mes

---

## 🔒 Seguridad

### **Recomendaciones**:

1. ✅ **SECRET_KEY única**: Nunca uses la del desarrollo
2. ✅ **DEBUG=false** en producción
3. ✅ **HTTPS**: Railway lo proporciona automáticamente
4. ✅ **Variables sensibles**: Usa variables de entorno, nunca en código
5. ✅ **CORS restrictivo**: Solo URLs necesarias en `ALLOWED_ORIGINS`
6. ✅ **Actualiza dependencias**: Mantén `requirements.txt` actualizado

---

## 🔄 CI/CD Automático

Railway hace deployment automático cuando:
1. Haces push a tu rama principal (main/master)
2. Railway detecta los cambios
3. Ejecuta el build
4. Despliega la nueva versión

**No requiere configuración adicional** ✨

---

## 📚 Recursos Adicionales

- **Documentación Railway**: https://docs.railway.app/
- **Railway CLI**: https://docs.railway.app/develop/cli
- **Variables de entorno**: `apps/vecindApp/backend/ENV_VARIABLES_RAILWAY.md`
- **Soporte Railway**: https://help.railway.app/

---

## ✅ Checklist Final

- [ ] Repositorio pusheado a GitHub
- [ ] Proyecto creado en Railway
- [ ] Root directory configurado: `apps/vecindApp/backend`
- [ ] PostgreSQL agregado y conectado
- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY generada y agregada
- [ ] Migraciones ejecutadas
- [ ] API respondiendo en `/api/health`
- [ ] CORS configurado con `ALLOWED_ORIGINS`
- [ ] Frontend actualizado con URL del backend
- [ ] Capacitor actualizado con URL del backend
- [ ] App móvil probada con backend en Railway

---

¡Listo! Tu backend ahora está desplegado en Railway y accesible desde cualquier lugar. 🎉

