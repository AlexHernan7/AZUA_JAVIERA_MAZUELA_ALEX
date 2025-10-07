# INSTRUCCIONES PARA RESET DE BASE DE DATOS

## Descripción
Scripts para resetear completamente la base de datos del proyecto VecindApp.

## ADVERTENCIA
**ESTE PROCESO ELIMINARÁ TODOS LOS DATOS EXISTENTES**

## Archivos Disponibles

- `reset_database.py` - Script completo (recomendado)
- `reset_schema.py` - Solo borra esquema y recrea tablas
- `create_initial_data.py` - Solo carga datos iniciales

## Opción 1: Reset Completo (RECOMENDADO)

```bash
cd apps/vecindApp/backend
python reset_database.py
```

**¿Qué hace?**
- Elimina el esquema `vecindapp` completo
- Recrea el esquema y todas las tablas
- Carga datos iniciales (regiones, comunas, juntas, roles, etc.)
- Crea usuario administrador

## Opción 2: Solo Resetear Esquema

```bash
cd apps/vecindApp/backend
python reset_schema.py
python create_initial_data.py
```

**¿Qué hace?**
- Solo elimina y recrea el esquema
- Luego carga datos iniciales por separado

## Datos Iniciales Creados

Después del reset tendrás:

- 1 Región: Región Metropolitana de Santiago
- 1 Comuna: Maipú
- 3 Juntas de Vecinos de ejemplo
- 3 Roles: vecino, directiva, admin
- Estados de Certificado: pendiente_pago, generado, entregado
- Estados de Reserva: pendiente, pagada, aprobada, rechazada, cancelada, confirmada
- Tipos de Espacio: cancha, sala, plaza, otro
- 12 Motivos de Solicitud agrupados por categorías
- Usuario Admin: admin@admin.cl (contraseña: admin)

## Credenciales de Acceso

- Email: admin@admin.cl
- Contraseña: admin

## Solución de Problemas

### Error: "Este script debe ejecutarse desde el directorio backend/"
```bash
cd apps/vecindApp/backend
pwd  # Debe mostrar: .../backend
```

### Error de conexión a base de datos
Verifica que:
1. PostgreSQL esté ejecutándose
2. La base de datos `vecindapp` exista
3. Las variables de entorno estén configuradas

---

**¡Listo! Con estos scripts puedes resetear la base de datos fácilmente.**
