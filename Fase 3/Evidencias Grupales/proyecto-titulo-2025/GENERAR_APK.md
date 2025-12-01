# 📦 Generar APK para Android

Esta guía te muestra cómo empaquetar tu aplicación **vecindApp** en un archivo APK para distribuir en dispositivos Android.

---

## 📋 Tabla de Contenidos

1. [Tipos de APK](#tipos-de-apk)
2. [Preparar la App](#preparar-la-app)
3. [Generar APK Debug (Testing)](#generar-apk-debug-testing)
4. [Generar APK Release (Producción)](#generar-apk-release-producción)
5. [Crear Keystore](#crear-keystore)
6. [Firmar APK](#firmar-apk)
7. [Instalar APK en Dispositivo](#instalar-apk-en-dispositivo)
8. [Subir a Google Play Store](#subir-a-google-play-store)
9. [Troubleshooting](#troubleshooting)

---

## 📱 Tipos de APK

### **Debug APK**
- ✅ Para pruebas y desarrollo
- ✅ No requiere firma
- ✅ Fácil de generar
- ❌ No se puede publicar en Play Store
- ❌ Menos optimizado

### **Release APK**
- ✅ Para producción
- ✅ Optimizado y más pequeño
- ✅ Listo para Play Store
- ❌ Requiere firma con keystore
- ❌ Más pasos de configuración

---

## 🔧 Preparar la App

### **1. Actualizar Configuración de Producción**

Asegúrate de que `environment.prod.ts` tenga la URL correcta del backend:

**`apps/vecindApp/frontend/src/environments/environment.prod.ts`:**
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://tu-backend.up.railway.app/api'
};
```

### **2. Actualizar Capacitor Config**

**`capacitor.config.ts`:**
```typescript
const config: CapacitorConfig = {
  appId: 'com.vecindapp',
  appName: 'vecindApp',
  webDir: 'dist/apps/vecindApp/frontend',
  server: {
    androidScheme: 'https',
    cleartext: false  // Importante: false para producción
  },
  // ... resto de configuración
};
```

### **3. Actualizar Información de la App**

**`android/app/build.gradle`:**

Busca y actualiza:
```gradle
android {
    defaultConfig {
        applicationId "com.vecindapp"
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 1        // Incrementa con cada release
        versionName "1.0.0"  // Versión visible para usuarios
    }
}
```

### **4. Construir la Aplicación Angular**

```bash
# Desde la raíz del proyecto (proyecto-titulo-2025)
npm run build:mobile
```

Este comando ejecuta:
```bash
npx nx build frontend --configuration=production
```

### **5. Sincronizar con Capacitor**

```bash
npm run cap:sync:android
```

---

## 🧪 Generar APK Debug (Testing)

APK sin firmar para pruebas rápidas.

### **Método 1: Desde Android Studio (Recomendado)**

1. **Abrir el proyecto**:
   ```bash
   npm run cap:open:android
   ```

2. **En Android Studio**:
   - Ve a `Build > Build Bundle(s) / APK(s) > Build APK(s)`
   - Espera a que termine el build (puede tardar 5-10 minutos)

3. **Ubicación del APK**:
   ```
   android/app/build/outputs/apk/debug/app-debug.apk
   ```

### **Método 2: Desde Terminal**

```bash
# Ir a la carpeta android
cd android

# Windows
.\gradlew assembleDebug

# Linux/Mac
./gradlew assembleDebug
```

**APK generado en**:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

### **Instalar el APK Debug**

```bash
# Con dispositivo conectado
adb install android/app/build/outputs/apk/debug/app-debug.apk

# O arrastra el archivo al emulador
```

---

## 🚀 Generar APK Release (Producción)

APK optimizado y firmado para distribución.

### **Prerequisitos**

Antes de generar el APK Release, necesitas:
1. ✅ Crear un Keystore (archivo de firma)
2. ✅ Configurar las credenciales de firma

---

## 🔐 Crear Keystore

El keystore es tu "firma digital" para la app. **¡Guárdalo en un lugar seguro!**

### **Generar Keystore**

```bash
# Windows PowerShell o CMD
cd android/app
keytool -genkey -v -keystore vecindapp-release-key.keystore -alias vecindapp -keyalg RSA -keysize 2048 -validity 10000

# Linux/Mac
cd android/app
keytool -genkey -v -keystore vecindapp-release-key.keystore -alias vecindapp -keyalg RSA -keysize 2048 -validity 10000
```

**Responde las preguntas**:
```
Enter keystore password: [TU_PASSWORD_SEGURA]
Re-enter new password: [TU_PASSWORD_SEGURA]
What is your first and last name? [Tu Nombre o Empresa]
What is the name of your organizational unit? [Tu Equipo]
What is the name of your organization? [Tu Organización]
What is the name of your City or Locality? [Tu Ciudad]
What is the name of your State or Province? [Tu Región]
What is the two-letter country code for this unit? [CL para Chile]
Is CN=..., correct? [yes]

Enter key password for <vecindapp>: [Presiona Enter para usar el mismo password]
```

### **⚠️ IMPORTANTE: Guardar Credenciales**

Crea un archivo **`keystore-info.txt`** (NO lo subas a Git):
```
Keystore: vecindapp-release-key.keystore
Alias: vecindapp
Store Password: TU_PASSWORD_AQUI
Key Password: TU_PASSWORD_AQUI
```

**🚨 NO PIERDAS ESTAS CREDENCIALES**: Sin ellas, no podrás actualizar la app en el futuro.

---

## 🔏 Configurar Firma en Gradle

### **Opción A: Archivo de Propiedades (Más Seguro)**

1. **Crear `key.properties`** en `android/`:

```properties
storeFile=app/vecindapp-release-key.keystore
storePassword=TU_PASSWORD
keyAlias=vecindapp
keyPassword=TU_PASSWORD
```

2. **Actualizar `android/app/build.gradle`**:

Agrega antes de `android {`:
```gradle
def keystorePropertiesFile = rootProject.file("key.properties")
def keystoreProperties = new Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```

Dentro de `android {`, después de `defaultConfig {`:
```gradle
signingConfigs {
    release {
        if (keystorePropertiesFile.exists()) {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
        minifyEnabled false
        proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
    }
}
```

3. **Agregar al `.gitignore`**:
```bash
# En .gitignore
android/key.properties
android/app/*.keystore
```

### **Opción B: Directo en build.gradle (Menos Seguro)**

En `android/app/build.gradle`, dentro de `android {`:

```gradle
signingConfigs {
    release {
        storeFile file('vecindapp-release-key.keystore')
        storePassword 'TU_PASSWORD'
        keyAlias 'vecindapp'
        keyPassword 'TU_PASSWORD'
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
        minifyEnabled false
        proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
    }
}
```

---

## 📦 Generar APK Release Firmado

### **Método 1: Android Studio**

1. Abre el proyecto en Android Studio:
   ```bash
   npm run cap:open:android
   ```

2. Ve a `Build > Generate Signed Bundle / APK`

3. Selecciona `APK` y haz clic en `Next`

4. Completa la información del keystore:
   - **Key store path**: Selecciona `android/app/vecindapp-release-key.keystore`
   - **Key store password**: Tu password
   - **Key alias**: `vecindapp`
   - **Key password**: Tu password

5. Haz clic en `Next` y luego `Finish`

6. **APK generado en**:
   ```
   android/app/release/app-release.apk
   ```

### **Método 2: Terminal/Gradle**

```bash
cd android

# Windows
.\gradlew assembleRelease

# Linux/Mac
./gradlew assembleRelease
```

**APK firmado en**:
```
android/app/build/outputs/apk/release/app-release.apk
```

---

## 📲 Instalar APK en Dispositivo

### **Desde ADB (Dispositivo conectado)**

```bash
# Desinstalar versión anterior (opcional)
adb uninstall com.vecindapp

# Instalar nueva versión
adb install android/app/build/outputs/apk/release/app-release.apk

# O si ya existe
adb install -r android/app/build/outputs/apk/release/app-release.apk
```

### **Transferencia Manual**

1. Copia el APK a tu dispositivo (email, USB, Drive, etc.)
2. En el dispositivo:
   - Abre el archivo APK
   - Permite "Instalar desde fuentes desconocidas" si es necesario
   - Instala

---

## 🏪 Subir a Google Play Store

### **1. Preparar Assets**

Necesitarás:
- ✅ Icono de la app (512x512 px)
- ✅ Feature Graphic (1024x500 px)
- ✅ Screenshots (al menos 2)
- ✅ Descripción de la app
- ✅ Política de privacidad (URL)

### **2. Crear Cuenta de Desarrollador**

1. Ve a https://play.google.com/console
2. Paga la tarifa única de $25 USD
3. Completa tu perfil

### **3. Crear Nueva App**

1. En Play Console, haz clic en "Create app"
2. Completa la información básica
3. Acepta las declaraciones

### **4. Configurar Store Listing**

1. Sube icono, screenshots y gráficos
2. Escribe descripción corta y completa
3. Categoriza la app

### **5. Configurar Content Rating**

1. Completa el cuestionario de contenido
2. Obtén la calificación

### **6. Pricing & Distribution**

1. Selecciona países donde estará disponible
2. Define si es gratis o de pago

### **7. Subir APK**

1. Ve a "Release > Production"
2. Haz clic en "Create new release"
3. Sube el APK o AAB (Bundle)
4. Completa las notas de la versión
5. Guarda y envía para revisión

### **8. Revisión**

- Google revisará tu app (1-7 días)
- Recibirás un email cuando esté aprobada o si hay problemas

---

## 📦 Generar AAB (Android App Bundle) - Recomendado

Google Play Store recomienda AAB en lugar de APK.

### **Ventajas del AAB**:
- ✅ Tamaño más pequeño para usuarios
- ✅ Optimización automática por dispositivo
- ✅ Requerido para apps nuevas en Play Store

### **Generar AAB**:

```bash
cd android

# Windows
.\gradlew bundleRelease

# Linux/Mac
./gradlew bundleRelease
```

**AAB generado en**:
```
android/app/build/outputs/bundle/release/app-release.aab
```

---

## 🧪 Optimizaciones Antes del Release

### **1. Proguard (Ofuscación)**

En `android/app/build.gradle`:
```gradle
buildTypes {
    release {
        minifyEnabled true  // Cambiar a true
        shrinkResources true
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
}
```

### **2. Actualizar Versiones**

En `android/app/build.gradle`:
```gradle
defaultConfig {
    versionCode 2       // Incrementar en cada release
    versionName "1.1.0" // Incrementar versión visible
}
```

### **3. Comprimir Imágenes**

Optimiza las imágenes en `public/images/` usando herramientas como:
- TinyPNG
- ImageOptim
- Squoosh

---

## 🐛 Troubleshooting

### **Error: "Keystore was tampered with"**

**Causa**: Password incorrecto

**Solución**: Verifica el password en `key.properties`

### **Error: "Failed to read key from keystore"**

**Causa**: Alias incorrecto o keystore corrupto

**Solución**:
```bash
# Listar aliases del keystore
keytool -list -v -keystore vecindapp-release-key.keystore
```

### **Error: "Build failed" al generar release**

**Causa**: Configuración de firma incorrecta

**Solución**:
1. Verifica que `key.properties` exista
2. Verifica las rutas en `build.gradle`
3. Revisa los logs en Android Studio

### **APK muy grande**

**Solución**:
1. Habilita `minifyEnabled true`
2. Usa AAB en lugar de APK
3. Optimiza imágenes
4. Revisa dependencias innecesarias

### **App crashea al abrir**

**Solución**:
1. Conecta el dispositivo
2. Abre `chrome://inspect`
3. Revisa los logs
4. Verifica que `environment.prod.ts` tenga la URL correcta

---

## 📋 Checklist de Release

- [ ] Backend desplegado en Railway
- [ ] `environment.prod.ts` con URL correcta
- [ ] `capacitor.config.ts` con `cleartext: false`
- [ ] Build de producción exitoso: `npm run build:mobile`
- [ ] Sincronizado: `npm run cap:sync:android`
- [ ] Keystore creado y guardado en lugar seguro
- [ ] Credenciales guardadas (password, alias)
- [ ] `key.properties` configurado
- [ ] `build.gradle` configurado con signingConfig
- [ ] `versionCode` y `versionName` actualizados
- [ ] APK/AAB generado sin errores
- [ ] APK probado en dispositivo físico
- [ ] Funcionalidades críticas probadas
- [ ] Sin errores de conexión al backend
- [ ] Iconos y assets optimizados

---

## 📚 Recursos Adicionales

- **Android Developers**: https://developer.android.com/studio/publish
- **Google Play Console**: https://play.google.com/console
- **Capacitor Deployment**: https://capacitorjs.com/docs/android/deploying-to-google-play
- **Keystore Guide**: https://developer.android.com/studio/publish/app-signing

---

## 🔄 Actualizar la App (Releases Futuros)

Para publicar una actualización:

1. **Hacer cambios en el código**

2. **Incrementar versión** en `android/app/build.gradle`:
   ```gradle
   versionCode 2      // +1 del anterior
   versionName "1.1.0"
   ```

3. **Construir y sincronizar**:
   ```bash
   npm run build:mobile
   npm run cap:sync:android
   ```

4. **Generar nuevo APK/AAB** con el mismo keystore

5. **Subir a Play Store** como nueva versión

⚠️ **IMPORTANTE**: Debes usar el mismo keystore para todas las actualizaciones.

---

¡Listo! Tu app está empaquetada y lista para distribuir. 🎉

