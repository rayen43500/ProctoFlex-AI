const { app, BrowserWindow, ipcMain, shell } = require('electron');
const { join } = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const { existsSync } = require('fs');

const execAsync = promisify(exec);

// Fonction pour vérifier si le serveur Vite est prêt
async function checkViteServer(): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:5173');
    return response.ok;
  } catch {
    return false;
  }
}

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
async function createWindow(): Promise<void> {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true,
      preload: join(__dirname, 'preload.js'),
      allowRunningInsecureContent: false,
      experimentalFeatures: false
    },
    icon: join(__dirname, 'assets/icon.png'),
    titleBarStyle: 'default',
    show: false
  });

  // Charger l'application
  if (process.env.NODE_ENV === 'development') {
    console.log('Mode développement détecté');
    
    // Attendre que le serveur Vite soit prêt
    const loadDevServer = async () => {
      try {
        // Vérifier si le serveur Vite est prêt
        const isViteReady = await checkViteServer();
        if (!isViteReady) {
          console.log('Serveur Vite pas encore prêt, nouvelle tentative dans 2 secondes...');
          setTimeout(loadDevServer, 2000);
          return;
        }
        
        console.log('Serveur Vite prêt, chargement de l\'URL...');
        await mainWindow.loadURL('http://localhost:5173');
        console.log('URL chargée avec succès');
        mainWindow.webContents.openDevTools();
        console.log('Outils de développement ouverts');
      } catch (error) {
        console.log('Erreur lors du chargement:', (error as Error).message);
        console.log('Nouvelle tentative dans 3 secondes...');
        setTimeout(loadDevServer, 3000);
      }
    };
    
    // Commencer à vérifier après 2 secondes
    setTimeout(loadDevServer, 2000);
  } else {
    console.log('Mode production détecté');
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
