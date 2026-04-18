const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

let mainWindow = null;
let activationWindow = null;
let backendProcess = null;

// Backend configuration
const BACKEND_PORT = 18090;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

/**
 * Get the path to the Python backend
 */
function getBackendPath() {
    if (app.isPackaged) {
        // Production: PyInstaller bundled executable (.exe on Windows)
        return path.join(process.resourcesPath, 'backend', 'kkrpa-server.exe');
    }
    // Development: run with Python directly
    return null; // Will use python command
}

/**
 * Start the Python backend server
 */
function startBackend() {
    return new Promise((resolve, reject) => {
        const backendPath = getBackendPath();

        if (backendPath) {
            // Production mode - run bundled executable
            backendProcess = spawn(backendPath, [], {
                env: { ...process.env, PORT: BACKEND_PORT.toString() },
                windowsHide: true,
            });
        } else {
            // Development mode - run with uvicorn
            const backendDir = path.join(__dirname, '..', 'backend');
            backendProcess = spawn('python', [
                '-m', 'uvicorn', 'app.main:app',
                '--host', '127.0.0.1',
                '--port', BACKEND_PORT.toString(),
            ], {
                cwd: backendDir,
                env: { ...process.env },
                shell: true,       // Required on Windows for python in PATH
                windowsHide: true, // Don't show console window
            });
        }

        backendProcess.stdout.on('data', (data) => {
            console.log(`[Backend] ${data.toString()}`);
        });

        backendProcess.stderr.on('data', (data) => {
            console.log(`[Backend] ${data.toString()}`);
        });

        backendProcess.on('error', (err) => {
            console.error('Failed to start backend:', err);
            reject(err);
        });

        // Wait for backend to be ready
        const checkReady = (retries = 0) => {
            if (retries > 30) {
                reject(new Error('Backend failed to start'));
                return;
            }

            http.get(`${BACKEND_URL}/api/health`, (res) => {
                if (res.statusCode === 200) {
                    console.log('Backend is ready!');
                    resolve();
                } else {
                    setTimeout(() => checkReady(retries + 1), 1000);
                }
            }).on('error', () => {
                setTimeout(() => checkReady(retries + 1), 1000);
            });
        };

        setTimeout(() => checkReady(), 2000);
    });
}

/**
 * Stop the backend process
 */
function stopBackend() {
    if (backendProcess) {
        // Windows: use taskkill to kill the entire process tree
        if (process.platform === 'win32') {
            const { execSync } = require('child_process');
            try {
                execSync(`taskkill /pid ${backendProcess.pid} /T /F`, { windowsHide: true });
            } catch (e) {
                // Process may already be dead
            }
        } else {
            backendProcess.kill();
        }
        backendProcess = null;
    }
}

/**
 * Create the activation/license window
 */
function createActivationWindow() {
    activationWindow = new BrowserWindow({
        width: 520,
        height: 620,
        resizable: false,
        frame: false,
        transparent: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    activationWindow.loadFile(path.join(__dirname, 'activation.html'));
}

/**
 * Create the main application window
 */
function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: 1440,
        height: 900,
        minWidth: 1024,
        minHeight: 680,
        title: 'KKRPA - 自动化流程图形化编程平台',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
        },
    });

    if (app.isPackaged) {
        // Production: load static frontend
        mainWindow.loadFile(path.join(process.resourcesPath, 'frontend', 'index.html'));
    } else {
        // Development: load from Next.js dev server
        mainWindow.loadURL('http://localhost:3000');
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// ── IPC Handlers ──────────────────────────────────────────

// Check license status
ipcMain.handle('license:check', async () => {
    try {
        const res = await fetch(`${BACKEND_URL}/api/license/status`);
        return await res.json();
    } catch {
        return { activated: false, edition: 'community', message: 'Backend not ready' };
    }
});

// Activate license
ipcMain.handle('license:activate', async (event, key) => {
    try {
        const res = await fetch(`${BACKEND_URL}/api/license/activate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ license_key: key }),
        });
        return await res.json();
    } catch (err) {
        return { activated: false, message: err.message };
    }
});

// Skip activation (use community)
ipcMain.handle('license:skip', async () => {
    return { activated: true, edition: 'community', message: '使用社区版' };
});

// Proceed to main app
ipcMain.handle('app:proceed', async () => {
    if (activationWindow) {
        activationWindow.close();
        activationWindow = null;
    }
    createMainWindow();
});

// Generate a test license key
ipcMain.handle('license:generate', async (event, edition) => {
    try {
        const res = await fetch(`${BACKEND_URL}/api/license/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ edition }),
        });
        return await res.json();
    } catch (err) {
        return { error: err.message };
    }
});

// ── App Lifecycle ─────────────────────────────────────────

app.whenReady().then(async () => {
    try {
        console.log('Starting KKRPA backend...');
        await startBackend();
        console.log('Backend started, showing activation window...');
        createActivationWindow();
    } catch (err) {
        console.error('Failed to start:', err);
        app.quit();
    }
});

app.on('window-all-closed', () => {
    stopBackend();
    app.quit();
});

app.on('before-quit', () => {
    stopBackend();
});
