import { Injectable } from '@angular/core';
import { App } from '@capacitor/app';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Network } from '@capacitor/network';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';
import { Keyboard } from '@capacitor/keyboard';

/**
 * Servicio de ejemplo para integración con Capacitor
 * Demuestra cómo usar los plugins de Capacitor en Angular
 */
@Injectable({
  providedIn: 'root'
})
export class CapacitorExampleService {

  constructor() {
    this.initializeApp();
  }

  /**
   * Inicialización de la app móvil
   */
  private async initializeApp() {
    // Escuchar cuando la app pasa a primer plano
    App.addListener('appStateChange', ({ isActive }) => {
      console.log('App state changed. Is active?', isActive);
    });

    // Escuchar cambios en el estado de la red
    Network.addListener('networkStatusChange', status => {
      console.log('Network status changed', status);
    });

    // Ocultar el splash screen después de que la app cargue
    await SplashScreen.hide();
  }

  /**
   * Configurar la barra de estado
   * @param style - Estilo de la barra (LIGHT o DARK)
   * @param color - Color de fondo en hexadecimal
   */
  async setStatusBar(style: Style = Style.Light, color: string = '#ffffff') {
    try {
      await StatusBar.setStyle({ style });
      await StatusBar.setBackgroundColor({ color });
    } catch (error) {
      console.error('Error setting status bar:', error);
    }
  }

  /**
   * Tomar una foto con la cámara
   * @returns URL de la imagen capturada
   */
  async takePicture(): Promise<string | null> {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Uri,
        source: CameraSource.Camera
      });

      return image.webPath || null;
    } catch (error) {
      console.error('Error taking picture:', error);
      return null;
    }
  }

  /**
   * Seleccionar una imagen de la galería
   * @returns URL de la imagen seleccionada
   */
  async selectFromGallery(): Promise<string | null> {
    try {
      const image = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Uri,
        source: CameraSource.Photos
      });

      return image.webPath || null;
    } catch (error) {
      console.error('Error selecting from gallery:', error);
      return null;
    }
  }

  /**
   * Verificar el estado de la conexión de red
   * @returns Estado de la conexión
   */
  async checkNetworkStatus() {
    try {
      const status = await Network.getStatus();
      return {
        connected: status.connected,
        connectionType: status.connectionType
      };
    } catch (error) {
      console.error('Error checking network status:', error);
      return null;
    }
  }

  /**
   * Obtener información de la app
   * @returns Información de la app (id, nombre, versión, build)
   */
  async getAppInfo() {
    try {
      const info = await App.getInfo();
      return {
        id: info.id,
        name: info.name,
        version: info.version,
        build: info.build
      };
    } catch (error) {
      console.error('Error getting app info:', error);
      return null;
    }
  }

  /**
   * Mostrar u ocultar el teclado
   */
  async showKeyboard() {
    try {
      await Keyboard.show();
    } catch (error) {
      console.error('Error showing keyboard:', error);
    }
  }

  async hideKeyboard() {
    try {
      await Keyboard.hide();
    } catch (error) {
      console.error('Error hiding keyboard:', error);
    }
  }

  /**
   * Cerrar la aplicación (solo Android)
   */
  async exitApp() {
    try {
      await App.exitApp();
    } catch (error) {
      console.error('Error exiting app:', error);
    }
  }

  /**
   * Minimizar la app (enviar a segundo plano)
   */
  async minimizeApp() {
    try {
      await App.minimizeApp();
    } catch (error) {
      console.error('Error minimizing app:', error);
    }
  }
}

