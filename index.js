const { app, BrowserWindow } = require('electron');

function ElectroMainMethod() {
    const launchWindow = new BrowserWindow({
        title: 'Sales Person Dashboards',
        fullscreen: true,
        width: 777,
        height: 444
    });

    const appUrl = "http://127.0.0.1:8000";
    launchWindow.loadURL(appUrl);
}

app.whenReady().then(ElectroMainMethod);
