const socket = io();

let config = {
    party_size: 4,
    parties_needed: 2,
    max_players: 8,
    sound_notification: true
};

let currentQueue = {
    players: [],
    count: 0,
    max: 8,
    percentage: 0,
    ready: false
};

document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    setupEventListeners();
    setupSocketListeners();
    
    const playerNameInput = document.getElementById('playerName');
    playerNameInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addPlayer();
        }
    });
});

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        config = await response.json();
        document.getElementById('maxPlayers').textContent = config.max_players;
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

function setupEventListeners() {
    // Any additional event listeners can go here
}

function setupSocketListeners() {
    socket.on('connect', () => {
        updateStatus(true);
    });

    socket.on('disconnect', () => {
        updateStatus(false);
    });

    socket.on('queue_update', (data) => {
        handleQueueUpdate(data);
    });

    socket.on('parties_formed', (data) => {
        handlePartiesFormed(data);
    });
}

function updateStatus(connected) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        indicator.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

async function addPlayer() {
    const input = document.getElementById('playerName');
    const name = input.value.trim();
    
    if (!name) {
        return;
    }
    
    try {
        const response = await fetch('/api/queue/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });
        
        const result = await response.json();
        
        if (result.success) {
            input.value = '';
            input.focus();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error adding player:', error);
        alert('Failed to add player');
    }
}

async function addMultiple(count) {
    const input = document.getElementById('playerName');
    const baseName = input.value.trim();
    
    if (!baseName) {
        alert('Please enter a base name');
        return;
    }
    
    const names = [];
    if (count === 1) {
        names.push(baseName);
    } else {
        for (let i = 1; i <= count; i++) {
            names.push(`${baseName}_${i}`);
        }
    }
    
    try {
        const response = await fetch('/api/queue/add-multiple', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ names })
        });
        
        const result = await response.json();
        
        if (result.success) {
            input.value = '';
            input.focus();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error adding players:', error);
        alert('Failed to add players');
    }
}

async function addMultipleFromText() {
    const textarea = document.getElementById('multipleNames');
    const text = textarea.value.trim();
    
    if (!text) {
        return;
    }
    
    const names = text
        .split(/[\n,;]+/)
        .map(name => name.trim())
        .filter(name => name.length > 0);
    
    if (names.length === 0) {
        alert('No valid names found');
        return;
    }
    
    try {
        const response = await fetch('/api/queue/add-multiple', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ names })
        });
        
        const result = await response.json();
        
        if (result.success) {
            textarea.value = '';
            if (result.skipped.length > 0) {
                alert(`Added ${result.added.length} players. Skipped (already in queue): ${result.skipped.join(', ')}`);
            }
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error adding players:', error);
        alert('Failed to add players');
    }
}

async function removePlayer(name) {
    try {
        const response = await fetch('/api/queue/remove', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name })
        });
        
        const result = await response.json();
        
        if (!result.success) {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error removing player:', error);
        alert('Failed to remove player');
    }
}

async function clearQueue() {
    if (!confirm('Are you sure you want to clear the entire queue?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/queue/clear', {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (!result.success) {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error clearing queue:', error);
        alert('Failed to clear queue');
    }
}

async function finalizeParties() {
    try {
        const response = await fetch('/api/parties/finalize', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('partiesSection').style.display = 'none';
            loadHistory();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error finalizing parties:', error);
        alert('Failed to finalize parties');
    }
}

function handleQueueUpdate(data) {
    if (data.queue) {
        currentQueue = data.queue;
        updateQueueDisplay();
    }
    
    if (data.ready && data.parties) {
        showParties(data.parties);
        playNotification();
    }
}

function handlePartiesFormed(data) {
    if (data.success) {
        loadHistory();
    }
}

function updateQueueDisplay() {
    const queueCount = document.getElementById('queueCount');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const queueList = document.getElementById('queueList');
    
    queueCount.textContent = currentQueue.count;
    progressFill.style.width = `${currentQueue.percentage}%`;
    progressText.textContent = `${Math.round(currentQueue.percentage)}%`;
    
    if (currentQueue.players.length === 0) {
        queueList.innerHTML = '<p class="empty-message">No players in queue yet</p>';
    } else {
        queueList.innerHTML = currentQueue.players
            .map((player, index) => createQueueItemHTML(player, index + 1))
            .join('');
    }
    
    if (currentQueue.ready) {
        const parties = formPartiesFromQueue();
        showParties(parties);
    } else {
        document.getElementById('partiesSection').style.display = 'none';
    }
}

function formPartiesFromQueue() {
    const parties = [];
    const playersToGroup = currentQueue.players.slice(0, config.max_players);
    
    for (let i = 0; i < config.parties_needed; i++) {
        const start = i * config.party_size;
        const end = start + config.party_size;
        parties.push(playersToGroup.slice(start, end));
    }
    
    return parties;
}

function createQueueItemHTML(player, position) {
    const timeAgo = getTimeAgo(new Date(player.joined_at));
    const sourceLabel = player.source === 'log' ? '🤖 Auto' : '✋ Manual';
    
    return `
        <div class="queue-item">
            <div class="player-info">
                <span class="player-number">${position}</span>
                <span class="player-name">${escapeHtml(player.name)}</span>
                <span class="player-source">${sourceLabel}</span>
            </div>
            <div>
                <span class="player-time">${timeAgo}</span>
                <button class="remove-btn" onclick="removePlayer('${escapeHtml(player.name)}')">✕</button>
            </div>
        </div>
    `;
}

function showParties(parties) {
    const partiesSection = document.getElementById('partiesSection');
    const partiesContainer = document.getElementById('partiesContainer');
    
    partiesContainer.innerHTML = parties
        .map((party, index) => createPartyCardHTML(party, index + 1))
        .join('');
    
    partiesSection.style.display = 'block';
    partiesSection.scrollIntoView({ behavior: 'smooth' });
}

function createPartyCardHTML(party, partyNumber) {
    return `
        <div class="party-card">
            <div class="party-title">
                👥 Party ${partyNumber}
            </div>
            ${party.map(player => `
                <div class="party-member">
                    • ${escapeHtml(player.name)}
                </div>
            `).join('')}
        </div>
    `;
}

function copyParties() {
    const parties = formPartiesFromQueue();
    
    let text = '🎮 Quest Group Ready!\n\n';
    parties.forEach((party, index) => {
        text += `Party ${index + 1}:\n`;
        party.forEach(player => {
            text += `• ${player.name}\n`;
        });
        text += '\n';
    });
    
    navigator.clipboard.writeText(text).then(() => {
        alert('Parties copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('Parties copied to clipboard!');
    });
}

async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const history = await response.json();
        displayHistory(history);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(history) {
    const historyList = document.getElementById('historyList');
    
    if (history.length === 0) {
        historyList.innerHTML = '<p class="empty-message">No party history yet</p>';
        return;
    }
    
    historyList.innerHTML = history
        .reverse()
        .map(record => createHistoryItemHTML(record))
        .join('');
}

function createHistoryItemHTML(record) {
    const time = new Date(record.formed_at).toLocaleString();
    
    return `
        <div class="history-item">
            <div class="history-time">📅 ${time}</div>
            <div class="history-parties">
                ${record.parties.map((party, index) => `
                    <div class="history-party">
                        <div class="history-party-title">Party ${index + 1}</div>
                        ${party.map(p => `<div>• ${escapeHtml(p.name)}</div>`).join('')}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function playNotification() {
    if (!config.sound_notification) {
        return;
    }
    
    const audio = document.getElementById('notificationSound');
    audio.play().catch(err => {
        console.log('Could not play notification sound:', err);
    });
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 10) return 'just now';
    if (seconds < 60) return `${seconds}s ago`;
    
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

setInterval(() => {
    updateQueueDisplay();
}, 30000);

loadHistory();

