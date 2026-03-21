const API_BASE = "http://127.0.0.1:5000/api/v1";

// Function for Teammate to load a chapter's notes
async function loadChapterNotes(chapterId) {
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
            <h3>Summary</h3>
            <p>${data.summary}</p>
            <a href="${data.pdf_url}" target="_blank" class="pdf-btn">View Original PDF</a>
        </div>
    `;
}
