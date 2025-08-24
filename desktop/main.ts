import { app, BrowserWindow, ipcMain, shell } from 'electron';
import { join } from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Configuration de sécurité
app.on('web-contents-created', (event, contents) => {
  // Bloquer la navigation vers des sites externes
  contents.on('will-navigate', (event, navigationUrl) => {
    const parsedUrl = new URL(navigationUrl);
    if (parsedUrl.origin !== 'http://localhost:5173') {
      event.preventDefault();
    }
  });

  // Bloquer l'ouverture de nouvelles fenêtres
  contents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
});

// Créer la fenêtre principale
function createWindow(): void {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true,
      preload: join(__dirname, 'preload.js')
    },
    icon: join(__dirname, 'assets/icon.png'),
    titleBarStyle: 'default',
    show: false
  });

  // Charger l'application
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(join(__dirname, 'renderer/index.html'));
  }

  // Afficher la fenêtre quand elle est prête
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Gérer la fermeture de la fenêtre
  mainWindow.on('closed', () => {
    // Fermer l'application
    app.quit();
  });
}

// Gestionnaires IPC pour la communication avec le renderer
ipcMain.handle('get-running-processes', async () => {
  try {
    if (process.platform === 'win32') {
      const { stdout } = await execAsync('Get-Process | Select-Object ProcessName, Id, CPU | ConvertTo-Json', { shell: 'PowerShell' });
      return JSON.parse(stdout);
    } else {
      const { stdout } = await execAsync('ps -eo comm,pid,%cpu --no-headers | awk \'{print "{\\"ProcessName\\":\\"" $1 "\\",\\"Id\\":" $2 ",\\"CPU\\":" $3 "}"}\' | jq -s .');
      return JSON.parse(stdout);
    }
  } catch (error) {
    console.error('Erreur lors de la récupération des processus:', error);
    return [];
  }
});

ipcMain.handle('capture-screen', async () => {
  try {
    const mainWindow = BrowserWindow.getFocusedWindow();
    if (mainWindow) {
      const image = await mainWindow.webContents.capturePage();
      return image.toDataURL();
    }
    return null;
  } catch (error) {
    console.error('Erreur lors de la capture d\'écran:', error);
    return null;
  }
});

ipcMain.handle('log-security-alert', async (event, alertData) => {
  try {
    console.log('Alerte de sécurité:', alertData);
    // Ici, vous pouvez implémenter la journalisation locale
    return true;
  } catch (error) {
    console.error('Erreur lors de la journalisation:', error);
    return false;
  }
});

// Gestionnaires d'événements de l'application
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Gestion des erreurs non capturées
process.on('uncaughtException', (error) => {
  console.error('Erreur non capturée:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Promesse rejetée non gérée:', reason);
});
