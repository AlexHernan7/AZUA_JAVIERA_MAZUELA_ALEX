# Instrucciones para el Proyecto Angular - VecindApp

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Node.js** (versión 18 o superior)
- **npm** (viene incluido con Node.js)
- **Angular CLI** (se instalará automáticamente con las dependencias del proyecto)

## 🚀 Levantar el Servidor de Desarrollo

### 1. Navegar al directorio del proyecto
```bash
cd "Fase 2/front-end/vecindApp"
```

### 2. Instalar dependencias (solo la primera vez)
```bash
npm install
```

### 3. Levantar el servidor de desarrollo
```bash
npm start
```

O alternativamente:
```bash
ng serve
```

### 4. Acceder a la aplicación
Una vez que el servidor esté corriendo, abre tu navegador y ve a:
```
http://localhost:4200
```

El servidor se recargará automáticamente cuando detecte cambios en los archivos.

## 🛠️ Comandos Disponibles

### Servidor de desarrollo
```bash
npm start          # Levanta el servidor en modo desarrollo
ng serve           # Comando directo de Angular CLI
```

### Construcción del proyecto
```bash
npm run build      # Construye el proyecto para producción
ng build           # Comando directo de Angular CLI
```

### Modo watch (desarrollo con recarga automática)
```bash
npm run watch      # Construye y observa cambios
```

### Pruebas
```bash
npm test           # Ejecuta las pruebas unitarias
ng test            # Comando directo de Angular CLI
```

### Servidor SSR (Server-Side Rendering)
```bash
npm run serve:ssr:vecindApp    # Levanta el servidor con SSR
```

## 🧩 Crear un Nuevo Componente

### 1. Usando Angular CLI (Recomendado)
```bash
ng generate component nombre-del-componente
```

O la versión corta:
```bash
ng g c nombre-del-componente
```

### 2. Crear componente en una carpeta específica
```bash
ng g c carpeta/nombre-del-componente
```

### 3. Crear componente con opciones adicionales
```bash
ng g c nombre-del-componente --skip-tests    # Sin archivos de prueba
ng g c nombre-del-componente --inline-style  # Estilos inline
ng g c nombre-del-componente --inline-template # Template inline
```

### 4. Estructura de archivos generada
Cuando creas un componente, Angular CLI genera automáticamente:

```
src/app/nombre-del-componente/
├── nombre-del-componente.component.ts      # Lógica del componente
├── nombre-del-componente.component.html    # Template HTML
├── nombre-del-componente.component.css     # Estilos CSS
└── nombre-del-componente.component.spec.ts # Pruebas unitarias
```

## 📁 Estructura del Proyecto

```
vecindApp/
├── src/
│   ├── app/                    # Código fuente de la aplicación
│   │   ├── app.component.*     # Componente principal
│   │   └── ...                 # Otros componentes
│   ├── assets/                 # Recursos estáticos
│   ├── environments/           # Configuraciones de entorno
│   ├── index.html             # Página principal
│   ├── main.ts                # Punto de entrada de la aplicación
│   └── styles.css             # Estilos globales
├── public/                    # Archivos públicos
├── angular.json               # Configuración de Angular CLI
├── package.json              # Dependencias y scripts
└── tsconfig.json             # Configuración de TypeScript
```

## 🎨 Tecnologías Utilizadas

- **Angular 19.2.0** - Framework principal
- **TypeScript 5.7.2** - Lenguaje de programación
- **Tailwind CSS 4.1.13** - Framework de CSS
- **Angular SSR** - Server-Side Rendering
- **RxJS 7.8.0** - Programación reactiva

## 🔧 Configuración Adicional

### Personalizar el puerto del servidor
```bash
ng serve --port 4300
```

### Abrir automáticamente el navegador
```bash
ng serve --open
```

### Servir en una IP específica
```bash
ng serve --host 0.0.0.0
```

## 🐛 Solución de Problemas Comunes

### Error: "ng no se reconoce como comando"
```bash
npm install -g @angular/cli
```

### Error de dependencias
```bash
rm -rf node_modules package-lock.json
npm install
```

### Puerto ya en uso
```bash
ng serve --port 4201
```

## 📚 Recursos Adicionales

- [Documentación oficial de Angular](https://angular.io/docs)
- [Angular CLI Reference](https://angular.io/cli)
- [Guía de TypeScript](https://www.typescriptlang.org/docs/)

## 🚨 Notas Importantes

1. **Siempre ejecuta `npm install`** después de clonar el repositorio
2. **El servidor se ejecuta en el puerto 4200** por defecto
3. **Los cambios se reflejan automáticamente** en el navegador
4. **Usa Angular CLI** para generar componentes, servicios, etc.
5. **El proyecto incluye SSR** (Server-Side Rendering) configurado

---

¡Listo para desarrollar! 🎉
