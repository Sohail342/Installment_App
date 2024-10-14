const { app, BrowserWindow } = require('electron');

function ElectroMainMethod() {
    const launchWindow = new BrowserWindow({
        title: 'Sales Person Dashboards',
        width: 1777,
        height: 1444
    });

    const appUrl = "http://127.0.0.1:8000";
    launchWindow.loadURL(appUrl);
}

app.whenReady().then(ElectroMainMethod);
