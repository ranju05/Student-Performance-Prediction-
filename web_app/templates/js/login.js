document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById('loginForm');
  const errorDisplay = document.getElementById('loginError');

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        window.location.href = "/predict";
      } else {
        errorDisplay.textContent = result.message || 'Login failed.';
      }
    } catch (err) {
      console.error('Login error:', err);
      errorDisplay.textContent = 'Something went wrong.';
    }
  });
});
