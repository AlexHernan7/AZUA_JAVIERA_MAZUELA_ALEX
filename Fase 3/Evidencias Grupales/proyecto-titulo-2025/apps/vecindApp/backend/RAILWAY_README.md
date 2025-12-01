# 🚀 Backend - Railway Deployment

Este backend está listo para ser desplegado en Railway.

## ✅ Archivos de Configuración

- ✅ `requirements.txt` - Dependencias de Python
- ✅ `Procfile` - Comando de inicio para Railway
- ✅ `railway.json` - Configuración de Railway
- ✅ `nixpacks.toml` - Configuración del builder
- ✅ `runtime.txt` - Versión de Python (3.11.5)
- ✅ `ENV_VARIABLES_RAILWAY.md` - Variables de entorno necesarias

## 🎯 Deployment Rápido

### 1. **Conectar a Railway**

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link al proyecto (si ya existe)
railway link
```

### 2. **O desplegar desde GitHub**

1. Ve a https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Selecciona este repositorio
4. **IMPORTANTE**: Configura Root Directory: `apps/vecindApp/backend`

### 3. **Configurar Variables de Entorno**

Ver archivo completo: `ENV_VARIABLES_RAILWAY.md`

**Variables obligatorias**:
```bash
ENVIRONMENT=PRODUCTION
SECRET_KEY=tu_secret_key_segura
DB_USER_QP=${{Postgres.PGUSER}}
DB_PASSWORD_QP=${{Postgres.PGPASSWORD}}
DB_HOST_QP=${{Postgres.PGHOST}}
DB_PORT_QP=${{Postgres.PGPORT}}
DB_DATABASE_QP=${{Postgres.PGDATABASE}}
DB_SCHEMA=vecindapp
```

### 4. **Agregar PostgreSQL**

En Railway:
1. Click en "+ New"
2. Selecciona "Database" → "PostgreSQL"
3. Conecta al servicio del backend

### 5. **Ejecutar Migraciones**

```bash
# Con Railway CLI
railway run alembic -n vecindApp_dev upgrade head

# O desde Railway Terminal
# (Menu del servicio → Terminal)
cd /app
alembic -n vecindApp_dev upgrade head
```

## 🔍 Verificar Deployment

Una vez desplegado:

```bash
# Health check
curl https://tu-backend.up.railway.app/api/health

# Documentación
https://tu-backend.up.railway.app/api/docs
```

## 📚 Documentación Completa

- 📄 **Guía completa**: Ver `/DEPLOYMENT_RAILWAY.md` en la raíz del proyecto
- ⚙️ **Variables de entorno**: Ver `ENV_VARIABLES_RAILWAY.md` en esta carpeta
- 🔗 **Configurar frontend**: Ver `/CONFIGURAR_API_URL.md` en la raíz

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError"

Verifica que `requirements.txt` esté actualizado:
```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Error: "Database connection failed"

1. Verifica que PostgreSQL esté agregado al proyecto
2. Verifica las variables `DB_*` en Railway
3. Verifica que las migraciones se hayan ejecutado

### Ver Logs

En Railway:
1. Selecciona el servicio
2. Click en "Deployments"
3. Click en el deployment activo
4. Verás los logs en tiempo real

## 🔄 Updates Automáticos

Railway redespliega automáticamente cuando:
- Haces push a la rama principal (main/master)
- Cambias variables de entorno

No requiere configuración adicional. ✨

## 📞 Soporte

- Documentación Railway: https://docs.railway.app/
- Railway CLI: https://docs.railway.app/develop/cli
- Community: https://discord.gg/railway

