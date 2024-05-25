const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');

const isDev = process.env.NODE_ENV === 'development';
const isMac = process.platform === 'darwin';

let mainWindow;
let twitchOverlayWindow;
let flaskProcess = null;

// function startFlask() {
//     const pythonPath = 'C:\\Users\\Mike\\AppData\\Local\\Microsoft\\WindowsApps\\python.exe';
//     const scriptPath = 'C:\\Users\\Mike\\Documents\\Springy\\epic-seven-armory\\app.py';

//     flaskProcess = spawn(pythonPath, [scriptPath], { shell: true });

//     flaskProcess.stdout.on('data', (data) => {
//         console.log(`Flask: ${data}`);
//     });

//     flaskProcess.stderr.on('data', (data) => {
//         console.error(`Flask Error: ${data}`);
//     });

//     flaskProcess.on('close', (code) => {
//         console.log(`Flask process exited with code ${code}`);
//     });
// }

// function checkServerReady() {
//     return new Promise((resolve, reject) => {
//         const url = 'http://127.0.0.1:5000/';
//         const interval = setInterval(() => {
//             axios.get(url)
//                 .then(response => {
//                     if (response.status === 200) {
//                         console.log('Flask server is ready.');
//                         clearInterval(interval);
//                         resolve();
//                     }
//                 })
//                 .catch(error => {
//                     console.log('Waiting for Flask server to start...');
//                 });
//         }, 2000);
//     });
// }

async function createMainWindow() {
    mainWindow = new BrowserWindow({
        title: 'E7',
        width: 1100,
        height: 890,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            preload: path.join(__dirname, '/static/js/pre-load.js')
        }
    });

    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.loadFile(path.join(__dirname, '/renderer/splash.html'));

    mainWindow.loadURL('https://epic-seven-armory.onrender.com/');

    mainWindow.on('closed', () => {
        mainWindow = null;
        if (flaskProcess != null) {
            flaskProcess.kill();
        }
    });
}

function createTwitchWindow() {
    twitchOverlayWindow = new BrowserWindow({
        width: 800,
        height: 850,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: false 
        }
    });

    twitchOverlayWindow.loadFile('./renderer/login.html');
    twitchOverlayWindow.removeMenu();

//     fetchSelectedUnitsData(twitchOverlayWindow);
//     setInterval(() => fetchSelectedUnitsData(twitchOverlayWindow), 1000); // Fetch data every 5 seconds
}

// function fetchSelectedUnitsData(window) {
//     fetch('http://localhost:5000/get_selected_units_data')
//         .then(response => response.json())
//         .then(unitsData => {
//             window.webContents.send('update-unit-data', unitsData);
//         })
//         .catch(error => console.error(error));
// }

function createAboutWindow() {
    const aboutWindow = new BrowserWindow({
        title: 'About E7 App',
        width: 400,
        height: 300
    });

    aboutWindow.loadFile(path.join(__dirname, './renderer/about.html'));
    aboutWindow.removeMenu();
}

const initialMenuTemplate = [
    ...(isMac ? [{
        label: app.name,
        submenu: [
            {
                label: 'About',
                click: createAboutWindow,
            },
            { type: 'separator' },
            { role: 'quit' }
        ]
    }] : []),
    {
        role: 'fileMenu',
    },
    {
        label: 'Help',
        submenu: [
            {
                label: 'About',
                click: createAboutWindow,
            },
        ],
    },
];

const loggedInMenuTemplate = [
    ...(isMac ? [{
        label: app.name,
        submenu: [
            {
                label: 'About',
                click: createAboutWindow,
            },
            { type: 'separator' },
            { role: 'quit' }
        ]
    }] : []),
    {
        role: 'fileMenu',
    },
    {
        label: 'Twitch Overlay',
        click: createTwitchWindow,
    },
    {
        label: 'Help',
        submenu: [
            {
                label: 'About',
                click: createAboutWindow,
            },
        ],
    },
];

function createMenu(isLoggedIn) {
    console.log(`Creating menu. User logged in: ${isLoggedIn}`);
    const template = isLoggedIn ? loggedInMenuTemplate : initialMenuTemplate;
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

app.whenReady().then(() => {
    // startFlask();
    createMainWindow();
    createMenu(false);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createMainWindow();
        }
    });
});

ipcMain.on('login-status', (event, isLoggedIn) => {
    console.log(`Received login status: ${isLoggedIn}`);
    createMenu(isLoggedIn);
});


app.on('window-all-closed', () => {
    if (!isMac) {
        app.quit();
    }
});

app.on('quit', () => {
    if (flaskProcess != null) {
        flaskProcess.kill();
    }
});
