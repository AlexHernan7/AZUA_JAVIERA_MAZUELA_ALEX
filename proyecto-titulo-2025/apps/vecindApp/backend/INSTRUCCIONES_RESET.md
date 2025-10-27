# INSTRUCCIONES PARA INICIALIZAR/RESETEAR BASE DE DATOS

## Descripción
Scripts para inicializar o resetear completamente la base de datos del proyecto VecindApp.

## ADVERTENCIA
**EL RESET ELIMINARÁ TODOS LOS DATOS EXISTENTES**

## 🚀 Primera Instalación

Si es la primera vez que instalas el sistema:

```bash
cd apps/vecindApp/backend
poetry run python init_database.py
```

**¿Qué hace?**
- Crea el esquema `vecindapp`
- Crea todas las tablas del sistema
- Carga regiones y comunas desde JSON (todas las de Chile)
- Carga roles, estados, tipos de espacio y motivos de solicitud
- Crea usuario administrador
- **NO crea juntas de vecinos** (se crean desde el frontend)

## 🔄 Reset Completo (cuando necesites borrar todo)

```bash
cd apps/vecindApp/backend
poetry run python reset_database.py
```

**¿Qué hace?**
- Elimina el esquema `vecindapp` completo
- Ejecuta automáticamente `init_database.py`
- Recrea todo desde cero

## 📊 Datos Iniciales Creados

Después de ejecutar `init_database.py` tendrás:

- ✅ **16 Regiones** de Chile (todas)
- ✅ **346 Comunas** de Chile (todas)
- ✅ **3 Roles**: vecino, directiva, admin
- ✅ **3 Estados de Certificado**: pendiente_pago, generado, entregado
- ✅ **6 Estados de Reserva**: pendiente, pagada, aprobada, rechazada, cancelada, confirmada
- ✅ **4 Tipos de Espacio**: cancha, sala, plaza, otro
- ✅ **12 Motivos de Solicitud** agrupados por categorías
- ✅ **Usuario Admin**: admin@admin.cl (contraseña: admin)
- ❌ **0 Juntas de Vecinos** (se crean desde el frontend por el admin)

## 🔐 Credenciales de Acceso

Después de ejecutar `init_database.py`:

- **Email**: admin@admin.cl
- **Contraseña**: admin

## 💡 Próximos Pasos

1. **Crear Juntas de Vecinos**: Iniciar sesión como admin y crear juntas desde el frontend
2. **Registrar Vecinos**: Los vecinos se registran desde el formulario público
3. **Crear Espacios**: Las directivas crean espacios desde su panel

## ⚠️ Solución de Problemas

### Error: "Este script debe ejecutarse desde el directorio backend/"
```bash
cd apps/vecindApp/backend
pwd  # Debe mostrar: .../backend
```

### Error de conexión a base de datos
Verifica que:
1. PostgreSQL esté ejecutándose
2. La base de datos `vecindapp` exista
3. Las variables de entorno (.env) estén configuradas

### Error: "No se encontró el archivo JSON de regiones"
Verifica que exista el archivo:
```
frontend/public/data/regiones-comunas.json
```

### Las regiones/comunas no se muestran en el frontend
Ejecuta el script completo nuevamente:
```bash
poetry run python init_database.py
```

## 🆚 Diferencias con versiones anteriores

- ✅ Ahora hay **UN SOLO SCRIPT** (`init_database.py`)
- ✅ Carga **TODAS las regiones y comunas de Chile** desde JSON
- ✅ **NO crea juntas** de ejemplo (se crean desde el frontend)
- ✅ Más ordenado y con mejor output visual

---

**¡Listo! Tu base de datos estará lista para usar en minutos.**
