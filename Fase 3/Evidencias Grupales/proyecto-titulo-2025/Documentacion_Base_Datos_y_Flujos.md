# Documentación de Base de Datos y Flujos de Datos
## Sistema VecindApp - Gestión de Juntas de Vecinos

---

## Índice
1. [Arquitectura General del Sistema](#arquitectura-general)
2. [Estructura de Base de Datos](#estructura-base-datos)
3. [Relaciones Entre Tablas](#relaciones-entre-tablas)
4. [Flujos de Datos Principales](#flujos-datos-principales)
5. [Flujos de Pago](#flujos-pago)
6. [Diagramas de Flujo](#diagramas-flujo)

---

## Arquitectura General del Sistema {#arquitectura-general}

### Tecnologías Utilizadas
- **Backend**: FastAPI (Python)
- **Frontend**: Angular 17
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (JSON Web Tokens)
- **Pagos**: Webpay Plus (Transbank)
- **Workspace**: Nx Monorepo

### Estructura del Proyecto
```
proyecto-titulo-2025/
├── apps/
│   └── vecindApp/
│       ├── backend/          # API FastAPI
│       └── frontend/         # Aplicación Angular
└── libs/                     # Librerías compartidas
```

---

## Estructura de Base de Datos {#estructura-base-datos}

### Tablas Principales

#### 1. **users** - Usuarios del Sistema
```sql
CREATE TABLE users (
    id_user SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellido_paterno VARCHAR(100) NOT NULL,
    apellido_materno VARCHAR(100),
    rut VARCHAR(12) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    roles TEXT[] DEFAULT '{"vecino"}',
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. **juntas_vecinos** - Juntas de Vecinos
```sql
CREATE TABLE juntas_vecinos (
    id_junta SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    direccion TEXT NOT NULL,
    comuna VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(255),
    presidente_rut VARCHAR(12),
    activa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. **vecinos** - Perfiles de Vecinos
```sql
CREATE TABLE vecinos (
    id_vecino SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id_user) ON DELETE CASCADE,
    junta_id INTEGER REFERENCES juntas_vecinos(id_junta) ON DELETE SET NULL,
    rut VARCHAR(12) UNIQUE NOT NULL,
    direccion TEXT NOT NULL,
    numero_casa VARCHAR(10),
    foto_perfil VARCHAR(500),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. **espacios_comunitarios** - Espacios para Reservar
```sql
CREATE TABLE espacios_comunitarios (
    id_espacio SERIAL PRIMARY KEY,
    junta_id INTEGER REFERENCES juntas_vecinos(id_junta) ON DELETE CASCADE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL, -- 'cancha', 'sala', 'plaza'
    capacidad INTEGER NOT NULL,
    valor DECIMAL(10,2) NOT NULL, -- Valor por hora en CLP
    foto VARCHAR(500),
    permitido TEXT[], -- Actividades permitidas
    no_permitido TEXT[], -- Actividades no permitidas
    max_horas INTEGER DEFAULT 4,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. **reservas** - Reservas de Espacios
```sql
CREATE TABLE reservas (
    id_reserva SERIAL PRIMARY KEY,
    espacio_id INTEGER REFERENCES espacios_comunitarios(id_espacio) ON DELETE CASCADE,
    vecino_id INTEGER REFERENCES vecinos(id_vecino) ON DELETE CASCADE,
    junta_id INTEGER REFERENCES juntas_vecinos(id_junta) ON DELETE CASCADE,
    inicio TIMESTAMP NOT NULL,
    fin TIMESTAMP NOT NULL,
    motivo TEXT NOT NULL,
    asistentes INTEGER,
    observaciones TEXT,
    estado VARCHAR(20) DEFAULT 'pendiente_pago', -- 'pendiente_pago', 'confirmada', 'cancelada'
    valor_reserva DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. **certificados_pedidos** - Solicitudes de Certificados
```sql
CREATE TABLE certificados_pedidos (
    id_pedido SERIAL PRIMARY KEY,
    vecino_id INTEGER REFERENCES vecinos(id_vecino) ON DELETE CASCADE,
    motivo_solicitud TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente_pago', -- 'pendiente_pago', 'generado', 'entregado'
    valor_certificado DECIMAL(10,2) DEFAULT 2000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. **certificados** - Certificados Generados
```sql
CREATE TABLE certificados (
    id_certificado SERIAL PRIMARY KEY,
    pedido_id INTEGER REFERENCES certificados_pedidos(id_pedido) ON DELETE CASCADE,
    numero VARCHAR(50) UNIQUE NOT NULL,
    fecha_emision DATE NOT NULL,
    fecha_vencimiento DATE NOT NULL,
    pdf_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. **payment_intents** - Intenciones de Pago
```sql
CREATE TABLE payment_intents (
    id_payment_intent SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id_user) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL, -- 'certificado', 'reserva'
    entity_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CLP',
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    description TEXT NOT NULL,
    external_id VARCHAR(255), -- ID de Transbank
    extra_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Relaciones Entre Tablas {#relaciones-entre-tablas}

### Diagrama de Relaciones
```
users (1) ──→ (1) vecinos
  │                │
  │                │
  └──→ (1) payment_intents    vecinos (N) ──→ (1) juntas_vecinos
                                      │
                                      │
                              juntas_vecinos (1) ──→ (N) espacios_comunitarios
                                                              │
                                                              │
                                                      espacios_comunitarios (1) ──→ (N) reservas
                                                                                      │
                                                                                      │
                                                                              vecinos (1) ──→ (N) reservas
                                                                                      │
                                                                                      │
                                                                              vecinos (1) ──→ (N) certificados_pedidos
                                                                                      │
                                                                                      │
                                                                              certificados_pedidos (1) ──→ (1) certificados
```

### Relaciones Detalladas

#### 1. **users ↔ vecinos** (1:1)
- Un usuario tiene un perfil de vecino
- Relación obligatoria para acceder al sistema
- `vecinos.user_id` → `users.id_user`

#### 2. **vecinos ↔ juntas_vecinos** (N:1)
- Un vecino pertenece a una junta
- Una junta tiene muchos vecinos
- `vecinos.junta_id` → `juntas_vecinos.id_junta`

#### 3. **juntas_vecinos ↔ espacios_comunitarios** (1:N)
- Una junta tiene muchos espacios
- Un espacio pertenece a una junta
- `espacios_comunitarios.junta_id` → `juntas_vecinos.id_junta`

#### 4. **espacios_comunitarios ↔ reservas** (1:N)
- Un espacio puede tener muchas reservas
- Una reserva es para un espacio específico
- `reservas.espacio_id` → `espacios_comunitarios.id_espacio`

#### 5. **vecinos ↔ reservas** (1:N)
- Un vecino puede hacer muchas reservas
- Una reserva es hecha por un vecino
- `reservas.vecino_id` → `vecinos.id_vecino`

#### 6. **vecinos ↔ certificados_pedidos** (1:N)
- Un vecino puede solicitar muchos certificados
- Un pedido es hecho por un vecino
- `certificados_pedidos.vecino_id` → `vecinos.id_vecino`

#### 7. **certificados_pedidos ↔ certificados** (1:1)
- Un pedido genera un certificado
- Un certificado proviene de un pedido
- `certificados.pedido_id` → `certificados_pedidos.id_pedido`

#### 8. **users ↔ payment_intents** (1:N)
- Un usuario puede tener muchas intenciones de pago
- Una intención de pago pertenece a un usuario
- `payment_intents.user_id` → `users.id_user`

---

## Flujos de Datos Principales {#flujos-datos-principales}

### 1. Flujo de Registro de Usuario

#### 1.1 Registro Inicial
```
Frontend (Angular) → Backend (FastAPI) → Base de Datos
```

**Pasos:**
1. Usuario completa formulario de registro
2. Frontend valida datos y envía POST a `/api/auth/register`
3. Backend valida datos y crea registro en tabla `users`
4. Se genera hash de contraseña con bcrypt
5. Se asigna rol por defecto: `["vecino"]`
6. Se retorna respuesta de éxito

#### 1.2 Creación de Perfil de Vecino
```
Usuario registrado → Completar perfil → Tabla vecinos
```

**Pasos:**
1. Usuario inicia sesión
2. Sistema detecta que no tiene perfil de vecino
3. Redirige a formulario de perfil
4. Usuario completa datos (dirección, número de casa, etc.)
5. Se crea registro en tabla `vecinos` vinculado al `user_id`
6. Se asigna a una junta existente

### 2. Flujo de Gestión de Juntas

#### 2.1 Creación de Junta (Admin/Directiva)
```
Admin → Formulario → Backend → Tabla juntas_vecinos
```

**Pasos:**
1. Usuario con rol admin/directiva accede a "Crear Junta"
2. Completa formulario con datos de la junta
3. Backend valida y crea registro en `juntas_vecinos`
4. Se establece presidente (opcional)
5. Junta queda activa y disponible para asignar vecinos

#### 2.2 Asignación de Vecinos a Junta
```
Admin → Gestión → Asignar vecino → Actualizar vecinos.junta_id
```

**Pasos:**
1. Admin accede a gestión de vecinos
2. Selecciona vecino sin junta asignada
3. Asigna a junta específica
4. Se actualiza `vecinos.junta_id`

### 3. Flujo de Gestión de Espacios

#### 3.1 Creación de Espacio (Admin/Directiva)
```
Admin → Formulario → Backend → Tabla espacios_comunitarios
```

**Pasos:**
1. Admin accede a "Crear Espacio"
2. Completa formulario (nombre, tipo, capacidad, valor, etc.)
3. Sube foto del espacio (opcional)
4. Define actividades permitidas/no permitidas
5. Backend crea registro en `espacios_comunitarios`
6. Espacio queda disponible para reservas

### 4. Flujo de Reservas de Espacios

#### 4.1 Verificación de Disponibilidad
```
Vecino → Selecciona espacio → Verifica disponibilidad → Backend valida
```

**Pasos:**
1. Vecino selecciona espacio comunitario
2. Completa formulario (fecha, hora inicio, hora fin, motivo)
3. Frontend valida fechas/horarios no pasados
4. Backend verifica disponibilidad consultando tabla `reservas`
5. Retorna resultado de disponibilidad

#### 4.2 Creación de Reserva
```
Vecino → Confirma → Backend → Tabla reservas → Estado "pendiente_pago"
```

**Pasos:**
1. Vecino confirma datos de reserva
2. Backend calcula valor total (horas × valor por hora)
3. Se crea registro en `reservas` con estado "pendiente_pago"
4. Se inicia proceso de pago

---

## Flujos de Pago {#flujos-pago}

### 1. Flujo de Pago de Certificados

#### 1.1 Solicitud de Certificado
```
Vecino → Formulario → Backend → Tabla certificados_pedidos
```

**Pasos:**
1. Vecino accede a "Crear Certificado"
2. Completa motivo de solicitud
3. Backend crea registro en `certificados_pedidos` (estado: "pendiente_pago")
4. Se inicia proceso de pago

#### 1.2 Proceso de Pago Webpay
```
Backend → Webpay Service → Transbank → Usuario → Pago → Retorno
```

**Pasos:**
1. Backend crea `payment_intent` (entity_type: "certificado")
2. Webpay Service genera transacción en Transbank
3. Usuario es redirigido a Webpay para pagar
4. Usuario completa pago con tarjeta
5. Transbank retorna resultado a endpoint `/api/payments/webpay/return`
6. Backend actualiza `payment_intent` (status: "completed")
7. Se libera certificado (estado: "generado")
8. Se genera PDF del certificado

### 2. Flujo de Pago de Reservas

#### 2.1 Proceso de Pago de Reserva
```
Vecino → Confirma reserva → Backend → Webpay → Pago → Confirmación
```

**Pasos:**
1. Vecino confirma datos de reserva
2. Backend crea `payment_intent` (entity_type: "reserva")
3. Webpay Service genera transacción
4. Usuario paga con tarjeta
5. Transbank retorna resultado
6. Backend actualiza `payment_intent` (status: "completed")
7. Se confirma reserva (estado: "confirmada")

### 3. Estructura de Payment Intents

#### 3.1 Para Certificados
```json
{
  "entity_type": "certificado",
  "entity_id": 123, // ID del certificado_pedido
  "amount": 2000.00,
  "description": "Certificado de residencia - Juan Pérez",
  "extra_data": {
    "certificado_pedido_id": 123,
    "motivo_solicitud": "Trámite bancario",
    "vecino_rut": "12345678-9"
  }
}
```

#### 3.2 Para Reservas
```json
{
  "entity_type": "reserva",
  "entity_id": 456, // ID de la reserva
  "amount": 5000.00,
  "description": "Reserva Cancha de Fútbol",
  "extra_data": {
    "reserva_id": 456,
    "espacio_nombre": "Cancha de Fútbol",
    "fecha": "2025-10-03",
    "hora_inicio": "13:00",
    "hora_termino": "14:00",
    "vecino_rut": "12345678-9"
  }
}
```

---

## Diagramas de Flujo {#diagramas-flujo}

### 1. Flujo de Registro y Autenticación

```
[Usuario] → [Formulario Registro] → [Backend] → [Tabla users]
     ↓
[Login] → [JWT Token] → [Frontend] → [Acceso al Sistema]
     ↓
[Completar Perfil] → [Tabla vecinos] → [Asignar a Junta]
```

### 2. Flujo de Reserva de Espacio

```
[Vecino] → [Seleccionar Espacio] → [Completar Formulario]
     ↓
[Verificar Disponibilidad] → [Backend Valida] → [Disponible]
     ↓
[Confirmar Reserva] → [Crear payment_intent] → [Webpay]
     ↓
[Pago Exitoso] → [Confirmar Reserva] → [Estado: "confirmada"]
```

### 3. Flujo de Certificado

```
[Vecino] → [Solicitar Certificado] → [Completar Motivo]
     ↓
[Crear certificados_pedidos] → [payment_intent] → [Webpay]
     ↓
[Pago Exitoso] → [Generar PDF] → [certificados] → [Descargar]
```

### 4. Flujo de Pago Webpay

```
[Backend] → [Webpay Service] → [Transbank API]
     ↓
[Token + URL] → [Frontend] → [Redirección a Webpay]
     ↓
[Usuario Paga] → [Transbank] → [Return URL] → [Backend]
     ↓
[Confirmar Transacción] → [Actualizar payment_intent] → [Procesar Entidad]
```

---

## Consideraciones Técnicas

### 1. Seguridad
- **Contraseñas**: Hash con bcrypt
- **JWT**: Tokens con expiración
- **Validaciones**: Frontend y Backend
- **CORS**: Configurado para desarrollo

### 2. Integración Webpay
- **Ambiente**: Integración (testing)
- **Tarjetas de Prueba**: Configuradas
- **Retorno**: Endpoint dedicado
- **Logs**: Extensivos para debugging

### 3. Validaciones de Negocio
- **Fechas**: No permitir fechas pasadas
- **Horarios**: No permitir horarios pasados
- **Disponibilidad**: Verificar conflictos
- **Roles**: Restricciones por tipo de usuario

### 4. Estados de Entidades
- **Reservas**: pendiente_pago → confirmada → cancelada
- **Certificados**: pendiente_pago → generado → entregado
- **Payment Intents**: pending → completed → failed

---

## Conclusión

Este sistema implementa una arquitectura robusta para la gestión de juntas de vecinos, con:

1. **Separación clara de responsabilidades** entre frontend y backend
2. **Base de datos normalizada** con relaciones bien definidas
3. **Flujos de pago integrados** con Webpay Plus
4. **Validaciones de negocio** en múltiples capas
5. **Sistema de roles** para diferentes tipos de usuarios
6. **Trazabilidad completa** de transacciones y pagos

La estructura permite escalabilidad y mantenimiento, cumpliendo con los requisitos de una aplicación de gestión comunitaria moderna.

---

*Documento generado para la defensa del proyecto de título - Sistema VecindApp*
*Fecha: Octubre 2025*
