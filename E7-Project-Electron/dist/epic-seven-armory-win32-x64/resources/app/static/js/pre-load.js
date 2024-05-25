const { ipcRenderer } = require('electron');
const axios = require('axios');

//listener for userlogin status to change electron menus
window.addEventListener('DOMContentLoaded', () => {
    axios.get('https://epic-seven-armory.onrender.com/login_status')
        .then(response => {
            console.log(`Sending login status: ${response.data.logged_in}`);
            ipcRenderer.send('login-status', response.data.logged_in);
        })
        .catch(error => {
            console.error('Error checking login status:', error);
        });
});

//Bridge between flask app and electron twitch extension.
contextBridge.exposeInMainWorld('electron', {
    send: (channel, data) => {
        ipcRenderer.send(channel, data);
    },
    on: (channel, func) => {
        ipcRenderer.on(channel, (event, ...args) => func(...args));
    }
});
