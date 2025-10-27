# 📱 Guía de Capacitor para Android - vecindApp

Esta guía te ayudará a ejecutar la aplicación vecindApp en dispositivos Android.

## ✅ Pasos Completados

Ya se han realizado los siguientes pasos de configuración:

- ✅ Instalación de Capacitor Core, CLI y Android
- ✅ Inicialización de Capacitor con configuración base
- ✅ Creación de `capacitor.config.ts`
- ✅ Ajuste de presupuestos de build en `project.json`
- ✅ Plataforma Android agregada al proyecto
- ✅ Plugins de Capacitor instalados:
  - `@capacitor/app` - Gestión del ciclo de vida de la app
  - `@capacitor/splash-screen` - Pantalla de inicio
  - `@capacitor/status-bar` - Control de la barra de estado
  - `@capacitor/keyboard` - Control del teclado
  - `@capacitor/network` - Estado de la red
  - `@capacitor/camera` - Acceso a la cámara
  - `@capacitor/filesystem` - Sistema de archivos
- ✅ Scripts npm agregados para desarrollo móvil
- ✅ `.gitignore` actualizado con exclusiones de Android

## 🔧 Requisitos Previos

Antes de continuar, asegúrate de tener instalado:

### 1. **Java Development Kit (JDK)**
- **Versión requerida**: JDK 17 o superior
- **Descargar**: [Oracle JDK](https://www.oracle.com/java/technologies/downloads/) o [OpenJDK](https://adoptium.net/)
- **Verificar instalación**:
  ```powershell
  java -version
  ```

### 2. **Android Studio**
- **Descargar**: [Android Studio](https://developer.android.com/studio)
- **Componentes necesarios durante la instalación**:
  - Android SDK
  - Android SDK Platform
  - Android Virtual Device (AVD)
  - Android SDK Build-Tools
  - Android SDK Platform-Tools

### 3. **Variables de Entorno** (Configurar en Windows)

Agrega las siguientes variables de entorno:

```
ANDROID_HOME = C:\Users\TU_USUARIO\AppData\Local\Android\Sdk
JAVA_HOME = C:\Program Files\Java\jdk-17
```

Y agrega a la variable `Path`:
```
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
%ANDROID_HOME%\tools\bin
%JAVA_HOME%\bin
```

Para verificar:
```powershell
adb --version
```

## 🚀 Flujo de Trabajo

### **Desarrollo Diario**

Cuando hagas cambios en el código Angular:

1. **Construir la aplicación**:
   ```powershell
   npm run build:mobile
   ```

2. **Sincronizar con Android**:
   ```powershell
   npm run cap:sync:android
   ```

3. **Abrir en Android Studio**:
   ```powershell
   npm run cap:open:android
   ```

O ejecuta todo en un solo comando:
```powershell
npm run android:dev
```

### **Primera vez - Abrir el proyecto en Android Studio**

1. Ejecuta:
   ```powershell
   npm run cap:open:android
   ```

2. Android Studio se abrirá con el proyecto
3. Espera a que Gradle sincronice (primera vez puede tardar varios minutos)
4. Si aparece un mensaje de actualización de Gradle, puedes actualizarlo

### **Ejecutar la App**

#### **Opción 1: Desde Android Studio**

1. Selecciona un dispositivo o emulador en la barra superior
2. Haz clic en el botón ▶️ "Run" (o presiona `Shift + F10`)

#### **Opción 2: Crear un Emulador**

1. En Android Studio, ve a `Tools > Device Manager`
2. Haz clic en `Create Device`
3. Selecciona un dispositivo (ej: Pixel 6)
4. Selecciona una imagen del sistema (ej: Android 13 - API 33)
5. Descarga la imagen si es necesario
6. Haz clic en `Finish`

#### **Opción 3: Usar un Dispositivo Físico**

1. Habilita **Opciones de Desarrollador** en tu dispositivo Android:
   - Ve a `Ajustes > Acerca del teléfono`
   - Toca 7 veces en `Número de compilación`
2. Habilita **Depuración USB**:
   - Ve a `Ajustes > Opciones de Desarrollador`
   - Activa `Depuración USB`
3. Conecta el dispositivo con un cable USB
4. Acepta el mensaje de autorización en el dispositivo
5. Verifica la conexión:
   ```powershell
   adb devices
   ```

#### **Opción 4: Desde la Terminal**

```powershell
npm run cap:run:android
```

Esto construirá, sincronizará y ejecutará la app en el dispositivo/emulador conectado.

## 📝 Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `npm run build:mobile` | Construye la aplicación Angular para producción |
| `npm run cap:sync` | Sincroniza todos los cambios con todas las plataformas |
| `npm run cap:sync:android` | Sincroniza solo con Android |
| `npm run cap:open:android` | Abre el proyecto en Android Studio |
| `npm run cap:run:android` | Ejecuta la app en un dispositivo/emulador |
| `npm run cap:build:android` | Build completo + sync + open Android Studio |
| `npm run android:dev` | Desarrollo rápido: build + sync + open |

## 🔍 Verificar la Configuración

### **Verificar que todo está configurado correctamente:**

```powershell
npx cap doctor
```

Este comando verificará:
- Instalación de Capacitor
- Configuración de Android SDK
- Sincronización de la plataforma

## 🛠️ Troubleshooting

### **Problema: "ANDROID_HOME not set"**
**Solución**: Configura la variable de entorno `ANDROID_HOME` como se indica arriba.

### **Problema: "No Android SDKs found"**
**Solución**: 
1. Abre Android Studio
2. Ve a `File > Settings > Appearance & Behavior > System Settings > Android SDK`
3. Instala al menos una versión del SDK (recomendado: API 33 o superior)

### **Problema: "Gradle build failed"**
**Solución**:
1. Abre el proyecto en Android Studio
2. Ve a `File > Invalidate Caches > Invalidate and Restart`
3. O ejecuta desde la terminal dentro de `android/`:
   ```powershell
   cd android
   .\gradlew clean
   ```

### **Problema: "Device not found"**
**Solución**:
- Para emulador: Crea uno en Android Studio (`Tools > Device Manager`)
- Para dispositivo físico: Verifica que esté conectado con `adb devices`

### **Problema: La app no refleja los cambios**
**Solución**:
1. Reconstruye la app Angular: `npm run build:mobile`
2. Sincroniza: `npm run cap:sync:android`
3. Reinicia la app en el dispositivo

### **Problema: Error de permisos en la cámara**
**Solución**: Los permisos ya están configurados en `AndroidManifest.xml`. Si aún falla:
1. Ve a `Configuración` del dispositivo/emulador
2. `Apps > vecindApp > Permisos`
3. Activa los permisos necesarios

## 📱 Configuración Avanzada

### **Cambiar el Icono de la App**

1. Genera iconos usando [Icon Generator](https://www.appicon.co/)
2. Reemplaza los archivos en `android/app/src/main/res/mipmap-*/`
3. Sincroniza: `npm run cap:sync:android`

### **Cambiar el Splash Screen**

1. Coloca tu imagen en `android/app/src/main/res/drawable/splash.png`
2. Ajusta la configuración en `capacitor.config.ts`:
   ```typescript
   plugins: {
     SplashScreen: {
       launchShowDuration: 3000,
       backgroundColor: "#ffffffff",
       androidSplashResourceName: "splash",
       showSpinner: true
     }
   }
   ```

### **Configurar Deep Links**

En `capacitor.config.ts`:
```typescript
{
  appId: 'com.vecindapp',
  appName: 'vecindApp',
  webDir: 'dist/apps/vecindApp/frontend',
  server: {
    androidScheme: 'https',
    hostname: 'vecindapp.com'
  }
}
```

## 🔄 Actualizar Capacitor

Para actualizar Capacitor a la última versión:

```powershell
npm install @capacitor/core@latest @capacitor/cli@latest @capacitor/android@latest
npx cap sync android
```

## 📚 Recursos Adicionales

- [Documentación oficial de Capacitor](https://capacitorjs.com/docs)
- [Capacitor Android Documentation](https://capacitorjs.com/docs/android)
- [Capacitor Plugins](https://capacitorjs.com/docs/plugins)
- [Android Studio Documentation](https://developer.android.com/studio)

## 💡 Consejos

1. **Live Reload en dispositivo**: Puedes configurar live reload apuntando a tu servidor de desarrollo local
2. **Depuración**: Usa Chrome DevTools conectándote a `chrome://inspect` cuando la app esté corriendo
3. **Logs**: Revisa los logs de Android Studio (Logcat) para depurar errores nativos
4. **Build de Producción**: Para generar un APK firmado, necesitarás configurar un keystore

## 🎉 ¡Listo!

Ahora puedes ejecutar tu aplicación vecindApp en dispositivos Android. Si tienes problemas, revisa la sección de Troubleshooting o consulta la documentación oficial.

