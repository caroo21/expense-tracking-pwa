// ==================== AUTH HELPER ====================

const API_URL = ''; // Leer = gleiche Domain

// Token Management
function saveToken(token) {
    localStorage.setItem('auth_token', token);
}

function getToken() {
    return localStorage.getItem('auth_token');
}

function saveUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function getUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function clearAuth() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
}

function isAuthenticated() {
    return !!getToken();
}

// API Functions
async function register(username, email, password) {
    const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || 'Registrierung fehlgeschlagen');
    }

    // Token und User speichern
    saveToken(data.token);
    saveUser(data.user);

    return data;
}

async function login(username, password) {
    const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.message || 'Login fehlgeschlagen');
    }

    // Token und User speichern
    saveToken(data.token);
    saveUser(data.user);

    return data;
}

function logout() {
    clearAuth();
    window.location.href = '/index.html';
}

// Prüfe beim Laden ob User eingeloggt ist
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login.html';
    }
}
