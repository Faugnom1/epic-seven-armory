document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('https://epic-seven-armory.onrender.com/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (response.ok) {
                    localStorage.setItem('access_token', data.access_token);
                    localStorage.setItem('username', username);
                    window.location.href = 'video_overlay.html';
                } else {
                    errorMessage.textContent = 'Login failed: ' + data.msg;
                }
            } else {
                const text = await response.text();
                console.error('Error logging in:', text);
                errorMessage.textContent = 'Error logging in: ' + text;
            }
        } catch (error) {
            console.error('Error logging in:', error);
            errorMessage.textContent = 'Error logging in: ' + error;
        }
    });
});
