# Migración de Resend a Brevo

## ✅ Cambios Realizados

Se ha migrado exitosamente el servicio de envío de emails de **Resend** a **Brevo** (SendinBlue).

### Archivos Modificados

1. **requirements.txt**
   - ❌ Removido: `resend>=2.0.0,<3.0.0`
   - ✅ Agregado: `sib-api-v3-sdk>=7.6.0,<8.0.0`

2. **src/core/config.py**
   - Cambiado `RESEND_API_KEY` → `BREVO_API_KEY`
   - Cambiado `RESEND_FROM_EMAIL` → `BREVO_FROM_EMAIL`
   - Agregado `BREVO_FROM_NAME`

3. **src/services/email_service.py**
   - Reescrito completamente para usar la API de Brevo
   - Mantiene la misma interfaz pública (métodos compatibles)

4. **src/api/routes/auth_routes.py**
   - Actualizado para usar las nuevas variables de configuración de Brevo

5. **ENV_VARIABLES_RAILWAY.md**
   - Documentación actualizada con las nuevas variables de entorno

## 🚀 Pasos para Desplegar en Railway

### 1. Instalar Nuevas Dependencias

En Railway, las dependencias se instalan automáticamente desde `requirements.txt`, pero puedes forzar la reinstalación:

```bash
# Si estás en local, actualiza tus dependencias:
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno en Railway

Ya tienes configurada la API key de Brevo, pero debes verificar estas 3 variables:

1. Ve a tu proyecto en Railway
2. Selecciona el servicio del backend
3. Ve a la pestaña "Variables"
4. Verifica/agrega estas variables:

```bash
BREVO_API_KEY=xkeysib-tu_api_key_de_brevo_aqui
BREVO_FROM_EMAIL=vecindapp66@gmail.com
BREVO_FROM_NAME=VecindApp
```

> **⚠️ IMPORTANTE:** Nunca expongas tu API key real en el código. Mantenla solo en las variables de entorno de Railway.

**⚠️ IMPORTANTE sobre BREVO_FROM_EMAIL:**

- Si usas un **dominio NO verificado** en Brevo, usa el email que hayas verificado en tu cuenta de Brevo
- Para usar `noreply@vecindapp.com`, debes:
  1. Ir a Brevo → Settings → Senders & IP
  2. Agregar y verificar el dominio `vecindapp.com`
  3. Configurar registros DNS (SPF, DKIM)
- Mientras tanto, puedes usar tu email personal verificado

### 3. Eliminar Variables Antiguas (Opcional)

Puedes eliminar las variables antiguas de Resend si ya no las usas:
- `RESEND_API_KEY`
- `RESEND_FROM_EMAIL`

### 4. Redesplegar

Railway debería redesplegar automáticamente al detectar los cambios en Git. Si no lo hace:

1. Ve a tu proyecto en Railway
2. Click en "Deploy" o "Redeploy"
3. O haz un nuevo commit y push a tu repositorio

### 5. Verificar Logs

Después del despliegue, verifica los logs en Railway:

```
✅ Busca: "Email enviado exitosamente" cuando se envíe un código de recuperación
❌ Busca errores: "Error de API Brevo" o "Error inesperado enviando email"
```

## 🧪 Probar la Funcionalidad

### Desde el Frontend

1. Ve a la pantalla de "Olvidé mi contraseña"
2. Ingresa un email registrado
3. Deberías recibir un email con el código de 6 dígitos

### Logs Esperados

**✅ Éxito:**
```
🔐 Solicitud de recuperación de contraseña para: usuario@example.com
✅ Email enviado exitosamente a usuario@example.com (ID: <message_id_brevo>)
✅ Código de recuperación enviado a usuario@example.com
```

**❌ Error (API key inválida):**
```
❌ Error de API Brevo: Unauthorized
```

**❌ Error (email no verificado):**
```
❌ Error de API Brevo: Sender email not verified
```

## 🔍 Solución de Problemas

### Error: "Sender email not verified"

**Causa:** El email del remitente no está verificado en Brevo.

**Solución:**
1. Ve a https://app.brevo.com/settings/senders
2. Agrega y verifica un email o dominio
3. Actualiza la variable `BREVO_FROM_EMAIL` en Railway con el email verificado

### Error: "Unauthorized" o "Invalid API key"

**Causa:** La API key de Brevo es inválida o está mal configurada.

**Solución:**
1. Ve a https://app.brevo.com/settings/keys/api
2. Verifica tu API key (debe empezar con `xkeysib-`)
3. Actualiza la variable `BREVO_API_KEY` en Railway

### Error: "Account suspended" o límite de envío

**Causa:** Cuenta de Brevo suspendida o límite diario alcanzado.

**Solución:**
1. Verifica el estado de tu cuenta en Brevo
2. Revisa el plan gratuito (300 emails/día)
3. Considera upgrade si necesitas más

## 📊 Límites de Brevo

### Plan Gratuito
- ✅ 300 emails por día
- ✅ Emails transaccionales ilimitados (API)
- ❌ Email marketing limitado

### Para Producción
- Considera un plan de pago si esperas más de 300 recuperaciones de contraseña por día
- O combina con otro servicio para respaldo

## 🔄 Diferencias Clave: Resend vs Brevo

| Característica | Resend | Brevo |
|----------------|--------|-------|
| SDK | `resend` | `sib-api-v3-sdk` |
| Verificación de dominio | Opcional (usa resend.dev) | **Obligatoria** para dominios propios |
| Plan gratuito | 100 emails/día | 300 emails/día |
| API key format | `re_*` | `xkeysib-*` |
| Complejidad setup | Muy simple | Media (requiere verificación) |

## ✅ Checklist Final

- [x] Dependencias actualizadas (`requirements.txt`)
- [x] Variables de entorno configuradas en Railway
- [ ] Email remitente verificado en Brevo
- [ ] Redespliegue en Railway completado
- [ ] Prueba de envío de código realizada
- [ ] Logs verificados sin errores

## 📧 ¿Necesitas ayuda?

Si tienes problemas:
1. Revisa los logs de Railway
2. Verifica la configuración en Brevo Dashboard
3. Consulta la documentación oficial: https://developers.brevo.com/docs

---

**Fecha de migración:** Octubre 2025
**Versión SDK Brevo:** 7.6.0+


