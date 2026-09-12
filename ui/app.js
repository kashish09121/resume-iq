const API_URL = 'http://127.0.0.1:8000/api/v1/parse';

// Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileNameDisplay = document.getElementById('file-name');
const btnRemove = document.getElementById('btn-remove');
const btnAnalyze = document.getElementById('btn-analyze');
const errorMessage = document.getElementById('error-message');
const warningMessage = document.getElementById('warning-message');

const uploadSection = document.getElementById('upload-section');
const loadingSection = document.getElementById('loading-section');
const loadingStage = document.getElementById('loading-stage');
const resultsSection = document.getElementById('results-section');
const btnReset = document.getElementById('btn-reset');

let selectedFile = null;

// Event Listeners
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFileSelect(e.target.files[0]);
    }
});

btnRemove.addEventListener('click', () => {
    selectedFile = null;
    fileInput.value = '';
    dropZone.classList.remove('hidden');
    fileInfo.classList.add('hidden');
    btnAnalyze.disabled = true;
    errorMessage.classList.add('hidden');
});

btnReset.addEventListener('click', () => {
    resultsSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    btnRemove.click(); // resets file state
});

btnAnalyze.addEventListener('click', analyzeResume);

function handleFileSelect(file) {
    errorMessage.classList.add('hidden');
    
    // Validate Extension
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (ext !== '.pdf' && ext !== '.docx') {
        showError('Unsupported file format. Please upload a PDF or DOCX.');
        return;
    }

    // Validate Size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('File is too large. Maximum size is 5MB.');
        return;
    }

    selectedFile = file;
    fileNameDisplay.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    dropZone.classList.add('hidden');
    fileInfo.classList.remove('hidden');
    btnAnalyze.disabled = false;
}

function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.classList.remove('hidden');
}

function showWarning(msg) {
    warningMessage.textContent = msg;
    warningMessage.classList.remove('hidden');
}

async function analyzeResume() {
    if (!selectedFile) return;

    // UI Transitions
    uploadSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');
    
    // Simulate stages for better UX (actual parsing is fast, this prevents flashing)
    let stageInt = setInterval(() => {
        const stages = ["Extracting text...", "Segmenting sections...", "Running NLP matching...", "Structuring results..."];
        const rand = stages[Math.floor(Math.random() * stages.length)];
        loadingStage.textContent = rand;
    }, 800);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            body: formData
        });

        clearInterval(stageInt);
        
        if (!response.ok) {
            let errorMsg = "An error occurred during processing.";
            try {
                const errData = await response.json();
                errorMsg = errData.detail || errorMsg;
            } catch (e) {}
            throw new Error(errorMsg);
        }

        const data = await response.json();
        renderResults(data);
        
        loadingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
    } catch (error) {
        clearInterval(stageInt);
        loadingSection.classList.add('hidden');
        uploadSection.classList.remove('hidden');
        showError(error.message);
    }
}

function renderResults(data) {
    // Hide warnings initially
    warningMessage.classList.add('hidden');
    
    // 1. Candidate & Contact
    document.getElementById('res-name').textContent = data.contact?.name || 'Not detected';
    document.getElementById('res-email').textContent = data.contact?.email || 'Not detected';
    document.getElementById('res-phone').textContent = data.contact?.phone || 'Not detected';
    document.getElementById('res-linkedin').textContent = data.contact?.linkedin || 'Not detected';
    document.getElementById('res-portfolio').textContent = data.contact?.portfolio || 'Not detected';
    
    // 2. Summary
    document.getElementById('res-summary').textContent = data.summary || 'Not detected';

    // 3. Experience
    const expContainer = document.getElementById('res-experience');
    if (data.experience && data.experience.length > 0) {
        expContainer.innerHTML = data.experience.map(exp => `
            <div class="list-item">
                <div class="list-title">${escapeHTML(exp.job_title || 'Unknown Title')}</div>
                <div class="list-meta">${escapeHTML(exp.company || 'Unknown Company')} | ${escapeHTML(exp.start_date || '')} - ${escapeHTML(exp.end_date || 'Present')}</div>
                <p class="text-sm">${escapeHTML(exp.description || '').replace(/\n/g, '<br>')}</p>
            </div>
        `).join('');
    } else {
        expContainer.innerHTML = '<p class="text-muted">Not detected</p>';
    }

    // 4. Education
    const eduContainer = document.getElementById('res-education');
    if (data.education && data.education.length > 0) {
        eduContainer.innerHTML = data.education.map(edu => `
            <div class="list-item">
                <div class="list-title">${escapeHTML(edu.institution || 'Unknown Institution')}</div>
                <div class="list-meta">${escapeHTML(edu.degree || '')} ${escapeHTML(edu.field ? 'in ' + edu.field : '')}</div>
                <div class="text-sm text-muted">${escapeHTML(edu.start_date || '')} - ${escapeHTML(edu.end_date || '')}</div>
            </div>
        `).join('');
    } else {
        eduContainer.innerHTML = '<p class="text-muted">Not detected</p>';
    }

    // 5. Projects
    const projContainer = document.getElementById('res-projects');
    if (data.projects && data.projects.length > 0) {
        projContainer.innerHTML = data.projects.map(proj => `
            <div class="list-item">
                <p class="text-sm">${escapeHTML(proj).replace(/\n/g, '<br>')}</p>
            </div>
        `).join('');
    } else {
        projContainer.innerHTML = '<p class="text-muted">Not detected</p>';
    }

    // 6. Skills
    const skillsContainer = document.getElementById('res-skills');
    document.getElementById('res-skills-count').textContent = `${data.skills ? data.skills.length : 0} detected`;
    
    if (data.skills && data.skills.length > 0) {
        // Group by category
        const grouped = {};
        data.skills.forEach(skill => {
            const cat = skill.category || 'Uncategorized';
            if (!grouped[cat]) grouped[cat] = [];
            grouped[cat].push(skill.canonical_name);
        });

        skillsContainer.innerHTML = Object.keys(grouped).map(cat => `
            <div class="skill-category">
                <div class="skill-category-title">${escapeHTML(cat)}</div>
                <div>
                    ${grouped[cat].map(skillName => `<span class="skill-tag">${escapeHTML(skillName)}</span>`).join('')}
                </div>
            </div>
        `).join('');
    } else {
        skillsContainer.innerHTML = '<p class="text-muted">Not detected</p>';
    }

    // Warnings mapping
    if (data.skills && data.skills.length === 0 && data.experience && data.experience.length === 0) {
         showWarning("Minimal information was extracted. This document may be a scanned image (OCR unsupported) or have a highly unusual layout.");
    }
}

function escapeHTML(str) {
    if (!str) return '';
    return String(str).replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
