document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('loginForm');
    const errorDisplay = document.getElementById('loginError');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();

        if (!username || !password) {
            errorDisplay.textContent = 'Please fill in all fields.';
            return;
        }

        try {
            const response = await fetch('/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                // Redirect to dashboard on successful login
                window.location.href = '/admin_dashboard';
            } else {
                const data = await response.json();
                errorDisplay.textContent = data.error || 'Invalid credentials.';
            }
        } catch (error) {
            console.error('Login error:', error);
            errorDisplay.textContent = 'An error occurred. Please try again later.';
        }
    });
});
