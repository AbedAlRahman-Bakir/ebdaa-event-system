// Shared auth utilities for admin pages

function getToken() {
    return localStorage.getItem('token');
}

function getRole() {
    return localStorage.getItem('role');
}

function getUsername() {
    return localStorage.getItem('username');
}

function authHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getToken(),
    };
}

function requireAuth(allowedRoles) {
    const token = getToken();
    const role = getRole();

    if (!token) {
        window.location.href = '/login';
        return false;
    }

    if (allowedRoles && !allowedRoles.includes(role)) {
        window.location.href = '/login';
        return false;
    }

    return true;
}

function logout() {
    fetch('/auth/logout', {
        method: 'POST',
        headers: authHeaders(),
    }).finally(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        window.location.href = '/login';
    });
}
