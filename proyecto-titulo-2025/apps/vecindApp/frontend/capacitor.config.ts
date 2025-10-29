import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'cl.duocuc.vecindapp',
  appName: 'VecindApp',
  webDir: '../../../dist/apps/vecindApp/frontend',
  server: {
    androidScheme: 'https',
    cleartext: true
  },
  android: {
    allowMixedContent: true
  }
};

export default config;

