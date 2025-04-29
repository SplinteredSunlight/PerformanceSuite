// MCP Server Status Dashboard JavaScript

// Initialize when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load MCP server status
    loadMcpServerStatus();
    
    // Add refresh event listener
    document.getElementById('refresh-btn').addEventListener('click', function() {
        loadMcpServerStatus();
    });
    
    // Initialize server status indicators in header
    initServerStatusIndicators();
    
    // Set up auto-refresh every 30 seconds
    setInterval(loadMcpServerStatus, 30000);
});

// Load MCP server status
function loadMcpServerStatus() {
    const mcpServersContainer = document.getElementById('mcp-servers-container');
    
    // Show loading state
    mcpServersContainer.innerHTML = '<div class="loading-indicator">Loading MCP server status...</div>';
    
    // Fetch MCP server status
    fetch('/api/mcp_servers')
        .then(response => response.json())
        .then(servers => {
            // Clear loading state
            mcpServersContainer.innerHTML = '';
            
            // Create server cards
            servers.forEach(server => {
                const serverCard = createServerCard(server);
                mcpServersContainer.appendChild(serverCard);
            });
            
            // If no servers, show message
            if (servers.length === 0) {
                mcpServersContainer.innerHTML = '<div class="loading-indicator">No MCP servers configured.</div>';
            }
        })
        .catch(error => {
            console.error('Error loading MCP server status:', error);
            mcpServersContainer.innerHTML = '<div class="loading-indicator">Error loading MCP server status. Please try again.</div>';
        });
}

// Create a server card
function createServerCard(server) {
    const card = document.createElement('div');
    card.className = 'mcp-server-card';
    card.dataset.serverId = server.id;
    
    // Create header with name and status
    const header = document.createElement('div');
    header.className = 'mcp-server-header';
    
    const name = document.createElement('div');
    name.className = 'mcp-server-name';
    name.textContent = server.name;
    
    const status = document.createElement('div');
    status.className = `mcp-server-status status-${server.running ? 'running' : 'stopped'}`;
    status.textContent = server.running ? 'Running' : 'Stopped';
    
    header.appendChild(name);
    header.appendChild(status);
    
    // Create description
    const description = document.createElement('div');
    description.className = 'mcp-server-description';
    description.textContent = server.description;
    
    // Create actions
    const actions = document.createElement('div');
    actions.className = 'mcp-server-actions';
    
    const startBtn = document.createElement('button');
    startBtn.className = 'start-btn';
    startBtn.textContent = 'Start';
    startBtn.disabled = server.running;
    startBtn.addEventListener('click', () => performServerAction(server.id, 'start'));
    
    const stopBtn = document.createElement('button');
    stopBtn.className = 'stop-btn';
    stopBtn.textContent = 'Stop';
    stopBtn.disabled = !server.running;
    stopBtn.addEventListener('click', () => performServerAction(server.id, 'stop'));
    
    const restartBtn = document.createElement('button');
    restartBtn.className = 'restart-btn';
    restartBtn.textContent = 'Restart';
    restartBtn.disabled = !server.running;
    restartBtn.addEventListener('click', () => performServerAction(server.id, 'restart'));
    
    actions.appendChild(startBtn);
    actions.appendChild(stopBtn);
    actions.appendChild(restartBtn);
    
    // Add elements to card
    card.appendChild(header);
    card.appendChild(description);
    card.appendChild(actions);
    
    return card;
}

// Perform server action (start, stop, restart)
function performServerAction(serverId, action) {
    // Show loading state
    const serverCard = document.querySelector(`.mcp-server-card[data-server-id="${serverId}"]`);
    const statusElement = serverCard.querySelector('.mcp-server-status');
    const startBtn = serverCard.querySelector('.start-btn');
    const stopBtn = serverCard.querySelector('.stop-btn');
    const restartBtn = serverCard.querySelector('.restart-btn');
    
    // Disable buttons during action
    startBtn.disabled = true;
    stopBtn.disabled = true;
    restartBtn.disabled = true;
    
    // Update status to show action in progress
    statusElement.className = 'mcp-server-status';
    statusElement.textContent = `${action.charAt(0).toUpperCase() + action.slice(1)}ing...`;
    
    // Perform action
    fetch(`/api/mcp_action/${serverId}/${action}`)
        .then(response => response.json())
        .then(result => {
            console.log(`${action} result:`, result);
            
            // Show result message
            showActionMessage(result.message, result.status);
            
            // Refresh server status after a short delay
            setTimeout(() => {
                loadMcpServerStatus();
                
                // Also update the header indicators
                updateServerStatusIndicators();
            }, 1000);
        })
        .catch(error => {
            console.error(`Error ${action}ing server:`, error);
            
            // Show error message
            showActionMessage(`Error ${action}ing server. Please try again.`, 'error');
            
            // Re-enable buttons
            startBtn.disabled = false;
            stopBtn.disabled = false;
            restartBtn.disabled = false;
            
            // Restore status
            checkServerStatus(serverId);
        });
}

// Check server status
function checkServerStatus(serverId) {
    fetch(`/api/mcp_action/${serverId}/status`)
        .then(response => response.json())
        .then(result => {
            // Update server card
            const serverCard = document.querySelector(`.mcp-server-card[data-server-id="${serverId}"]`);
            const statusElement = serverCard.querySelector('.mcp-server-status');
            const startBtn = serverCard.querySelector('.start-btn');
            const stopBtn = serverCard.querySelector('.stop-btn');
            const restartBtn = serverCard.querySelector('.restart-btn');
            
            // Update status
            statusElement.className = `mcp-server-status status-${result.running ? 'running' : 'stopped'}`;
            statusElement.textContent = result.running ? 'Running' : 'Stopped';
            
            // Update buttons
            startBtn.disabled = result.running;
            stopBtn.disabled = !result.running;
            restartBtn.disabled = !result.running;
        })
        .catch(error => {
            console.error('Error checking server status:', error);
        });
}

// Show action message
function showActionMessage(message, status) {
    // Create message element if it doesn't exist
    let messageElement = document.getElementById('action-message');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'action-message';
        messageElement.className = 'action-message';
        document.querySelector('.container').prepend(messageElement);
    }
    
    // Set message and status
    messageElement.textContent = message;
    messageElement.className = `action-message ${status}`;
    
    // Show message
    setTimeout(() => {
        messageElement.classList.add('show');
    }, 10);
    
    // Hide message after 3 seconds
    setTimeout(() => {
        messageElement.classList.remove('show');
    }, 3000);
}

// Initialize server status indicators in header
function initServerStatusIndicators() {
    // Get the server status indicators container
    const serverStatusIndicators = document.getElementById('server-status-indicators');
    
    // Create server status indicators
    fetch('/api/mcp_servers')
        .then(response => response.json())
        .then(servers => {
            // Clear existing indicators
            serverStatusIndicators.innerHTML = '';
            
            // Create indicators for each server
            servers.forEach(server => {
                // Only show dashboard and task_manager in the header
                if (server.id === 'dashboard' || server.id === 'task_manager') {
                    const indicator = createServerStatusIndicator(server);
                    serverStatusIndicators.appendChild(indicator);
                }
            });
        })
        .catch(error => {
            console.error('Error loading server status indicators:', error);
        });
    
    // Set up auto-refresh for server status indicators
    setInterval(updateServerStatusIndicators, 10000); // Update every 10 seconds
}

// Update server status indicators
function updateServerStatusIndicators() {
    fetch('/api/mcp_servers')
        .then(response => response.json())
        .then(servers => {
            servers.forEach(server => {
                // Only update dashboard and task_manager in the header
                if (server.id === 'dashboard' || server.id === 'task_manager') {
                    updateServerStatusIndicator(server);
                }
            });
        })
        .catch(error => {
            console.error('Error updating server status indicators:', error);
        });
}

// Create a server status indicator
function createServerStatusIndicator(server) {
    const indicator = document.createElement('div');
    indicator.className = 'server-status-indicator';
    indicator.dataset.serverId = server.id;
    
    const icon = document.createElement('span');
    icon.className = `server-status-icon ${server.running ? 'running' : 'stopped'}`;
    
    const name = document.createElement('span');
    name.className = 'server-status-name';
    name.textContent = server.id === 'dashboard' ? 'Dashboard' : 'Task Manager';
    
    const tooltip = document.createElement('div');
    tooltip.className = 'server-status-tooltip';
    tooltip.textContent = `${server.name} is ${server.running ? 'running' : 'stopped'}`;
    
    indicator.appendChild(icon);
    indicator.appendChild(name);
    indicator.appendChild(tooltip);
    
    // Add click event to toggle server
    indicator.addEventListener('click', () => {
        const action = server.running ? 'stop' : 'start';
        performServerAction(server.id, action);
    });
    
    return indicator;
}

// Update a server status indicator
function updateServerStatusIndicator(server) {
    const indicator = document.querySelector(`.server-status-indicator[data-server-id="${server.id}"]`);
    if (!indicator) return;
    
    const icon = indicator.querySelector('.server-status-icon');
    const tooltip = indicator.querySelector('.server-status-tooltip');
    
    // Update icon class
    icon.className = `server-status-icon ${server.running ? 'running' : 'stopped'}`;
    
    // Update tooltip text
    tooltip.textContent = `${server.name} is ${server.running ? 'running' : 'stopped'}`;
}