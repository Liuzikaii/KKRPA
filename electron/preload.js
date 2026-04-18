const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('kkrpa', {
    // License operations
    checkLicense: () => ipcRenderer.invoke('license:check'),
    activateLicense: (key) => ipcRenderer.invoke('license:activate', key),
    skipActivation: () => ipcRenderer.invoke('license:skip'),
    generateLicense: (edition) => ipcRenderer.invoke('license:generate', edition),

    // App operations
    proceed: () => ipcRenderer.invoke('app:proceed'),
});
