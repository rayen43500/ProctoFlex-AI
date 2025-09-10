// Imports Node.js pour le main process uniquement
const electron = require('electron');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const fs = require('fs');

// Destructuration des modules Electron
const { app, BrowserWindow, ipcMain, shell } = electron;
const { join } = path;
const { existsSync } = fs;

// S'assurer que __dirname est disponible
if (typeof __dirname === 'undefined') {
  global.__dirname = path.dirname(require.main?.filename || process.execPath);
}

// __dirname est automatiquement disponible en CommonJS

const execAsync = promisify(exec);

// Fonction pour vérifier si le serveur Vite est prêt
async function checkViteServer(): Promise<boolean> {
  try {
    console.log('Vérification du serveur Vite...');
    const response = await fetch('http://localhost:5173');
    console.log('Réponse du serveur Vite:', response.status, response.statusText);
    return response.ok;
  } catch (error) {
    console.log('Erreur lors de la vérification du serveur Vite:', error);
    return false;
  }
}

// Configuration de sécurité
app.on('web-contents-created', (event: any, contents: any) => {
  // Bloquer la navigation vers des sites externes
  contents.on('will-navigate', (event: any, navigationUrl: string) => {
    const parsedUrl = new URL(navigationUrl);
    if (parsedUrl.origin !== 'http://localhost:5173') {
      event.preventDefault();
    }
  });

  // Bloquer l'ouverture de nouvelles fenêtres
  contents.setWindowOpenHandler(({ url }: { url: string }) => {
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
      experimentalFeatures: false,
      enableRemoteModule: false,
      sandbox: false
    },
    icon: join(__dirname, 'assets/icon.png'),
    titleBarStyle: 'default',
    show: false
  });

  // Charger l'application
  // Forcer le mode développement pour utiliser Vite
  console.log('NODE_ENV:', process.env.NODE_ENV);
  console.log('ELECTRON_IS_DEV:', process.env.ELECTRON_IS_DEV);
  
  // Toujours utiliser le mode développement pour le moment
  const isDevelopment = true; // process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;
  
  if (isDevelopment) {
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
    // Démarrer la surveillance des processus
    startProcessMonitor(mainWindow);
  });

  // Gérer la fermeture de la fenêtre
  mainWindow.on('closed', () => {
    // Fermer l'application
    stopProcessMonitor();
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

ipcMain.handle('log-security-alert', async (event: any, alertData: any) => {
  try {
    console.log('Alerte de sécurité:', alertData);
    // Ici, vous pouvez implémenter la journalisation locale
    return true;
  } catch (error) {
    console.error('Erreur lors de la journalisation:', error);
    return false;
  }
});

// --- Process Monitor (polling) ---
let monitorInterval: NodeJS.Timeout | null = null;

async function fetchLockConfig() {
  try {
    const res = await fetch('http://localhost:8000/api/v1/config/lock');
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    console.error('Erreur fetch lock config:', e);
    return null;
  }
}

async function listProcessesLower(): Promise<string> {
  try {
    if (process.platform === 'win32') {
      const { stdout } = await execAsync('tasklist | findstr /V /B "Image Name"');
      return stdout.toLowerCase();
    }
    const { stdout } = await execAsync('ps -A -o comm');
    return stdout.toLowerCase();
  } catch (e) {
    return '';
  }
}

async function sendAlert(alert: any) {
  try {
    await fetch('http://localhost:8000/api/v1/alerts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...alert, timestamp: new Date().toISOString() })
    });
  } catch (e) {
    console.error('Erreur envoi alerte:', e);
  }
}

async function killProcessWindows(procNameLower: string) {
  try {
    await execAsync(`taskkill /IM ${procNameLower} /F`);
  } catch {}
}

async function tickProcessMonitor(mainWindow: Electron.BrowserWindow | null) {
  const cfg = await fetchLockConfig();
  if (!cfg) return;
  const allowed: string[] = (cfg.allowed_apps || []).map((s: string) => s.toLowerCase());
  const forbidden: string[] = (cfg.forbidden_apps || []).map((s: string) => s.toLowerCase());
  const autoKill: boolean = !!(cfg.policy && cfg.policy.auto_kill);

  const procs = await listProcessesLower();
  if (!procs) return;

  for (const forb of forbidden) {
    if (forb && procs.includes(forb)) {
      await sendAlert({ type: 'forbidden_app', process: forb });
      if (mainWindow) {
        mainWindow.webContents.send('student-warning', { message: `⚠️ L'application "${forb}" est interdite pendant l'examen.` });
      }
      if (autoKill && process.platform === 'win32') {
        await killProcessWindows(forb);
      }
    }
  }
}

function startProcessMonitor(mainWindow: Electron.BrowserWindow) {
  if (monitorInterval) return;
  monitorInterval = setInterval(() => {
    tickProcessMonitor(mainWindow);
  }, 4000); // toutes les 4s
}

function stopProcessMonitor() {
  if (monitorInterval) {
    clearInterval(monitorInterval);
    monitorInterval = null;
  }
}

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
