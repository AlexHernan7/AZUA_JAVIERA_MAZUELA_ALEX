# 🚨 CONFIGURACIÓN URGENTE - SMTP2GO

## ❌ Problema Detectado

SMTP2GO rechazó el envío de email con este error:
```
From header sender domain not verified (vecindapp.cl)
```

**Causa**: El email del remitente debe estar verificado en SMTP2GO antes de poder enviar emails.

---

## ✅ SOLUCIÓN INMEDIATA (2 opciones)

### 🎯 **OPCIÓN 1: Usar tu email personal (MÁS RÁPIDO)**

Si tienes una cuenta de Gmail, Outlook, o cualquier email personal:

#### 1. Actualiza el archivo `.env`:

```env
# Reemplaza con TU EMAIL PERSONAL (el que usas normalmente)
SMTP_FROM_EMAIL=tu_email@gmail.com

# O usa el email con el que te registraste en SMTP2GO
SMTP_FROM_EMAIL=al.mazuela@duocuc.cl
```

#### 2. Reinicia el servidor:
```bash
# Detén el servidor (Ctrl+C)
# Vuelve a iniciarlo
cd proyecto-titulo-2025/apps/vecindApp/backend
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. Prueba nuevamente ✅

---

### 🎯 **OPCIÓN 2: Verificar dominio en SMTP2GO (Más complejo)**

Si quieres usar `noreply@vecindapp.cl` o cualquier email personalizado:

#### Paso 1: Accede a SMTP2GO
1. Ve a https://app.smtp2go.com/
2. Inicia sesión con tu cuenta

#### Paso 2: Ir a Verified Senders
1. En el menú lateral, haz clic en **"Sending"**
2. Selecciona **"Verified Senders"**

#### Paso 3: Agregar Sender
1. Haz clic en **"Add Sender"**
2. Tienes 2 opciones:

   **A. Verificar un Email específico:**
   - Ingresa: `noreply@vecindapp.cl`
   - SMTP2GO te enviará un email de verificación
   - Haz clic en el link de verificación
   - ⚠️ **Problema**: Necesitas acceso a ese email

   **B. Verificar un Dominio completo:**
   - Ingresa: `vecindapp.cl`
   - SMTP2GO te dará registros DNS para agregar
   - Necesitas acceso al panel de control del dominio
   - Agrega los registros DNS (SPF, DKIM, DMARC)
   - ⚠️ **Problema**: Necesitas ser dueño del dominio

#### Paso 4: Esperar verificación
- La verificación puede tomar desde minutos hasta 24 horas

---

## 🚀 RECOMENDACIÓN PARA DESARROLLO

### Usa tu email personal temporalmente

Para desarrollo y pruebas, la forma más rápida es:

1. **Actualiza `.env` con tu email personal:**

```env
# ========================================
# CONFIGURACIÓN DE EMAIL - SMTP2GO
# ========================================
SMTP2GO_API_KEY=api-6E020687483F478A8971FA5386400333

# USA TU EMAIL PERSONAL AQUÍ (Gmail, Outlook, etc.)
SMTP_FROM_EMAIL=al.mazuela@duocuc.cl

# El nombre que aparecerá como remitente
SMTP_FROM_NAME=VecindApp
```

2. **Reinicia el servidor:**
```bash
cd proyecto-titulo-2025/apps/vecindApp/backend
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

3. **¡Listo! Ya debería funcionar** 🎉

---

## 📧 ¿Qué email puedo usar?

### ✅ Emails que SÍ funcionan:
- Tu email personal (Gmail, Outlook, Yahoo, etc.)
- El email con el que te registraste en SMTP2GO
- Cualquier email que hayas verificado en SMTP2GO

### ❌ Emails que NO funcionan (sin verificar):
- `noreply@vecindapp.cl` (dominio no verificado)
- `info@vecindapp.cl` (dominio no verificado)
- Cualquier email de un dominio que no controlas

---

## 🔍 Verificar si un email está permitido

1. Ve a https://app.smtp2go.com/
2. Ve a **Sending > Verified Senders**
3. Revisa la lista de senders verificados
4. Usa uno de esos emails en `SMTP_FROM_EMAIL`

---

## 📝 Ejemplo de configuración funcional

```env
# ========================================
# CONFIGURACIÓN FUNCIONAL DE SMTP2GO
# ========================================

# Tu API Key (no cambiar)
SMTP2GO_API_KEY=api-6E020687483F478A8971FA5386400333

# OPCIÓN A: Email personal/institucional
SMTP_FROM_EMAIL=al.mazuela@duocuc.cl
SMTP_FROM_NAME=VecindApp - Alex Mazuela

# OPCIÓN B: Gmail personal
# SMTP_FROM_EMAIL=tu_email@gmail.com
# SMTP_FROM_NAME=VecindApp

# OPCIÓN C: Email verificado en SMTP2GO
# SMTP_FROM_EMAIL=email_verificado@ejemplo.com
# SMTP_FROM_NAME=VecindApp
```

---

## 🧪 Probar después de configurar

1. Reinicia el servidor backend
2. Ve a http://localhost:4200/forgot-password
3. Ingresa el email de un usuario registrado
4. Deberías recibir el código por email ✅

---

## ⚠️ IMPORTANTE

- **Para desarrollo**: Usa tu email personal (más rápido)
- **Para producción**: Deberás verificar el dominio `vecindapp.cl` o comprar uno y verificarlo

---

## 🆘 Si sigue sin funcionar

Revisa los logs del backend:
```bash
# Los logs mostrarán el error específico
# Busca líneas con "❌" o "ERROR"
```

O contacta al soporte de SMTP2GO:
- https://www.smtp2go.com/support/

---

## ✅ Checklist rápido

- [ ] Actualizar `SMTP_FROM_EMAIL` en `.env` con un email válido
- [ ] Reiniciar el servidor backend
- [ ] Probar enviando código de recuperación
- [ ] Verificar que llegue el email
- [ ] ¡Celebrar! 🎉

---

**💡 TIP**: El email del remitente solo afecta el "From" que ve el usuario. Los emails llegarán igual a la bandeja de entrada del destinatario.

