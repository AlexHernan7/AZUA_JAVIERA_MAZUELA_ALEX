# 🎯 Empieza Aquí: Deployment y Distribución

## ¿Qué se ha preparado?

Tu aplicación **vecindApp** está completamente lista para:

1. ✅ **Ser desplegada en Railway** (backend en la nube)
2. ✅ **Conectarse desde web y móvil** (CORS configurado)
3. ✅ **Generar APKs de Android** (para distribución)
4. ✅ **Ser publicada en Play Store** (cuando estés listo)

---

## 🚀 Los 3 Pasos Principales

### **Paso 1: Desplegar Backend en Railway** (30-60 min)

**Qué vas a hacer**: Subir tu backend a Internet para que sea accesible desde cualquier lugar.

**Por qué es importante**: Sin esto, tu app móvil y frontend no podrán funcionar fuera de tu computadora.

**Sigue esta guía**: 📖 **[DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md)**

**Resumen rápido**:
1. Crea cuenta en https://railway.app (gratis)
2. Conecta tu repositorio GitHub
3. Configura el directorio: `apps/vecindApp/backend`
4. Agrega PostgreSQL (con un click)
5. Configura variables de entorno (SECRET_KEY, etc.)
6. Ejecuta migraciones
7. ¡Listo! Tu API está en línea 🎉

**URL resultante**: `https://tu-backend.up.railway.app`

---

### **Paso 2: Conectar Frontend al Backend** (15 min)

**Qué vas a hacer**: Actualizar las URLs para que apunten al backend en Railway.

**Por qué es importante**: Sin esto, tu app seguirá buscando `localhost:8000` que no existe en producción.

**Sigue esta guía**: 📖 **[CONFIGURAR_API_URL.md](CONFIGURAR_API_URL.md)**

**Resumen rápido**:
1. Abre `apps/vecindApp/frontend/src/environments/environment.prod.ts`
2. Cambia `TU_URL_DE_RAILWAY_AQUI` por la URL real de Railway
3. Ejecuta:
   ```bash
   npm run build:mobile
   npm run cap:sync:android
   ```
4. ¡Listo! Tu app apunta al backend en la nube 🎉

---

### **Paso 3: Generar APK para Distribución** (30 min)

**Qué vas a hacer**: Crear el archivo APK para instalar en dispositivos Android.

**Por qué es importante**: Sin esto, solo puedes probar en Android Studio. Con el APK, puedes enviar la app a quien quieras.

**Sigue esta guía**: 📖 **[GENERAR_APK.md](GENERAR_APK.md)**

**Resumen rápido**:

**Para testing (APK Debug)**:
```bash
cd android
./gradlew assembleDebug
# APK en: android/app/build/outputs/apk/debug/app-debug.apk
```

**Para producción (APK Release)**:
```bash
# 1. Crear keystore (solo una vez)
keytool -genkey -v -keystore vecindapp-release-key.keystore -alias vecindapp -keyalg RSA -keysize 2048 -validity 10000

# 2. Configurar firma en build.gradle (ver guía)

# 3. Generar APK firmado
./gradlew assembleRelease
# APK en: android/app/build/outputs/apk/release/app-release.apk
```

¡Listo! Ahora puedes compartir el APK 🎉

---

## 📚 Documentación Completa

| Archivo | Para qué es | Cuándo leerlo |
|---------|-------------|---------------|
| 📄 **[RESUMEN_DEPLOYMENT.md](RESUMEN_DEPLOYMENT.md)** | Vista general de todo | Si quieres ver el panorama completo |
| 🚀 **[DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md)** | Subir backend a Railway | **Paso 1 - EMPIEZA AQUÍ** |
| 🔗 **[CONFIGURAR_API_URL.md](CONFIGURAR_API_URL.md)** | Conectar frontend | **Paso 2 - Después de Railway** |
| 📦 **[GENERAR_APK.md](GENERAR_APK.md)** | Crear APK Android | **Paso 3 - Después de configurar** |
| ⚙️ **[ENV_VARIABLES_RAILWAY.md](apps/vecindApp/backend/ENV_VARIABLES_RAILWAY.md)** | Variables de entorno | Referencia durante Railway |
| 🤖 **[CAPACITOR_ANDROID_GUIDE.md](CAPACITOR_ANDROID_GUIDE.md)** | Guía completa Capacitor | Si tienes dudas sobre Android |
| 📱 **[PROXIMOS_PASOS_ANDROID.md](PROXIMOS_PASOS_ANDROID.md)** | Checklist Android | Si recién instalaste Capacitor |

---

## ⏱️ ¿Cuánto Tiempo Toma?

### Primera Vez (Todo desde cero)

- ⏰ **Railway**: 30-60 min (incluye crear cuenta, configurar, etc.)
- ⏰ **Configurar URLs**: 15 min
- ⏰ **Generar APK**: 30 min (incluye crear keystore)
- **Total**: ~1.5 - 2 horas

### Siguientes Veces (Ya configurado)

- ⏰ **Update & Deploy**: 5-10 min (push a GitHub → Railway redespliega automático)
- ⏰ **Rebuild APK**: 10 min (ya tienes keystore configurado)
- **Total**: ~15-20 min

---

## 💰 ¿Cuánto Cuesta?

### Railway
- **Gratis**: $5 USD mensuales de crédito
- **Costo típico**: $10-15 USD/mes (backend + PostgreSQL)
- **Plan Hobby**: $5 USD/mes por servicio adicional

### Google Play Store (Opcional)
- **Cuenta de desarrollador**: $25 USD (una sola vez)
- **Sin costos adicionales** por publicar apps

### Total
- **Solo Railway**: $5-15 USD/mes
- **Railway + Play Store**: $25 inicial + $10-15 USD/mes

---

## 🎯 Lo Que Necesitas Tener Listo

### Para Railway (Paso 1)

- ✅ Cuenta de GitHub (tu código debe estar en GitHub)
- ✅ Tarjeta de crédito/débito (para Railway, aunque es gratis hasta $5/mes)
- ✅ 30-60 minutos de tiempo

### Para Configurar URLs (Paso 2)

- ✅ URL de Railway del Paso 1
- ✅ 15 minutos de tiempo

### Para Generar APK (Paso 3)

- ✅ Android Studio instalado
- ✅ Java JDK 17+ instalado
- ✅ Password seguro para keystore (¡guárdalo bien!)
- ✅ 30 minutos de tiempo

---

## 🔄 Flujo de Trabajo Después de Configurar

Una vez que hagas los 3 pasos, tu flujo será:

### **Hacer Cambios en el Código**

```bash
# 1. Hacer tus cambios en el código

# 2. Commit y push a GitHub
git add .
git commit -m "Descripción de cambios"
git push

# 3. Railway redespliega automáticamente (2-5 min)

# 4. Si cambios solo en frontend/móvil
npm run build:mobile
npm run cap:sync:android

# 5. Si quieres nuevo APK
cd android
./gradlew assembleRelease
```

**¡Eso es todo!** Railway redespliega automáticamente cuando haces push.

---

## 🆘 ¿Necesitas Ayuda?

### Por Paso

**Paso 1 (Railway)**:
- 📖 Lee: [DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md)
- 🔍 Sección Troubleshooting en la guía
- 🌐 Docs Railway: https://docs.railway.app/

**Paso 2 (URLs)**:
- 📖 Lee: [CONFIGURAR_API_URL.md](CONFIGURAR_API_URL.md)
- 🔍 Sección Troubleshooting en la guía

**Paso 3 (APK)**:
- 📖 Lee: [GENERAR_APK.md](GENERAR_APK.md)
- 🔍 Sección Troubleshooting en la guía
- 🤖 Docs Android: https://developer.android.com/

### Errores Comunes

**"CORS error"**: Verifica `ALLOWED_ORIGINS` en Railway incluye tu dominio.

**"Network error" en app**: Verifica que `environment.prod.ts` tenga la URL correcta.

**"Keystore error"**: Verifica el password y alias sean correctos.

**"Build failed"**: Revisa los logs en Railway o Android Studio.

---

## ✅ Checklist Rápido

Marca cada paso cuando lo completes:

### Paso 1: Railway
- [ ] Cuenta Railway creada
- [ ] Repositorio conectado
- [ ] PostgreSQL agregado
- [ ] Variables de entorno configuradas
- [ ] Migraciones ejecutadas
- [ ] API respondiendo en `/api/health`

### Paso 2: URLs
- [ ] `environment.prod.ts` actualizado
- [ ] Build ejecutado: `npm run build:mobile`
- [ ] Sincronizado: `npm run cap:sync:android`
- [ ] Sin errores de CORS

### Paso 3: APK
- [ ] Keystore creado
- [ ] Credenciales guardadas en lugar seguro
- [ ] `build.gradle` configurado
- [ ] APK generado sin errores
- [ ] APK probado en dispositivo

---

## 🎉 ¡Estás Listo!

Todo está preparado. Solo sigue los 3 pasos en orden:

1. 🚀 **[DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md)** - Subir backend
2. 🔗 **[CONFIGURAR_API_URL.md](CONFIGURAR_API_URL.md)** - Conectar frontend
3. 📦 **[GENERAR_APK.md](GENERAR_APK.md)** - Crear APK

Cada guía tiene:
- ✅ Instrucciones paso a paso
- ✅ Comandos exactos para copiar
- ✅ Sección de Troubleshooting
- ✅ Capturas y ejemplos

---

**¿Por dónde empiezo?** → 🚀 **[DEPLOYMENT_RAILWAY.md](DEPLOYMENT_RAILWAY.md)**

**¡Éxito con el deployment! 🚀📱**

