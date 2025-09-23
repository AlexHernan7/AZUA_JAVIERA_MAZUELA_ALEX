# VecindApp Backend

Sistema de gestión de juntas de vecinos con integración de pagos Webpay Plus.

## 🏗️ Arquitectura

- **Framework**: FastAPI
- **Base de datos**: PostgreSQL con SQLAlchemy
- **Migraciones**: Alembic
- **Pagos**: Webpay Plus (Transbank)
- **Autenticación**: JWT
- **Documentos**: Generación de PDFs

## 🚀 Instalación

```bash
# Instalar dependencias
poetry install

# Configurar base de datos
poetry run alembic upgrade head

# Crear datos iniciales
poetry run python create_initial_data.py

# Iniciar servidor
poetry run uvicorn src.main:app --reload
```

## ⚙️ Configuración

Crear archivo `.env` con:

```env
# Base de datos
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=vecindapp
DATABASE_USER=tu_usuario
DATABASE_PASSWORD=tu_password

# API
SECRET_KEY=tu_secret_key_muy_segura
DEBUG=true
ENVIRONMENT=DEVELOPMENT

# Webpay Plus (Transbank)
WEBPAY_COMMERCE_CODE=597055555532
WEBPAY_API_KEY=579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C
WEBPAY_ENVIRONMENT=integration
WEBPAY_RETURN_URL=http://localhost:8000/api/payments/webpay/return
WEBPAY_FINAL_URL=http://localhost:4200/payment/success
```

## 🧪 Testing

```bash
# Test configuración Webpay
poetry run python test_webpay_config.py

# Test flujo completo de certificados con pago
poetry run python test_webpay_full_flow.py

# Listar usuarios del sistema
poetry run python test_list_users.py
```

## 📊 Funcionalidades

### ✅ Implementadas
- ✅ Sistema de autenticación JWT
- ✅ Gestión de usuarios y vecinos
- ✅ Creación de certificados de residencia
- ✅ Sistema de pagos con Webpay Plus
- ✅ Generación automática de PDFs
- ✅ Base de datos completa con migraciones
- ✅ API REST documentada

### 🔄 Flujo de Certificados con Pago

1. **Solicitud**: Usuario solicita certificado desde frontend
2. **Pago**: Redirección a Webpay Plus para pago seguro
3. **Confirmación**: Webpay confirma pago y retorna al sistema
4. **Generación**: Sistema genera PDF del certificado automáticamente
5. **Entrega**: Certificado disponible para descarga

## 🏦 Integración Webpay Plus

### Tarjetas de Prueba (Ambiente Integración)

**Para aprobar pagos:**
- Número: `4051 8856 0044 6623`
- CVV: `123`
- Fecha: `12/25`
- RUT: `11.111.111-1`
- Clave: `123`

## 📁 Estructura del Proyecto

```
src/
├── api/routes/          # Endpoints de la API
├── core/               # Configuración y seguridad
├── database/           # Modelos y sesión de BD
├── schemas/            # Esquemas Pydantic
├── services/           # Lógica de negocio
└── utils/              # Utilidades (PDF, imágenes)
```

## 🔧 Comandos Útiles

```bash
# Crear nueva migración
poetry run alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
poetry run alembic upgrade head

# Ver estado de migraciones
poetry run alembic current

# Iniciar con recarga automática
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📝 API Documentation

Cuando el servidor esté corriendo, visita:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🎯 Estado del Proyecto

✅ **Sistema completamente funcional** con:
- Arquitectura limpia y modular
- Integración de pagos estable
- Generación de certificados automática
- Base de datos bien estructurada
- Tests de integración funcionando

