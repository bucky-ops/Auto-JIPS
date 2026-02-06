// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// DOM Elements
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const analysisForm = document.getElementById('analysisForm');
const loadingState = document.getElementById('loadingState');
const resultsContainer = document.getElementById('results');
const analyzeButton = document.querySelector('.btn-analyze');

// Tab Switching
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;

        // Update active tab button
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        // Update active tab content
        tabContents.forEach(content => {
            if (content.dataset.content === tabName) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });
    });
});

// Form Submission
analysisForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form data
    const activeTab = document.querySelector('.tab-btn.active').dataset.tab;
    const jobText = document.getElementById('jobText').value.trim();
    const jobUrl = document.getElementById('jobUrl').value.trim();
    const resumeText = document.getElementById('resumeText').value.trim();

    // Validate input
    if (activeTab === 'text' && !jobText) {
        showError('Please enter a job description');
        return;
    }

    if (activeTab === 'url' && !jobUrl) {
        showError('Please enter a job posting URL');
        return;
    }

    // Prepare request payload
    const payload = {
        job_posting: {
            text: activeTab === 'text' ? jobText : null,
            url: activeTab === 'url' ? jobUrl : null
        },
        resume_text: resumeText || null
    };

    // Show loading state
    showLoading();

    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display results
        displayResults(data);

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('Error analyzing job posting:', error);
        showError('Failed to analyze job posting. Please try again.');
    } finally {
        hideLoading();
    }
});

// Show Loading State
function showLoading() {
    analyzeButton.classList.add('loading');
    analyzeButton.disabled = true;
    resultsContainer.classList.add('hidden');
}

// Hide Loading State
function hideLoading() {
    analyzeButton.classList.remove('loading');
    analyzeButton.disabled = false;
}

// Show Error Message
function showError(message) {
    // Create error alert
    const errorDiv = document.createElement('div');
    errorDiv.className = 'critique-item critical';
    errorDiv.style.marginTop = '1rem';
    errorDiv.innerHTML = `
        <span class="critique-severity">Error</span>
        <p>${message}</p>
    `;

    // Insert after form
    analysisForm.insertAdjacentElement('afterend', errorDiv);

    // Remove after 5 seconds
    setTimeout(() => errorDiv.remove(), 5000);
}

// Display Results
function displayResults(data) {
    resultsContainer.classList.remove('hidden');

    resultsContainer.innerHTML = `
        <div class="result-header">
            <h2 class="result-title">${escapeHtml(data.title || 'Job Analysis')}</h2>
            <div class="result-summary">${escapeHtml(data.summary)}</div>
        </div>
        
        ${data.resume_alignment !== null ? `
        <div class="result-section">
            <div class="resume-match">
                <div class="match-score">${Math.round(data.resume_alignment * 100)}%</div>
                <div class="match-label">Resume Match Score</div>
            </div>
        </div>
        ` : ''}
        
        <div class="result-section">
            <h3>
                <span>🎯</span>
                Focus Areas
            </h3>
            <div class="focus-areas">
                ${data.focus_areas.map(area => `
                    <div class="focus-area">
                        <div class="focus-area-header">
                            <div class="focus-area-name">${escapeHtml(area.name)}</div>
                            <div class="focus-area-weight">${Math.round(area.weight * 100)}%</div>
                        </div>
                        <div class="skill-tags">
                            ${area.skills.map(skill => `
                                <span class="skill-tag">${escapeHtml(skill)}</span>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div class="result-section">
            <h3>
                <span>💡</span>
                Explicit Skills (${data.explicit_skills.length})
            </h3>
            <div class="skill-tags">
                ${data.explicit_skills.map(skill => `
                    <span class="skill-tag">${escapeHtml(skill)}</span>
                `).join('')}
            </div>
        </div>
        
        ${data.hidden_skills.length > 0 ? `
        <div class="result-section">
            <h3>
                <span>🔍</span>
                Hidden Skills (${data.hidden_skills.length})
            </h3>
            <div class="skill-tags">
                ${data.hidden_skills.map(skill => `
                    <span class="skill-tag">${escapeHtml(skill)}</span>
                `).join('')}
            </div>
            <p style="margin-top: 1rem; color: var(--text-secondary); font-size: 0.875rem;">
                These skills are commonly associated with the explicit requirements but weren't directly mentioned.
            </p>
        </div>
        ` : ''}
        
        <div class="result-section">
            <h3>
                <span>⚠️</span>
                Requirement Critiques (${data.critiques.length})
            </h3>
            <div class="critique-list">
                ${data.critiques.map(critique => `
                    <div class="critique-item ${critique.severity}">
                        <span class="critique-severity">${critique.severity}</span>
                        <p>${escapeHtml(critique.message)}</p>
                    </div>
                `).join('')}
            </div>
        </div>
        
        <div style="margin-top: 2rem; text-align: center;">
            <button onclick="window.print()" class="btn btn-secondary">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M5 7V3H15V7M5 17H15M5 13H15V17H5V13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Print Report
            </button>
        </div>
    `;
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Smooth Scrolling for Navigation Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add scroll animation for sections
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});

// Example data for testing (can be removed in production)
window.testAnalysis = function () {
    const sampleData = {
        title: "Senior Backend Engineer",
        summary: "**Senior Backend Engineer** (Senior Level) | Key skills: python, aws, postgresql, docker, kubernetes | Primary focus: Backend Development (60% match) | Inferred 15 hidden skills that may be valuable | Job posting quality: B",
        focus_areas: [
            {
                name: "Backend Development",
                weight: 0.6,
                skills: ["python", "fastapi", "postgresql", "api"]
            },
            {
                name: "Cloud & Infrastructure",
                weight: 0.4,
                skills: ["aws", "docker", "kubernetes"]
            }
        ],
        explicit_skills: ["python", "fastapi", "postgresql", "aws", "docker", "kubernetes", "api", "rest"],
        hidden_skills: ["testing", "packaging", "type hints", "virtual environments", "pip", "pytest", "iam", "vpc", "cloudwatch", "s3", "ec2", "containerization", "dockerfile", "docker compose"],
        critiques: [
            {
                severity: "info",
                message: "No salary or compensation information provided. Including salary range increases application rates and attracts more qualified candidates."
            },
            {
                severity: "info",
                message: "Work location or remote policy not clearly specified."
            }
        ],
        resume_alignment: 0.75
    };

    displayResults(sampleData);
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

console.log('AJIPS UI loaded successfully!');
console.log('Tip: Use window.testAnalysis() to see sample results');
