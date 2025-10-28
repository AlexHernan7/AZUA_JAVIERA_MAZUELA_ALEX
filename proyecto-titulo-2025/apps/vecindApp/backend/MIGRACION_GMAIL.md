# Migración a Gmail SMTP

## ✅ Cambios Realizados

Se ha migrado el servicio de envío de emails a **Gmail SMTP**, que es más directo y no requiere activación externa.

### Archivos Modificados

1. **requirements.txt**
   - ❌ Removido: `sib-api-v3-sdk>=7.6.0,<8.0.0`
   - ✅ Usa bibliotecas estándar de Python (`smtplib`, `email`)

2. **src/core/config.py**
   - Cambiado `BREVO_API_KEY` → `GMAIL_APP_PASSWORD`
   - Cambiado `BREVO_FROM_EMAIL` → `GMAIL_USER`
   - Cambiado `BREVO_FROM_NAME` → `EMAIL_FROM_NAME`

3. **src/services/email_service.py**
   - Reescrito completamente para usar Gmail SMTP
   - Mantiene la misma interfaz pública (métodos compatibles)

4. **src/api/routes/auth_routes.py**
   - Actualizado para usar las nuevas variables de configuración de Gmail

5. **ENV_VARIABLES_RAILWAY.md**
   - Documentación actualizada con las nuevas variables de entorno

## 🔑 Configurar Contraseña de Aplicación de Gmail

### Paso 1: Habilitar Verificación en 2 Pasos

1. Ve a https://myaccount.google.com/security
2. En "Cómo accedes a Google", selecciona "Verificación en 2 pasos"
3. Sigue las instrucciones para habilitarla (si no la tienes)

### Paso 2: Crear Contraseña de Aplicación

1. Ve a https://myaccount.google.com/apppasswords
2. Inicia sesión con tu cuenta **vecindapp66@gmail.com**
3. En "Selecciona la app", elige **"Correo"**
4. En "Selecciona el dispositivo", elige **"Otro (nombre personalizado)"**
5. Escribe: **"VecindApp Railway Backend"**
6. Click en **"Generar"**
7. **Copia la contraseña de 16 caracteres** (sin espacios)

Ejemplo: `abcd efgh ijkl mnop` → usa `abcdefghijklmnop`

## 🚀 Configurar en Railway

### Variables de Entorno Necesarias

1. Ve a tu proyecto en Railway
2. Selecciona el servicio del backend
3. Ve a la pestaña **"Variables"**
4. Agrega estas 3 variables:

```bash
GMAIL_USER=vecindapp66@gmail.com
GMAIL_APP_PASSWORD=tu_contraseña_de_aplicacion_16_caracteres
EMAIL_FROM_NAME=VecindApp
```

**⚠️ IMPORTANTE:** 
- Usa la contraseña de aplicación, NO tu contraseña normal de Gmail
- La contraseña son 16 caracteres sin espacios
- Elimina las variables antiguas de Brevo si las tienes

### Variables a Eliminar (Opcional)

Puedes eliminar estas si ya no las usas:
- `BREVO_API_KEY`
- `BREVO_FROM_EMAIL`
- `BREVO_FROM_NAME`

## 🧪 Probar la Funcionalidad

### Desde el Frontend

1. Ve a la pantalla de "Olvidé mi contraseña"
2. Ingresa un email registrado
3. Deberías recibir un email de `vecindapp66@gmail.com` con el código

### Logs Esperados en Railway

**✅ Éxito:**
```
🔐 Solicitud de recuperación de contraseña para: usuario@example.com
✅ Email enviado exitosamente a usuario@example.com desde Gmail
✅ Código de recuperación enviado a usuario@example.com
```

**❌ Error (contraseña incorrecta):**
```
❌ Error de autenticación Gmail: (535, b'5.7.8 Username and Password not accepted')
💡 Verifica que uses una contraseña de aplicación, no tu contraseña normal
```

**❌ Error (verificación 2 pasos no habilitada):**
```
❌ Error de autenticación Gmail: (534, b'5.7.9 Please log in via your web browser')
```

## 🔍 Solución de Problemas

### Error: "Username and Password not accepted"

**Causas posibles:**
1. Estás usando tu contraseña normal en vez de la contraseña de aplicación
2. La contraseña de aplicación está mal copiada (tiene espacios o caracteres extra)
3. No has habilitado verificación en 2 pasos

**Solución:**
1. Verifica que tienes verificación en 2 pasos activa
2. Genera una nueva contraseña de aplicación
3. Cópiala sin espacios
4. Actualiza `GMAIL_APP_PASSWORD` en Railway

### Error: "Please log in via your web browser"

**Causa:** No tienes verificación en 2 pasos habilitada.

**Solución:**
1. Ve a https://myaccount.google.com/security
2. Habilita "Verificación en 2 pasos"
3. Luego crea la contraseña de aplicación

### Error: "SMTP connection timeout"

**Causa:** Railway puede estar bloqueando el puerto 587.

**Solución:** Ya está configurado correctamente con TLS en el puerto 587, que es el estándar.

### El email va a spam

**Solución:**
1. Los primeros emails pueden ir a spam
2. Marca como "No es spam" en Gmail
3. Gmail aprenderá que tus emails son legítimos

## 📊 Ventajas de Gmail SMTP vs Brevo

| Característica | Gmail SMTP | Brevo |
|----------------|-----------|-------|
| Configuración | ✅ Inmediata (con contraseña app) | ❌ Requiere activación manual |
| Límite gratuito | 500 emails/día | 300 emails/día (si activan) |
| Dependencias | ✅ Bibliotecas estándar Python | ❌ SDK externo |
| Autenticación | Contraseña de aplicación | API key |
| Complejidad setup | Muy simple | Media-Alta |
| Confiabilidad | ⭐⭐⭐⭐⭐ Alta | ⭐⭐⭐ Media |

## ⚠️ Limitaciones de Gmail

- **Límite diario:** 500 emails por día con cuenta gratuita
- **Emails por segundo:** ~1-2 emails/segundo
- **Para producción alta escala:** Considera servicios como SendGrid, Mailgun, o AWS SES

## ✅ Checklist Final

- [ ] Verificación en 2 pasos habilitada en Gmail
- [ ] Contraseña de aplicación creada
- [ ] Variables configuradas en Railway:
  - [ ] `GMAIL_USER=vecindapp66@gmail.com`
  - [ ] `GMAIL_APP_PASSWORD=contraseña_16_chars`
  - [ ] `EMAIL_FROM_NAME=VecindApp`
- [ ] Código desplegado en Railway
- [ ] Prueba de envío realizada
- [ ] Email recibido correctamente

## 📧 Estado Actual

- ✅ **Email configurado:** vecindapp66@gmail.com
- ✅ **Método:** Gmail SMTP con TLS
- ✅ **Puerto:** 587
- ✅ **Servidor:** smtp.gmail.com

---

**Fecha de migración:** Octubre 2025  
**Razón:** Brevo requería activación manual, Gmail SMTP es inmediato

