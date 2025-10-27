import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.vecindapp',
  appName: 'vecindApp',
  webDir: 'dist/apps/vecindApp/frontend',
  server: {
    androidScheme: 'https',
    cleartext: true,
    // Para desarrollo local con live reload, descomenta y ajusta la URL:
    // url: 'http://192.168.1.X:4200',
    // cleartext: true
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: "#ffffff",
      androidSplashResourceName: "splash",
      showSpinner: false,
      androidSpinnerStyle: "large",
      spinnerColor: "#999999"
    },
    StatusBar: {
      style: "LIGHT",
      backgroundColor: "#ffffff"
    },
    Keyboard: {
      resize: "body",
      style: "dark",
      resizeOnFullScreen: true
    }
  },
  android: {
    allowMixedContent: true,
    captureInput: true,
    webContentsDebuggingEnabled: true,
    buildOptions: {
      keystorePath: undefined,
      keystoreAlias: undefined
    }
  }
};

export default config;
