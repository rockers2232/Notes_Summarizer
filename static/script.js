// ELEMENTS
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const resultsArea = document.getElementById('results-area');
const extractedTextDiv = document.getElementById('extracted-text');
const aiResultDiv = document.getElementById('ai-result');
const downloadBtn = document.getElementById('download-btn');

const dashboardView = document.getElementById('dashboard-view');
const historyView = document.getElementById('history-view');
const navDashboard = document.getElementById('nav-dashboard');
const navHistory = document.getElementById('nav-history');

// === UPLOAD LOGIC ===
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleUpload);

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#4A90E2';
    dropZone.style.backgroundColor = '#F7FAFC';
});
dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '#CBD5E0';
    dropZone.style.backgroundColor = '#ffffff';
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#CBD5E0';
    dropZone.style.backgroundColor = '#ffffff';
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleUpload();
    }
});

function handleUpload() {
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    // Show Loading
    resultsArea.style.display = 'grid';
    downloadBtn.style.display = 'none';
    extractedTextDiv.innerHTML = '<div style="text-align:center; padding:20px; color:#aaa"><i class="fas fa-spinner fa-spin fa-2x"></i><br><br>Scanning...</div>';
    aiResultDiv.innerHTML = '<div style="text-align:center; padding:20px; color:#aaa"><i class="fas fa-brain fa-spin fa-2x"></i><br><br>Thinking...</div>';

    fetch('/upload', { method: 'POST', body: formData })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            aiResultDiv.innerHTML = `<span style="color:red">Error: ${data.error}</span>`;
            return;
        }
        renderResult(data.text, data.result);
    })
    .catch(error => alert('Upload failed.'));
}

function renderResult(text, result) {
    extractedTextDiv.innerText = text;
    aiResultDiv.innerHTML = result;
    
    if (!result.includes("Error") && !result.includes("warming up")) {
        downloadBtn.style.display = 'block';
    } else {
        downloadBtn.style.display = 'none';
    }
}

// === HISTORY LOGIC ===

function showDashboard() {
    dashboardView.style.display = 'block';
    historyView.style.display = 'none';
    navDashboard.classList.add('active');
    navHistory.classList.remove('active');
}

function showHistory() {
    dashboardView.style.display = 'none';
    historyView.style.display = 'block';
    navDashboard.classList.remove('active');
    navHistory.classList.add('active');

    fetch('/history')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('history-list');
            list.innerHTML = ''; 

            if (data.length === 0) {
                list.innerHTML = '<p style="color:#aaa;">No history yet. Upload a file!</p>';
                return;
            }

            data.forEach(item => {
                const card = document.createElement('div');
                card.className = 'history-card';
                // Clean HTML tags
                const cleanSummary = item.summary.replace(/<[^>]*>?/gm, ''); 

                card.innerHTML = `
                    <div>
                        <div class="history-header">
                            <div class="history-title">
                                <i class="fas fa-file-pdf" style="color:#e53e3e"></i> ${item.filename}
                            </div>
                            <button class="delete-btn" onclick="deleteHistoryItem(${item.id}, event)">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                        <div class="history-preview">
                            ${cleanSummary.substring(0, 150)}...
                        </div>
                    </div>
                    <div class="history-footer">
                        <i class="fas fa-external-link-alt"></i> Click to Open
                    </div>
                `;
                
                card.onclick = () => loadHistoryItem(item);
                list.appendChild(card);
            });
        });
}

function loadHistoryItem(item) {
    showDashboard(); 
    resultsArea.style.display = 'grid'; 
    renderResult(item.original_text, item.summary); 
}

// --- NEW: DELETE FUNCTION ---
function deleteHistoryItem(id, event) {
    // Stop the card click event so it doesn't open the note when we try to delete it
    event.stopPropagation();
    
    if(confirm("Are you sure you want to delete this note?")) {
        fetch(`/delete/${id}`, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                showHistory(); // Refresh the list
            } else {
                alert("Error deleting note");
            }
        });
    }
}

// === PDF DOWNLOAD ===
function downloadPDF() {
    const element = document.getElementById('ai-result');
    const opt = {
        margin: [15, 15, 15, 15],
        filename: 'StudyAI_Notes.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
}