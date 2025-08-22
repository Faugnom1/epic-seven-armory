// main.js
const { app, BrowserWindow, Menu, ipcMain, shell } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const { googleDesktopSignIn } = require("./auth/google_native");

let mainWindow;
let pythonProcess = null;
let statusCheckInterval = null;
let monitorEnabled = false;

// Use this to compare origins when deciding if a link is external
const APP_URL = process.env.APP_URL || "http://localhost:3000";
const APP_ORIGIN = new URL(APP_URL).origin;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1300,
    height: 1000,
    minWidth: 970,
    minHeight: 660,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      enableRemoteModule: false,
    },
  });

  mainWindow.loadURL(APP_URL);

  // Open any target="_blank"/window.open external link in the default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    try {
      const dest = new URL(url);
      // Allow same-origin (your app), send everything else to the system browser
      if (dest.origin === APP_ORIGIN) {
        return { action: "allow" };
      }
    } catch {
      // Non-HTTP(S) or invalid URL — treat as external
    }
    shell.openExternal(url);
    return { action: "deny" };
  });

  // Prevent in-app navigation to external sites (but allow same-origin)
  mainWindow.webContents.on("will-navigate", (event, url) => {
    try {
      const dest = new URL(url);
      if (dest.origin !== APP_ORIGIN) {
        event.preventDefault();
        shell.openExternal(url);
      }
      // else: same-origin (e.g., http://localhost:3000/route) — allow
    } catch {
      // If URL can't be parsed, be safe and block
      event.preventDefault();
      shell.openExternal(url);
    }
  });

  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
    updateHeroData();
    // Monitor is user-toggled
    mainWindow.webContents.openDevTools();
  });

  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  // Hide default menu
  Menu.setApplicationMenu(null);

  if (!statusCheckInterval) {
    statusCheckInterval = setInterval(checkMonitorStatus, 1000);
  }
}

// ---------- Helper: load Google client from JSON (no env vars) ----------
function loadGoogleClientFromFile() {
  const candidates = [
    path.join(__dirname, "backend", "config", "google_oauth.json"),
    path.join(__dirname, "config", "google_oauth.json"),
    process.resourcesPath
      ? path.join(
          process.resourcesPath,
          "backend",
          "config",
          "google_oauth.json"
        )
      : null,
  ].filter(Boolean);

  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) {
        const { client_id, client_secret } = JSON.parse(
          fs.readFileSync(p, "utf8")
        );
        const clientId = (client_id || "").trim();
        const clientSecret = (client_secret || "").trim();
        if (clientId) return { clientId, clientSecret, path: p };
      }
    } catch {
      // try next
    }
  }
  return { clientId: "", clientSecret: "", path: "(not found)" };
}

// ---------- Update hero data (unchanged) ----------
function updateHeroData() {
  const updateScript = path.join(__dirname, "python", "update_hero_data.py");
  console.log("Updating hero data...");

  const updateProcess = spawn("python", [updateScript]);

  updateProcess.stdout.on("data", (data) => {
    console.log(`Update script output: ${data}`);
    if (mainWindow && !mainWindow.isDestroyed())
      mainWindow.webContents.send("update-output", data.toString());
  });

  updateProcess.stderr.on("data", (data) => {
    console.error(`Update script error: ${data}`);
    if (mainWindow && !mainWindow.isDestroyed())
      mainWindow.webContents.send("update-error", data.toString());
  });

  updateProcess.on("close", (code) => {
    console.log(`Update script exited with code ${code}`);
    if (mainWindow && !mainWindow.isDestroyed())
      mainWindow.webContents.send("update-complete", code);
  });
}

// ---------- Monitor controls (unchanged behavior) ----------
function startPythonScript() {
  if (pythonProcess) return;
  const scriptPath = path.join(__dirname, "python", "monitor.py");
  console.log("Starting Python script:", scriptPath);

  pythonProcess = spawn("python", [scriptPath]);

  pythonProcess.stdout.on("data", (data) => {
    console.log(`Python script output: ${data}`);
    if (mainWindow && !mainWindow.isDestroyed())
      mainWindow.webContents.send("python-output", data.toString());
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`Python script error: ${data}`);
    if (mainWindow && !mainWindow.isDestroyed())
      mainWindow.webContents.send("python-error", data.toString());
  });

  pythonProcess.on("close", (code) => {
    console.log(`Python script exited with code ${code}`);
    pythonProcess = null;
    monitorEnabled = false;
    writeMonitorStatus({ enabled: false, found: false, bbox: null });
    if (mainWindow && !mainWindow.isDestroyed())
      mainWindow.webContents.send("python-exit", code);
  });

  monitorEnabled = true;
  writeMonitorStatus({ enabled: true, found: false, bbox: null });
}

function stopPythonScript() {
  if (pythonProcess) {
    try {
      pythonProcess.kill();
    } catch (e) {
      console.error("Error killing python process:", e);
    }
    pythonProcess = null;
  }
  monitorEnabled = false;
  writeMonitorStatus({ enabled: false, found: false, bbox: null });
}

function writeMonitorStatus(status) {
  const projectPath = path.join("C:", "Projects", "EpicSevenArmory");
  const statusPath = path.join(projectPath, "monitor_status.json");
  try {
    if (!fs.existsSync(projectPath))
      fs.mkdirSync(projectPath, { recursive: true });
    fs.writeFileSync(statusPath, JSON.stringify(status, null, 2), "utf8");
  } catch (err) {
    console.error("Error writing monitor_status.json:", err);
  }
}

function checkMonitorStatus() {
  const projectPath = path.join("C:", "Projects", "EpicSevenArmory");
  const statusPath = path.join(projectPath, "monitor_status.json");

  if (!fs.existsSync(projectPath))
    fs.mkdirSync(projectPath, { recursive: true });

  fs.readFile(statusPath, "utf8", (err, data) => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      if (err) {
        mainWindow.webContents.send("monitor-status", { status: "unknown" });
      } else {
        try {
          if (!data.trim()) {
            mainWindow.webContents.send("monitor-status", {
              status: "unknown",
              message: "Status file is empty",
            });
            return;
          }
          const status = JSON.parse(data);
          mainWindow.webContents.send("monitor-status", status);
        } catch (parseErr) {
          console.error("Error parsing status file:", parseErr);
          console.log("Raw file content:", data);
          mainWindow.webContents.send("monitor-status", {
            status: "error",
            message: "Invalid status data",
          });
        }
      }
    }
  });
}

// ---------- App lifecycle ----------
app.whenReady().then(createWindow);
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
app.on("will-quit", () => {
  stopPythonScript();
  if (statusCheckInterval) clearInterval(statusCheckInterval);
});

// ---------- IPC ----------
ipcMain.on("restart-monitor", () => {
  stopPythonScript();
  startPythonScript();
});
ipcMain.handle("monitor-toggle", async (_event, { enabled }) => {
  if (enabled) startPythonScript();
  else stopPythonScript();
  return { enabled: enabled && !!pythonProcess };
});

// Google OAuth — load client from JSON (no env vars)
ipcMain.handle("google-oauth-signin", async () => {
  try {
    const { clientId, clientSecret } = loadGoogleClientFromFile();
    if (!clientId) {
      return {
        ok: false,
        error:
          "Missing client_id. Create backend/config/google_oauth.json with your Desktop Client ID.",
      };
    }
    const result = await googleDesktopSignIn({ clientId, clientSecret });
    return { ok: true, ...result };
  } catch (err) {
    console.error("google-oauth-signin error:", err);
    return { ok: false, error: String(err && err.message ? err.message : err) };
  }
});
