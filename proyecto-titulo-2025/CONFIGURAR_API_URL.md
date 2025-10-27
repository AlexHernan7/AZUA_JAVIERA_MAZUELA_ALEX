# 🔗 Configurar API URL para Producción

Después de desplegar el backend en Railway, necesitas actualizar las URLs en el frontend y la app móvil.

---

## 📝 Pasos a Seguir

### **1. Obtener la URL de Railway**

1. Ve a tu proyecto en Railway
2. Selecciona el servicio del backend
3. Ve a "Settings" > "Networking"
4. Copia la URL generada (ejemplo: `https://vecindapp-backend.up.railway.app`)

---

### **2. Actualizar Environment de Producción**

Edita el archivo **`apps/vecindApp/frontend/src/environments/environment.prod.ts`**:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://TU-URL-RAILWAY.up.railway.app/api'
};
```

**Ejemplo real**:
```typescript
export const environment = {
  production: true,
  apiUrl: 'https://vecindapp-backend.up.railway.app/api'
};
```

⚠️ **IMPORTANTE**: No olvides agregar `/api` al final de la URL.

---

### **3. Actualizar Servicios Angular (Opcional pero Recomendado)**

Los servicios actualmente tienen URLs hardcodeadas. Debes actualizarlos para usar `environment.apiUrl`.

#### **Ejemplo de cómo actualizar un servicio:**

**Antes (hardcoded):**
```typescript
export class AuthService {
  private readonly API_URL = 'http://localhost:8000/api';
  // ...
}
```

**Después (usando environment):**
```typescript
import { environment } from '../../environments/environment';

export class AuthService {
  private readonly API_URL = environment.apiUrl;
  // ...
}
```

#### **Servicios a actualizar:**

Actualiza estos archivos siguiendo el ejemplo anterior:

1. ✅ `src/app/services/auth.service.ts`
2. ✅ `src/app/services/news.service.ts`
3. ✅ `src/app/services/junta.service.ts`
4. ✅ `src/app/services/espacio.service.ts`
5. ✅ `src/app/services/directiva.service.ts`
6. ✅ `src/app/services/certificado.service.ts`
7. ✅ `src/app/services/reserva.service.ts`
8. ✅ `src/app/services/payment.service.ts`
9. ✅ `src/app/services/master.service.ts`
10. ✅ `src/app/services/reporte.service.ts`
11. ✅ `src/app/services/admin.service.ts`

---

### **4. Actualizar proxy.conf.json**

Si usas el proxy para desarrollo local, actualiza **`apps/vecindApp/frontend/proxy.conf.json`**:

```json
{
  "/api": {
    "target": "https://TU-URL-RAILWAY.up.railway.app",
    "secure": true,
    "changeOrigin": true,
    "logLevel": "debug"
  }
}
```

---

### **5. Actualizar Capacitor Config**

Edita **`capacitor.config.ts`** en la raíz del proyecto:

```typescript
import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.vecindapp',
  appName: 'vecindApp',
  webDir: 'dist/apps/vecindApp/frontend',
  server: {
    androidScheme: 'https',
    cleartext: false,  // false para HTTPS en producción
    // Para desarrollo con servidor local:
    // url: 'http://192.168.1.X:4200',
    // cleartext: true
  },
  // ... resto de configuración
};

export default config;
```

**NOTA**: La app móvil usará `environment.prod.ts` automáticamente cuando construyas con `--configuration=production`.

---

### **6. Actualizar CORS en Railway**

En Railway, agrega la URL de tu frontend a las variables de entorno:

```bash
ALLOWED_ORIGINS=https://tu-frontend.com,capacitor://localhost,ionic://localhost,http://localhost:4200
```

Si tu frontend está en un dominio específico, agrégalo a la lista.

---

### **7. Construir la Aplicación**

#### **Para Web (Frontend):**

```bash
# Desarrollo
npx nx serve frontend

# Producción (usa environment.prod.ts automáticamente)
npx nx build frontend --configuration=production
```

#### **Para Móvil (Android):**

```bash
# Construir con configuración de producción
npm run build:mobile

# Sincronizar con Capacitor
npm run cap:sync:android

# Abrir en Android Studio
npm run cap:open:android
```

---

### **8. Verificar la Conexión**

#### **Desde el Frontend Web:**

1. Abre las DevTools del navegador (F12)
2. Ve a la pestaña "Network"
3. Realiza una acción que haga una petición a la API
4. Verifica que la URL sea `https://TU-URL-RAILWAY.up.railway.app/api/...`

#### **Desde la App Móvil:**

1. Conecta tu dispositivo/emulador
2. Abre Chrome y ve a `chrome://inspect`
3. Selecciona tu dispositivo
4. Ve a "Network" y verifica las peticiones

---

## 🔍 Script de Actualización Masiva (Opcional)

Si quieres automatizar la actualización de todos los servicios, puedes usar este script:

**`update-api-urls.js`** (crear en la raíz):

```javascript
const fs = require('fs');
const path = require('path');

const servicesDir = 'apps/vecindApp/frontend/src/app/services';
const files = fs.readdirSync(servicesDir).filter(f => f.endsWith('.service.ts'));

files.forEach(file => {
  const filePath = path.join(servicesDir, file);
  let content = fs.readFileSync(filePath, 'utf8');
  
  // Verificar si ya usa environment
  if (content.includes('environment.apiUrl')) {
    console.log(`✅ ${file} ya está actualizado`);
    return;
  }
  
  // Buscar import statements
  const hasImports = content.match(/^import .* from/m);
  
  if (hasImports && !content.includes("from '../../environments/environment'")) {
    // Agregar import después de otros imports
    const importIndex = content.lastIndexOf('\nimport');
    const nextLineIndex = content.indexOf('\n', importIndex + 1);
    
    content = content.slice(0, nextLineIndex + 1) +
              "import { environment } from '../../environments/environment';\n" +
              content.slice(nextLineIndex + 1);
  }
  
  // Reemplazar URL hardcodeada
  content = content.replace(
    /private readonly API_URL = 'http:\/\/localhost:8000\/api';/g,
    "private readonly API_URL = environment.apiUrl;"
  );
  
  fs.writeFileSync(filePath, content);
  console.log(`✅ Actualizado: ${file}`);
});

console.log('\n✅ Todos los servicios actualizados!');
```

**Ejecutar:**
```bash
node update-api-urls.js
```

---

## 🧪 Testing en Diferentes Entornos

### **Desarrollo Local:**
```bash
# Backend en localhost:8000
# Frontend en localhost:4200
npx nx serve frontend
```

### **Desarrollo con Backend en Railway:**
```bash
# Backend en Railway
# Frontend local apuntando a Railway
# Actualiza environment.ts temporalmente o usa environment.prod.ts
npx nx serve frontend --configuration=production
```

### **Producción:**
```bash
# Backend y Frontend en sus respectivos servidores
npx nx build frontend --configuration=production
```

---

## 📱 Configuraciones para App Móvil

### **Desarrollo (Live Reload con backend local):**

En `capacitor.config.ts`:
```typescript
server: {
  url: 'http://TU_IP_LOCAL:4200',
  cleartext: true
}
```

### **Desarrollo (con backend en Railway):**

En `capacitor.config.ts`:
```typescript
server: {
  androidScheme: 'https',
  cleartext: false
}
```

Y construye con:
```bash
npm run build:mobile  # Usa environment.prod.ts
```

### **Producción (APK final):**

Igual que desarrollo con Railway, pero además:
1. Asegúrate de que `environment.prod.ts` tenga la URL correcta
2. Construye con `--configuration=production`
3. Firma el APK (ver `GENERAR_APK.md`)

---

## ✅ Checklist

- [ ] URL de Railway obtenida
- [ ] `environment.prod.ts` actualizado con URL de Railway
- [ ] Servicios Angular actualizados para usar `environment.apiUrl`
- [ ] `capacitor.config.ts` configurado para HTTPS
- [ ] Variable `ALLOWED_ORIGINS` actualizada en Railway
- [ ] Build de producción exitoso
- [ ] Conexión verificada desde frontend web
- [ ] Conexión verificada desde app móvil
- [ ] Sin errores de CORS en consola

---

## 🆘 Troubleshooting

### **Error: "Failed to fetch" en la app móvil**

**Causa**: CORS o cleartext traffic bloqueado

**Solución**:
1. Verifica `ALLOWED_ORIGINS` en Railway incluye `capacitor://localhost`
2. En `capacitor.config.ts`, verifica `cleartext: false` para HTTPS
3. Reconstruye y sincroniza: `npm run build:mobile && npm run cap:sync:android`

### **Error: "Network Error" en desarrollo local**

**Causa**: Backend no está corriendo o URL incorrecta

**Solución**:
1. Verifica que el backend esté corriendo (local o Railway)
2. Verifica la URL en `environment.ts`
3. Verifica CORS en el backend

### **Funciona en web pero no en móvil**

**Causa**: Configuración de Capacitor o build incorrecto

**Solución**:
1. Reconstruye con producción: `npm run build:mobile`
2. Sincroniza: `npm run cap:sync:android`
3. Verifica en `chrome://inspect` las peticiones

---

¡Listo! Tu aplicación ahora está configurada para usar el backend en Railway. 🚀

