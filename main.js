const { app, BrowserWindow, ipcMain, Menu, dialog } = require('electron');
const path = require('path');
const { exec, spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

let pythonProcess; 
let mainWindow; 

function checkAndInstallPython() {
  exec('python --version', (error, stdout, stderr) => {
    if (error || stderr) {
      const pythonInstallerUrl = "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe";
      const installerPath = path.join(os.homedir(), 'Downloads', 'python-installer.exe');
      
      exec(`powershell -Command "Invoke-WebRequest -Uri ${pythonInstallerUrl} -OutFile ${installerPath}"`, (error) => {
        if (error) {
          dialog.showErrorBox('Error', error.message);
          return;
        }

        exec(`"${installerPath}" /quiet InstallAllUsers=1 PrependPath=1`, (error) => {
          if (error) {
            dialog.showErrorBox('Error', error.message);
            return;
          }
          checkAndInstallPythonModules();
        });
      });
    } else {
      checkAndInstallPythonModules(); 
    }
  });
}

function checkAndInstallPythonModules() {
  let moduleinstall = spawn('pip', ['install', 'sys', 'cx-Freeze', 'blinker', 'utility', 'opencv-python', 'mss', 'numpy', 'pyautogui', 'pygetwindow', 'keyboard', 'pywin32', 'pywinauto']);

  moduleinstall.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  moduleinstall.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  moduleinstall.on('close', (code) => {
    console.log(`Python module install process exited with code ${code}`);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 600,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'gui/preload.js'),
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false,
      enableRemoteModule: false
    },
    icon: path.join(__dirname, 'icon.ico'),
    title: "Blum Farmer | @umutxyp",
  });

  mainWindow.loadFile('gui/index.html');

  mainWindow.on('closed', () => {
    mainWindow = null;
    app.quit(); 
  });
}

app.whenReady().then(() => {
  checkAndInstallPython();
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('before-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill();
    console.log('Python process killed');
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

Menu.setApplicationMenu(null);

const pythonScriptPath = path.join(app.getAppPath(), 'main.py');

if (!fs.existsSync(pythonScriptPath)) {
  dialog.showErrorBox('Error', 'Python script not found.');
  app.quit();
}

ipcMain.on('start_blum_farmer', (event, args) => {
  const { speed, pause } = args;

  pythonProcess = spawn('python', [pythonScriptPath, speed, pause]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python script exited with code ${code}`);
  });
});
