async function logRequest(level) {
    try {
        const response = await fetch(`/log/${level}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: `Тестовое сообщение ${level.toUpperCase()} уровня`,
                timestamp: new Date().toISOString()
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addLogEntry(level, data.message);
        } else {
            addLogEntry('error', `Ошибка: ${data.error}`);
        }
    } catch (error) {
        addLogEntry('error', `Ошибка сети: ${error.message}`);
    }
}

function addLogEntry(level, message) {
    const logsDiv = document.getElementById('logs');

    const emptyDiv = logsDiv.querySelector('.empty-logs');
    if (emptyDiv) {
        emptyDiv.remove();
    }
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${level}`;
    
    const timestamp = new Date().toLocaleTimeString('ru-RU');
    logEntry.innerHTML = `<strong>[${timestamp}]</strong> ${message}`;
    
    logsDiv.insertBefore(logEntry, logsDiv.firstChild);
    
    const entries = logsDiv.querySelectorAll('.log-entry');
    if (entries.length > 50) {
        entries[entries.length - 1].remove();
    }
    
    logsDiv.scrollTop = 0;
}

function clearLogs() {
    const logsDiv = document.getElementById('logs');
    logsDiv.innerHTML = '<div class="empty-logs">Нажмите на кнопки выше, чтобы начать тестирование</div>';
}
