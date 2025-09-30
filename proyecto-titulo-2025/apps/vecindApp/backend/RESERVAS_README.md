# Sistema de Reservas - VecindApp

## Descripción

Sistema completo de reservas para espacios comunitarios (canchas, salas multiuso, plazas, etc.) con control de concurrencia robusto y validaciones inteligentes.

## Características Principales

### ✅ Control de Concurrencia
- **Garantía de integridad**: NUNCA habrá doble reserva del mismo horario
- **Algoritmo de solapamiento**: Detecta cualquier tipo de conflicto temporal
- **Transacciones atómicas**: El primero en llegar obtiene la reserva
- **Manejo de múltiples usuarios**: Soporta cientos de usuarios simultáneos

### ✅ Validaciones Inteligentes
- **Horarios permitidos**: 12:00 PM - 22:00 PM (10:00 PM)
- **Fechas futuras**: Solo se pueden reservar fechas futuras
- **Duración por tipo de espacio**:
  - Canchas: 1-3 horas
  - Salas: 1-6 horas
  - Plazas: 1-4 horas
  - Otros: 1-2 horas
- **Cancelación**: Mínimo 2 horas de anticipación

### ✅ Estados de Reserva
- `PENDIENTE` - Recién creada
- `APROBADA` - Aprobada por administrador
- `CONFIRMADA` - Confirmada por el usuario
- `PAGADA` - Pagada (si aplica)
- `CANCELADA` - Cancelada por el usuario
- `RECHAZADA` - Rechazada por administrador

## API Endpoints

### Reservas
```http
POST   /api/reservas/                    # Crear reserva
GET    /api/reservas/mis-reservas        # Listar mis reservas (con filtros)
GET    /api/reservas/{id}                # Obtener reserva específica
PUT    /api/reservas/{id}                # Actualizar reserva
DELETE /api/reservas/{id}                # Cancelar reserva
```

### Consultas
```http
POST   /api/reservas/disponibilidad      # Consultar disponibilidad por fecha
GET    /api/reservas/espacios/disponibles # Listar espacios de mi junta
```

## Ejemplos de Uso

### Crear Reserva
```json
POST /api/reservas/
{
  "id_espacio": 1,
  "inicio": "2025-10-01T14:00:00",
  "fin": "2025-10-01T15:00:00",
  "observaciones": "Partido de fútbol"
}
```

### Consultar Disponibilidad
```json
POST /api/reservas/disponibilidad
{
  "id_espacio": 1,
  "fecha": "2025-10-01T00:00:00"
}
```

**Respuesta:**
```json
{
  "id_espacio": 1,
  "fecha": "2025-10-01T00:00:00",
  "horarios_disponibles": [
    {"inicio": "12:00", "fin": "13:00"},
    {"inicio": "13:00", "fin": "14:00"},
    {"inicio": "15:00", "fin": "16:00"}
  ],
  "horarios_ocupados": [
    {
      "inicio": "14:00",
      "fin": "15:00",
      "id_reserva": 123,
      "estado": "confirmada"
    }
  ]
}
```

## Pruebas de Concurrencia

### Script de Pruebas Completas
```bash
# Ejecutar pruebas de concurrencia con base de datos
poetry run python test_concurrencia_reservas.py
```

**Pruebas incluidas:**
1. **Concurrencia mismo horario**: 5 usuarios intentan reservar simultáneamente
2. **Horarios adyacentes**: Verificar que reservas consecutivas funcionan
3. **Solapamiento parcial**: Probar todos los tipos de solapamiento
4. **Consulta de disponibilidad**: Verificar disponibilidad en tiempo real

### Escenarios de Concurrencia Manejados

#### Escenario 1: Múltiples usuarios simultáneos
```
Usuario A: Cancha 1, 14:00-15:00
Usuario B: Cancha 1, 14:30-15:30 (solapamiento)
Usuario C: Cancha 1, 14:00-15:00 (exacto)

Resultado:
✅ 1 usuario: Reserva exitosa
❌ 2 usuarios: Error 409 "El espacio no está disponible"
```

#### Escenario 2: Reservas adyacentes (permitidas)
```
Usuario A: Cancha 1, 14:00-15:00
Usuario B: Cancha 1, 15:00-16:00 (sin solapamiento)

Resultado:
✅ Ambos usuarios: Reservas exitosas
```

#### Escenario 3: Tipos de solapamiento detectados
- **Solapamiento parcial**: `[14:00-15:00]` vs `[14:30-15:30]`
- **Contenida**: `[14:00-15:00]` vs `[14:15-14:45]`
- **Contiene**: `[14:00-15:00]` vs `[13:30-15:30]`
- **Exactamente igual**: `[14:00-15:00]` vs `[14:00-15:00]`

## Arquitectura del Sistema

### Componentes
```
├── schemas/reserva_schemas.py      # Validaciones y tipos de datos
├── services/reserva_service.py     # Lógica de negocio
├── api/routes/reserva_routes.py    # Endpoints REST
├── models/reserva.py               # Modelo de base de datos
└── models/espacio.py               # Modelo de espacios
```

### Algoritmo de Detección de Solapamiento
```python
def hay_solapamiento(inicio1, fin1, inicio2, fin2):
    """
    Detecta si dos reservas se solapan en el tiempo.
    
    Hay solapamiento si:
    - inicio1 < fin2 AND fin1 > inicio2
    """
    return inicio1 < fin2 and fin1 > inicio2
```

### Base de Datos
- **Índices optimizados**: `(id_espacio, inicio, fin)` para consultas rápidas
- **Constraints**: Verificación de integridad a nivel de BD
- **Transacciones**: Operaciones atómicas garantizadas

## Seguridad

### Autenticación
- **JWT Bearer Token**: Requerido para todos los endpoints
- **Verificación de vecino**: Solo vecinos registrados pueden reservar
- **Restricción por junta**: Solo espacios de la propia junta

### Autorización
- **Reservas propias**: Solo puedes ver/modificar tus reservas
- **Estados válidos**: Solo se pueden modificar reservas `PENDIENTE`
- **Cancelación**: Solo con 2+ horas de anticipación

## Configuración

### Variables de Entorno
```env
# En .env del backend
DATABASE_URL=postgresql://...
SECRET_KEY=tu_clave_secreta
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Configuración de Horarios
```python
# En reserva_service.py
HORA_INICIO = 12  # 12:00 PM
HORA_FIN = 22     # 22:00 PM (10:00 PM)

DURACION_MAXIMA = {
    TipoEspacio.CANCHA: 3,  # 3 horas máximo
    TipoEspacio.SALA: 6,    # 6 horas máximo
    TipoEspacio.PLAZA: 4,   # 4 horas máximo
    TipoEspacio.OTRO: 2,    # 2 horas máximo
}
```

## Instalación y Uso

### Requisitos
- Python 3.11+
- PostgreSQL
- Poetry

### Instalación
```bash
# Instalar dependencias
poetry install

# Configurar base de datos
poetry run alembic upgrade head

# Crear datos iniciales (opcional)
poetry run python create_initial_data.py

# Ejecutar servidor
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Documentación API
Una vez ejecutando el servidor:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Monitoreo y Logs

### Logs de Reservas
```python
# Los logs incluyen:
- Intentos de reserva
- Conflictos detectados
- Cancelaciones
- Errores de validación
```

### Métricas Importantes
- **Tasa de conflictos**: % de reservas rechazadas por solapamiento
- **Tiempo de respuesta**: Latencia de creación de reservas
- **Uso por espacio**: Estadísticas de ocupación

## Troubleshooting

### Problemas Comunes

#### Error 409: "El espacio no está disponible"
- **Causa**: Otra reserva ya ocupa ese horario
- **Solución**: Consultar disponibilidad y elegir otro horario

#### Error 400: "Horario no permitido"
- **Causa**: Reserva fuera del rango 12:00-22:00
- **Solución**: Ajustar horario al rango permitido

#### Error 403: "No tiene perfil de vecino"
- **Causa**: Usuario no registrado como vecino
- **Solución**: Completar registro de vecino

### Comandos de Diagnóstico
```bash
# Verificar estado de la base de datos
poetry run python -c "from src.database.session import engine; print('DB OK')"

# Ejecutar pruebas
poetry run python test_concurrencia_reservas.py

# Ver logs
tail -f logs/logs.log
```

## Contribución

### Agregar Nuevos Tipos de Espacio
1. Actualizar `TipoEspacio` en `reserva_schemas.py`
2. Configurar duraciones en `ReservaService`
3. Ejecutar migraciones si es necesario

### Modificar Validaciones
1. Editar validadores en `reserva_schemas.py`
2. Actualizar tests de validación
3. Documentar cambios

---

## 🎯 Garantías del Sistema

✅ **NUNCA habrá doble reserva del mismo horario**  
✅ **El primero en llegar obtiene la reserva**  
✅ **Mensajes de error claros para usuarios**  
✅ **Transacciones atómicas en base de datos**  
✅ **Detección precisa de cualquier tipo de solapamiento**  
✅ **Escalabilidad para cientos de usuarios simultáneos**  

---

*Sistema desarrollado para VecindApp - Gestión de Juntas de Vecinos*
