document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        alert('Please fill in all fields');
        return;
    }

    fetch('/admin/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(async response => {
        if (response.ok) {
            // Successful login, redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Extract and display error message
            const data = await response.json();
            alert(data.error || 'Invalid username or password');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong. Please try again later.');
    });
});
