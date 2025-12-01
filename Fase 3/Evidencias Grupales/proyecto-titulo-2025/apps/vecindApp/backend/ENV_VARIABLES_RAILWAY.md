# Variables de Entorno para Railway

Estas son las variables de entorno que debes configurar en Railway para tu backend.

## Variables Obligatorias

### Entorno
```
ENVIRONMENT=PRODUCTION
DEBUG=false
```

### Base de Datos
Railway creará automáticamente estas variables cuando conectes PostgreSQL:
```
DB_USER_QP=${{Postgres.PGUSER}}
DB_PASSWORD_QP=${{Postgres.PGPASSWORD}}
DB_HOST_QP=${{Postgres.PGHOST}}
DB_PORT_QP=${{Postgres.PGPORT}}
DB_DATABASE_QP=${{Postgres.PGDATABASE}}
DB_SCHEMA=vecindapp
```

### API Settings
```
SECRET_KEY=genera_una_clave_super_segura_aqui_usa_openssl_rand_base64_32
ALGORITHM=HS256
```

## Variables Opcionales

### Google OAuth
```
GOOGLE_OAUTH_CLIENT_ID=tu_client_id_de_google
GOOGLE_OAUTH_CLIENT_SECRET=tu_client_secret_de_google
GOOGLE_OAUTH_REDIRECT_URI=https://tu-backend.up.railway.app/api/auth/google/callback
```

### Webpay (Transbank)
Para producción, obtén estas credenciales de Transbank:
```
WEBPAY_COMMERCE_CODE=tu_codigo_comercio_produccion
WEBPAY_API_KEY=tu_api_key_produccion
WEBPAY_ENVIRONMENT=production
WEBPAY_RETURN_URL=https://tu-backend.up.railway.app/api/payments/webpay/return
WEBPAY_FINAL_URL=https://tu-frontend-url.com/payment/success
```

### Email - SendGrid API
Obtén tu API key en https://app.sendgrid.com/settings/api_keys
```
SENDGRID_API_KEY=SG.tu_api_key_de_sendgrid
SENDGRID_FROM_EMAIL=vecindapp66@gmail.com
EMAIL_FROM_NAME=VecindApp
```

**Cómo crear cuenta y API key (5 minutos):**
1. Crea cuenta gratis en https://signup.sendgrid.com
2. Ve a Settings → API Keys
3. Click "Create API Key"
4. Nombre: "VecindApp Railway"
5. Permisos: "Full Access" o "Mail Send"
6. Copia la API key (empieza con `SG.`)
7. Ve a Settings → Sender Authentication → Verify Single Sender
8. Verifica `vecindapp66@gmail.com` (recibirás email de confirmación)

**Por qué SendGrid:**
- ✅ Usa API HTTP (funciona en Railway)
- ✅ **100 emails gratis por día** (permanente)
- ✅ **Envía a cualquier email** sin restricciones
- ✅ Setup rápido con verificación de un solo email
- ✅ Muy confiable y usado por empresas grandes

### CORS - URLs Permitidas
Lista de URLs separadas por comas que pueden acceder a tu API:
```
ALLOWED_ORIGINS=https://tu-frontend.com,https://www.tu-frontend.com,capacitor://localhost
```

## Cómo Configurar en Railway

1. Ve a tu proyecto en Railway
2. Selecciona el servicio del backend
3. Ve a la pestaña "Variables"
4. Haz clic en "+ New Variable"
5. Agrega cada variable con su valor
6. O usa "Raw Editor" para pegar todas las variables a la vez

## Generador de SECRET_KEY

Puedes generar una SECRET_KEY segura con:

### En Linux/Mac:
```bash
openssl rand -base64 32
```

### En Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

### En PowerShell:
```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

## Variables que Railway crea automáticamente

Cuando conectas PostgreSQL a tu servicio, Railway crea estas variables:
- `PGUSER`
- `PGPASSWORD`
- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `DATABASE_URL`

Puedes referenciarlas en tus variables personalizadas usando: `${{Postgres.VARIABLE_NAME}}`

