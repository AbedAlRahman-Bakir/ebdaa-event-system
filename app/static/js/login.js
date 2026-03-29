const alertContainer = document.getElementById('alert-container');
const loginBtn = document.getElementById('login-btn');

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    alertContainer.innerHTML = '';
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';

    const payload = {
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
    };

    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('token', data.data.access_token);
            localStorage.setItem('role', data.data.user.role);
            localStorage.setItem('username', data.data.user.username);

            // Redirect based on role
            if (data.data.user.role === 'admin') {
                window.location.href = '/admin/dashboard';
            } else {
                window.location.href = '/admin/checkin';
            }
        } else {
            showAlert(data.message || 'Login failed', 'danger');
        }
    } catch (err) {
        showAlert('Something went wrong. Please try again.', 'danger');
    }

    loginBtn.disabled = false;
    loginBtn.textContent = 'Login';
});

function showAlert(message, type) {
    alertContainer.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>`;
}
