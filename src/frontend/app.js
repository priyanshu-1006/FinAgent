// FinAgent AI - Frontend Application
// Modern, fast, and feature-rich UI with voice control

// ===== Global State =====
const state = {
    ws: null,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    currentApprovalId: null,
    sessionStartTime: null,
    stats: {
        tasksExecuted: 0,
        visionCalls: 0,
        approvalsNeeded: 0
    },
    isVoiceEnabled: true,
    recognition: null,
    zoomLevel: 1
};

// ===== Initialization =====
document.addEventListener('DOMContentLoaded', () => {
    initializeWebSocket();
    initializeVoiceControl();
    initializeTheme();
    loadSettings();
    startSessionTimer();
});

// ===== WebSocket Connection =====
function initializeWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    showLoading('Connecting to FinAgent...');
    
    state.ws = new WebSocket(wsUrl);
    
    state.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        hideLoading();
        updateAgentStatus('online', 'Connected');
        showToast('Connected to FinAgent', 'success');
        state.reconnectAttempts = 0;
    };
    
    state.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleMessage(message);
    };
    
    state.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        updateAgentStatus('error', 'Connection Error');
    };
    
    state.ws.onclose = () => {
        console.log('🔌 WebSocket closed');
        updateAgentStatus('offline', 'Disconnected');
        attemptReconnect();
    };
}

function attemptReconnect() {
    if (state.reconnectAttempts < state.maxReconnectAttempts) {
        state.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, state.reconnectAttempts), 10000);
        console.log(`🔄 Reconnecting in ${delay/1000}s... (Attempt ${state.reconnectAttempts})`);
        setTimeout(initializeWebSocket, delay);
    } else {
        showToast('Failed to connect. Please refresh the page.', 'error');
    }
}

// ===== Message Handling =====
function handleMessage(message) {
    const { type, data, message: text, timestamp } = message;
    
    switch (type) {
        case 'status':
            addActivity('info', text || 'Status update', timestamp);
            addLog('info', text || 'Status update');
            break;
            
        case 'screenshot':
            updateBrowserScreenshot(data);
            break;
            
        case 'approval_request':
            showApprovalModal(data);
            state.stats.approvalsNeeded++;
            updateStats();
            break;
            
        case 'task_update':
            handleTaskUpdate(data);
            break;
            
        case 'error':
            addActivity('error', text || 'An error occurred', timestamp);
            addLog('error', text || 'Error');
            showToast(text || 'An error occurred', 'error');
            break;
            
        case 'success':
            addActivity('success', text || 'Operation completed', timestamp);
            addLog('success', text || 'Success');
            showToast(text || 'Success', 'success');
            state.stats.tasksExecuted++;
            updateStats();
            break;
            
        case 'vision_call':
            state.stats.visionCalls++;
            updateStats();
            break;
    }
}

function handleTaskUpdate(task) {
    const { name, status, step, steps, message } = task;
    
    if (status === 'in_progress') {
        addActivity('info', `🔄 ${name} - Step ${step}/${steps}: ${message}`, new Date().toISOString());
    } else if (status === 'completed') {
        addActivity('success', `✅ ${name} completed`, new Date().toISOString());
    } else if (status === 'failed') {
        addActivity('error', `❌ ${name} failed: ${message}`, new Date().toISOString());
    }
}

// ===== Commands =====
async function sendCommand() {
    const input = document.getElementById('commandInput');
    const command = input.value.trim();
    
    if (!command) return;
    
    try {
        showLoading(`Executing: ${command}`);
        addActivity('info', `▶️ Command: ${command}`, new Date().toISOString());
        addLog('info', `> ${command}`);
        
        const response = await fetch('/command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ command })
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.status === 'success') {
            input.value = '';
            showToast('Command sent successfully', 'success');
        } else {
            showToast(result.message || 'Command failed', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Error sending command:', error);
        showToast('Failed to send command', 'error');
    }
}

function quickCommand(command) {
    document.getElementById('commandInput').value = command;
    sendCommand();
}

function handleCommandKeypress(event) {
    if (event.key === 'Enter') {
        sendCommand();
    }
}

// ===== Voice Control =====
function initializeVoiceControl() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('Speech recognition not supported');
        document.getElementById('voiceToggle').style.display = 'none';
        document.getElementById('voiceCmdBtn').style.display = 'none';
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    state.recognition = new SpeechRecognition();
    
    state.recognition.continuous = false;
    state.recognition.interimResults = false;
    state.recognition.lang = 'en-US';
    
    state.recognition.onstart = () => {
        document.getElementById('voiceIndicator').classList.remove('hidden');
        document.getElementById('voiceStatus').textContent = 'Listening...';
    };
    
    state.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('commandInput').value = transcript;
        document.getElementById('voiceStatus').textContent = `Heard: "${transcript}"`;
        
        setTimeout(() => {
            document.getElementById('voiceIndicator').classList.add('hidden');
            sendCommand();
        }, 1000);
    };
    
    state.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        document.getElementById('voiceIndicator').classList.add('hidden');
        showToast('Voice recognition failed', 'error');
    };
    
    state.recognition.onend = () => {
        setTimeout(() => {
            document.getElementById('voiceIndicator').classList.add('hidden');
        }, 500);
    };
}

function startVoiceCommand() {
    if (!state.recognition || !state.isVoiceEnabled) return;
    
    try {
        state.recognition.start();
    } catch (error) {
        console.error('Failed to start voice recognition:', error);
    }
}

function stopVoiceCommand() {
    if (!state.recognition) return;
    
    try {
        state.recognition.stop();
    } catch (error) {
        console.error('Failed to stop voice recognition:', error);
    }
}

// ===== Approval Modal =====
function showApprovalModal(approvalRequest) {
    state.currentApprovalId = approvalRequest.id;
    
    document.getElementById('approvalMessage').textContent = approvalRequest.reason;
    document.getElementById('approvalAction').textContent = approvalRequest.action;
    
    const riskBadge = document.getElementById('approvalRisk');
    riskBadge.textContent = approvalRequest.risk_level;
    riskBadge.className = 'badge';
    
    if (approvalRequest.risk_level === 'high') {
        riskBadge.style.background = 'var(--error)';
    } else if (approvalRequest.risk_level === 'medium') {
        riskBadge.style.background = 'var(--warning)';
    } else {
        riskBadge.style.background = 'var(--success)';
    }
    
    document.getElementById('approvalModal').classList.add('active');
}

async function grantApproval() {
    if (!state.currentApprovalId) return;
    
    try {
        await fetch('/approve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                request_id: state.currentApprovalId,
                approved: true
            })
        });
        
        document.getElementById('approvalModal').classList.remove('active');
        showToast('Action approved', 'success');
        state.stats.approvalsNeeded--;
        updateStats();
    } catch (error) {
        console.error('Error approving action:', error);
        showToast('Failed to approve action', 'error');
    }
}

async function denyApproval() {
    if (!state.currentApprovalId) return;
    
    try {
        await fetch('/approve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                request_id: state.currentApprovalId,
                approved: false
            })
        });
        
        document.getElementById('approvalModal').classList.remove('active');
        showToast('Action denied', 'warning');
        state.stats.approvalsNeeded--;
        updateStats();
    } catch (error) {
        console.error('Error denying action:', error);
        showToast('Failed to deny action', 'error');
    }
}

// ===== UI Updates =====
function updateAgentStatus(status, text) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('agentStatusText');
    
    statusText.textContent = text;
    
    if (status === 'online') {
        statusDot.style.background = 'var(--success)';
    } else if (status === 'error') {
        statusDot.style.background = 'var(--error)';
    } else {
        statusDot.style.background = 'var(--text-muted)';
    }
}

function updateBrowserScreenshot(base64Data) {
    const img = document.getElementById('browserScreenshot');
    img.src = `data:image/png;base64,${base64Data}`;
}

function updateStats() {
    document.getElementById('tasksExecuted').textContent = state.stats.tasksExecuted;
    document.getElementById('visionCalls').textContent = state.stats.visionCalls;
    document.getElementById('approvalsNeeded').textContent = state.stats.approvalsNeeded;
}

function addActivity(type, message, timestamp) {
    const feed = document.getElementById('activityFeed');
    const time = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
    
    const iconMap = {
        info: 'fa-info-circle',
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-times-circle'
    };
    
    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `
        <div class="activity-icon ${type}">
            <i class="fas ${iconMap[type] || 'fa-circle'}"></i>
        </div>
        <div class="activity-content">
            <strong>${message}</strong>
            <div class="activity-time">${time}</div>
        </div>
    `;
    
    feed.insertBefore(item, feed.firstChild);
    
    // Keep only last 50 items for performance
    while (feed.children.length > 50) {
        feed.removeChild(feed.lastChild);
    }
}

function addLog(level, message) {
    const console = document.getElementById('logConsole');
    const time = new Date().toLocaleTimeString();
    
    const entry = document.createElement('div');
    entry.className = `log-entry ${level}`;
    entry.textContent = `[${time}] ${message}`;
    
    console.appendChild(entry);
    console.scrollTop = console.scrollHeight;
    
    // Keep only last 200 logs for performance
    while (console.children.length > 200) {
        console.removeChild(console.firstChild);
    }
}

function clearLogs() {
    document.getElementById('logConsole').innerHTML = '';
    showToast('Logs cleared', 'info');
}

// ===== Navigation =====
function switchTab(tabName) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.closest('.nav-item').classList.add('active');
    
    // Update tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
    
    // Update header
    const titles = {
        dashboard: 'Dashboard',
        browser: 'Browser View',
        history: 'Command History',
        logs: 'System Logs',
        settings: 'Settings'
    };
    document.getElementById('pageTitle').textContent = titles[tabName] || tabName;
    document.getElementById('breadcrumbText').textContent = titles[tabName] || tabName;
}

// ===== Browser Controls =====
function refreshBrowser() {
    showLoading('Refreshing browser...');
    setTimeout(() => {
        hideLoading();
        showToast('Browser refreshed', 'info');
    }, 1000);
}

function zoomIn() {
    state.zoomLevel = Math.min(state.zoomLevel + 0.1, 2);
    document.getElementById('browserScreenshot').style.transform = `scale(${state.zoomLevel})`;
}

function zoomOut() {
    state.zoomLevel = Math.max(state.zoomLevel - 0.1, 0.5);
    document.getElementById('browserScreenshot').style.transform = `scale(${state.zoomLevel})`;
}

// ===== Loading Overlay =====
function showLoading(text = 'Processing...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// ===== Toast Notifications =====
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const iconMap = {
        info: 'fa-info-circle',
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error: 'fa-times-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${iconMap[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// ===== Theme Toggle =====
function initializeTheme() {
    const themeBtn = document.getElementById('themeToggle');
    themeBtn.addEventListener('click', () => {
        // Theme toggle implementation
        showToast('Theme toggle coming soon!', 'info');
    });
}

// ===== Settings =====
function loadSettings() {
    const settings = {
        autoApprove: localStorage.getItem('autoApprove') === 'true',
        voiceEnabled: localStorage.getItem('voiceEnabled') !== 'false',
        autoRefresh: localStorage.getItem('autoRefresh') === 'true',
        performanceMode: localStorage.getItem('performanceMode') === 'true'
    };
    
    document.getElementById('autoApprove').checked = settings.autoApprove;
    document.getElementById('voiceEnabled').checked = settings.voiceEnabled;
    document.getElementById('autoRefresh').checked = settings.autoRefresh;
    document.getElementById('performanceMode').checked = settings.performanceMode;
    
    state.isVoiceEnabled = settings.voiceEnabled;
    
    // Add event listeners
    document.getElementById('autoApprove').addEventListener('change', (e) => {
        localStorage.setItem('autoApprove', e.target.checked);
        showToast('Auto-approve ' + (e.target.checked ? 'enabled' : 'disabled'), 'info');
    });
    
    document.getElementById('voiceEnabled').addEventListener('change', (e) => {
        localStorage.setItem('voiceEnabled', e.target.checked);
        state.isVoiceEnabled = e.target.checked;
        showToast('Voice control ' + (e.target.checked ? 'enabled' : 'disabled'), 'info');
    });
    
    document.getElementById('autoRefresh').addEventListener('change', (e) => {
        localStorage.setItem('autoRefresh', e.target.checked);
        showToast('Auto-refresh ' + (e.target.checked ? 'enabled' : 'disabled'), 'info');
    });
    
    document.getElementById('performanceMode').addEventListener('change', (e) => {
        localStorage.setItem('performanceMode', e.target.checked);
        document.body.classList.toggle('performance-mode', e.target.checked);
        showToast('Performance mode ' + (e.target.checked ? 'enabled' : 'disabled'), 'info');
    });
}

// ===== Session Timer =====
function startSessionTimer() {
    state.sessionStartTime = Date.now();
    
    setInterval(() => {
        const elapsed = Date.now() - state.sessionStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        document.getElementById('sessionTime').textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

// ===== Notification Badge =====
setInterval(() => {
    fetch('/status')
        .then(res => res.json())
        .then(data => {
            document.getElementById('notifBadge').textContent = data.pending_approvals?.length || 0;
        })
        .catch(() => {});
}, 5000);

// ===== Keyboard Shortcuts =====
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: Focus command input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('commandInput').focus();
    }
    
    // Escape: Close modals
    if (e.key === 'Escape') {
        document.getElementById('approvalModal').classList.remove('active');
    }
});

console.log('🤖 FinAgent UI loaded - Press Ctrl+K to focus command input');
