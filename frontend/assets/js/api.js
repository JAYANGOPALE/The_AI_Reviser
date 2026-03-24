const API_BASE = "/api/v1";

// --- THEME MANAGEMENT ---

function initTheme() {
    const savedTheme = localStorage.getItem('revise_ai_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('revise_ai_theme', newTheme);
}

// Initialize theme on script load
initTheme();

// --- AUTH FUNCTIONS ---

async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return await response.json();
    } catch (e) { console.error("Login error:", e); return { error: "Connection error" }; }
}

function logout() {
    localStorage.removeItem('revise_ai_token');
    localStorage.removeItem('revise_ai_user');
    window.location.href = 'login.html';
}

// --- USER PROFILE FUNCTIONS ---

async function getProfile() {
    const token = localStorage.getItem('revise_ai_token');
    try {
        const response = await fetch(`${API_BASE}/user/profile`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('revise_ai_user', JSON.stringify(data));
        }
        return data;
    } catch (e) { console.error("Profile fetch error:", e); return { error: "Connection error" }; }
}

async function updateProfile(userData) {
    const token = localStorage.getItem('revise_ai_token');
    try {
        const response = await fetch(`${API_BASE}/user/profile`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify(userData)
        });
        return await response.json();
    } catch (e) { console.error("Profile update error:", e); return { error: "Connection error" }; }
}

// --- DATA FETCH FUNCTIONS ---

async function getLevels() {
    try {
        const response = await fetch(`${API_BASE}/levels`);
        return await response.json();
    } catch (e) { console.error("Error fetching levels:", e); return []; }
}

async function getSubjects(level) {
    try {
        const response = await fetch(`${API_BASE}/subjects?level=${level}`);
        return await response.json();
    } catch (e) { console.error("Error fetching subjects:", e); return []; }
}

async function getChapters(level, subject) {
    try {
        const response = await fetch(`${API_BASE}/chapters?level=${level}&subject=${subject}`);
        return await response.json();
    } catch (e) { console.error("Error fetching chapters:", e); return []; }
}

async function loadChapterNotes(chapterId) {
    try {
        const response = await fetch(`${API_BASE}/chapters/${chapterId}`);
        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        // Update the UI
        document.getElementById('chapter-title').innerText = data.title;
        document.getElementById('notes-display').innerHTML = `
            <div class="note-card">
                <h3>${data.subject} - ${data.title} (${data.level})</h3>
                <div class="summary-content">
                    ${data.summary}
                </div>
                ${data.pdf_url ? `<a href="${data.pdf_url}" target="_blank" class="pdf-btn"><i class="fas fa-file-pdf"></i> View Original PDF</a>` : ''}
            </div>
        `;
    } catch (e) { console.error("Error loading chapter notes:", e); }
}
