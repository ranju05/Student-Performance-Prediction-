console.log("✅ register.js loaded");

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById('registerForm');
  const errorDisplay = document.getElementById('registerError');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    try {
      const response = await fetch('/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok) {
        alert(result.message || "Registration successful!");
        window.location.href = "/login";
      } else {
        errorDisplay.textContent = result.message || "Registration failed. Please try again.";
      }
    } catch (error) {
      console.error("Registration error:", error);
      errorDisplay.textContent = "Something went wrong. Please try again.";
    }
  });
});
