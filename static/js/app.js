// PR Review Agent - Frontend JavaScript
class PRReviewApp {
    constructor() {
        this.currentAnalysis = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadHistory();
    }

    setupEventListeners() {
        // Code editor
        const codeEditor = document.getElementById('code-editor');
        codeEditor.addEventListener('input', () => this.updateLineCount());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'Enter':
                        e.preventDefault();
                        this.analyzeCode();
                        break;
                    case 'k':
                        e.preventDefault();
                        this.clearCode();
                        break;
                }
            }
        });
    }

    updateLineCount() {
        const codeEditor = document.getElementById('code-editor');
        const lines = codeEditor.value.split('\n').length;
        document.getElementById('line-count').textContent = `${lines} lines`;
    }

    async analyzeCode() {
        const codeEditor = document.getElementById('code-editor');
        const code = codeEditor.value.trim();
        
        if (!code) {
            this.showNotification('Please enter some code to analyze', 'warning');
            return;
        }

        this.showLoading(true);
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code,
                    filename: 'main.py'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentAnalysis = data;
                this.displayResults(data);
                this.showNotification('Analysis completed successfully!', 'success');
            } else {
                throw new Error(data.error || 'Analysis failed');
            }
        } catch (error) {
            this.showNotification(`Error: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async runDemo() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/demo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentAnalysis = data;
                this.displayResults(data);
                this.showNotification('Demo analysis completed!', 'success');
            } else {
                throw new Error(data.error || 'Demo failed');
            }
        } catch (error) {
            this.showNotification(`Error: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        // Update score display
        const scoreElement = document.querySelector('.score-value');
        const score = data.score;
        scoreElement.textContent = score.toFixed(1);
        
        // Color code the score
        scoreElement.className = 'score-value';
        if (score >= 8) {
            scoreElement.style.color = 'var(--severity-low)';
        } else if (score >= 6) {
            scoreElement.style.color = 'var(--severity-medium)';
        } else {
            scoreElement.style.color = 'var(--severity-high)';
        }

        // Update summary
        this.updateSummary(data);
        
        // Update issues
        this.updateIssues(data.issues);
        
        // Update suggestions
        this.updateSuggestions(data.suggestions, data.strengths);
        
        // Update badges
        document.getElementById('issues-badge').textContent = data.issues_count;
        
        // Show summary tab
        this.showTab('summary');
    }

    updateSummary(data) {
        const welcomeMessage = document.getElementById('welcome-message');
        const summaryContent = document.getElementById('summary-content');
        
        welcomeMessage.style.display = 'none';
        summaryContent.style.display = 'block';
        
        // Update stats
        document.getElementById('total-lines').textContent = data.file_stats.lines;
        document.getElementById('issues-found').textContent = data.issues_count;
        document.getElementById('suggestions-count').textContent = data.suggestions.length;
        
        // Update summary text
        const summaryText = document.getElementById('summary-text');
        summaryText.textContent = data.summary;
    }

    updateIssues(issues) {
        const issuesContent = document.getElementById('issues-content');
        
        if (issues.length === 0) {
            issuesContent.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-check-circle"></i>
                    <p>No issues found! Your code looks great!</p>
                </div>
            `;
            return;
        }

        // Group issues by severity
        const groupedIssues = {
            critical: issues.filter(issue => issue.severity === 'critical'),
            high: issues.filter(issue => issue.severity === 'high'),
            medium: issues.filter(issue => issue.severity === 'medium'),
            low: issues.filter(issue => issue.severity === 'low')
        };

        let html = '';
        
        ['critical', 'high', 'medium', 'low'].forEach(severity => {
            const severityIssues = groupedIssues[severity];
            if (severityIssues.length === 0) return;
            
            html += `<div class="severity-group">
                <h4 style="color: var(--severity-${severity}); margin-bottom: 1rem;">
                    ${severity.toUpperCase()} SEVERITY (${severityIssues.length} issues)
                </h4>`;
            
            severityIssues.forEach(issue => {
                html += `
                    <div class="issue">
                        <div class="issue-header">
                            <span class="severity-badge severity-${issue.severity}">${issue.severity}</span>
                            <span class="issue-location">${issue.file_path}:${issue.line_number}</span>
                        </div>
                        <div class="issue-message">${issue.message}</div>
                        ${issue.suggestion ? `<div class="issue-suggestion">💡 ${issue.suggestion}</div>` : ''}
                    </div>
                `;
            });
            
            html += '</div>';
        });

        issuesContent.innerHTML = html;
    }

    updateSuggestions(suggestions, strengths) {
        const suggestionsContent = document.getElementById('suggestions-content');
        
        let html = '';
        
        if (suggestions.length > 0) {
            html += '<h4 style="margin-bottom: 1rem; color: var(--github-text);">💡 Suggestions</h4>';
            suggestions.forEach((suggestion, index) => {
                html += `
                    <div class="suggestion">
                        <div class="suggestion-icon">💡</div>
                        <div class="suggestion-text">${suggestion}</div>
                    </div>
                `;
            });
        }
        
        if (strengths && strengths.length > 0) {
            html += '<h4 style="margin: 2rem 0 1rem 0; color: var(--github-text);">✨ Strengths</h4>';
            strengths.forEach(strength => {
                html += `
                    <div class="suggestion">
                        <div class="suggestion-icon">✨</div>
                        <div class="suggestion-text">${strength}</div>
                    </div>
                `;
            });
        }
        
        if (html === '') {
            html = `
                <div class="empty-state">
                    <i class="fas fa-lightbulb"></i>
                    <p>No suggestions available. Your code follows best practices!</p>
                </div>
            `;
        }
        
        suggestionsContent.innerHTML = html;
    }

    showTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });
        
        // Show selected tab
        document.getElementById(`${tabName}-tab`).classList.add('active');
        document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
    }

    clearCode() {
        document.getElementById('code-editor').value = '';
        this.updateLineCount();
        this.clearResults();
    }

    clearResults() {
        // Reset score
        document.querySelector('.score-value').textContent = '--';
        document.querySelector('.score-value').style.color = 'var(--github-text)';
        
        // Reset badges
        document.getElementById('issues-badge').textContent = '0';
        
        // Show welcome message
        document.getElementById('welcome-message').style.display = 'block';
        document.getElementById('summary-content').style.display = 'none';
        
        // Clear other tabs
        document.getElementById('issues-content').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-bug"></i>
                <p>No issues found yet. Analyze your code to see results.</p>
            </div>
        `;
        
        document.getElementById('suggestions-content').innerHTML = `
            <div class="empty-state">
                <i class="fas fa-lightbulb"></i>
                <p>No suggestions yet. Analyze your code to see recommendations.</p>
            </div>
        `;
        
        // Show summary tab
        this.showTab('summary');
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            if (data.success) {
                this.updateHistoryDisplay(data.history);
            }
        } catch (error) {
            console.error('Failed to load history:', error);
        }
    }

    updateHistoryDisplay(history) {
        const historyContent = document.getElementById('history-content');
        
        if (history.length === 0) {
            historyContent.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <p>No analysis history yet.</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        history.reverse().forEach(item => {
            const date = new Date(item.timestamp);
            html += `
                <div class="history-item" onclick="app.loadHistoryItem('${item.id}')">
                    <div class="history-header">
                        <div class="history-filename">${item.filename}</div>
                        <div class="history-timestamp">${date.toLocaleString()}</div>
                    </div>
                    <div class="history-stats">
                        <span>Score: ${item.score.toFixed(1)}/10</span>
                        <span>Issues: ${item.issues_count}</span>
                    </div>
                </div>
            `;
        });
        
        historyContent.innerHTML = html;
    }

    loadHistoryItem(analysisId) {
        const item = analysis_history.find(h => h.id === analysisId);
        if (item) {
            this.currentAnalysis = item;
            this.displayResults(item);
            this.closeHistory();
        }
    }

    showHistory() {
        document.getElementById('history-modal').classList.add('show');
        this.loadHistory();
    }

    closeHistory() {
        document.getElementById('history-modal').classList.remove('show');
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '6px',
            color: 'white',
            fontWeight: '500',
            zIndex: '1001',
            animation: 'fadeIn 0.3s ease',
            maxWidth: '300px'
        });
        
        // Set background color based on type
        const colors = {
            success: '#238636',
            error: '#da3633',
            warning: '#d29922',
            info: '#0969da'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Global functions for HTML onclick handlers
function analyzeCode() {
    app.analyzeCode();
}

function runDemo() {
    app.runDemo();
}

function clearCode() {
    app.clearCode();
}

function showTab(tabName) {
    app.showTab(tabName);
}

function showHistory() {
    app.showHistory();
}

function closeHistory() {
    app.closeHistory();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PRReviewApp();
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);
