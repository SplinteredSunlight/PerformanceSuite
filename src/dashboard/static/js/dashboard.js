// Dashboard JavaScript

// Global variables
let statusChart = null;
let selectedTaskId = null;
let allTasks = [];

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Load initial data
    loadDashboardData();
    
    // Set up event listeners
    document.getElementById('refresh-btn').addEventListener('click', loadDashboardData);
    
    // Initialize resizable elements
    initResizable();
    
    // Update last updated timestamp
    updateTimestamp();
    
    // Apply dark theme to charts
    Chart.defaults.color = '#e0e0e0';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    
    // Initialize system diagram interactions
    initSystemDiagram();
});

// Initialize resizable elements
function initResizable() {
    const resizableElements = document.querySelectorAll('.resizable');
    
    resizableElements.forEach(element => {
        const resizeHandle = element.querySelector('.resize-handle-se');
        
        if (resizeHandle) {
            resizeHandle.addEventListener('mousedown', function(e) {
                e.preventDefault();
                
                const startX = e.clientX;
                const startY = e.clientY;
                const startWidth = element.offsetWidth;
                const startHeight = element.offsetHeight;
                
                function resize(e) {
                    const newWidth = startWidth + e.clientX - startX;
                    const newHeight = startHeight + e.clientY - startY;
                    
                    element.style.width = newWidth + 'px';
                    element.style.height = newHeight + 'px';
                    
                    // If this is the overview card, update the chart
                    if (element.classList.contains('overview') && statusChart) {
                        statusChart.resize();
                    }
                }
                
                function stopResize() {
                    window.removeEventListener('mousemove', resize);
                    window.removeEventListener('mouseup', stopResize);
                }
                
                window.addEventListener('mousemove', resize);
                window.addEventListener('mouseup', stopResize);
            });
        }
    });
}

// Initialize system diagram interactions
function initSystemDiagram() {
    const diagramComponents = document.querySelectorAll('.diagram-component');
    const tooltip = document.getElementById('diagram-tooltip');
    
    // Component descriptions
    const componentDetails = {
        'Audio Analysis': {
            description: 'Processes real-time audio input and extracts musical features like tempo, key, and chord progressions.',
            tasks: ['MB-004', 'MB-005'],
            technologies: 'Python, NumPy, librosa, PyAudio',
            status: 'Not Started'
        },
        'Agent System': {
            description: 'Coordinates virtual musicians that respond to audio analysis data and generate appropriate musical responses.',
            tasks: ['MB-002', 'MB-006', 'MB-007'],
            technologies: 'Python, Multi-agent systems, State machines',
            status: 'Not Started'
        },
        'MIDI Generation': {
            description: 'Creates MIDI output based on agent decisions, generating musical parts for virtual instruments.',
            tasks: ['MB-008'],
            technologies: 'Python, MIDI libraries, Music theory algorithms',
            status: 'Not Started'
        },
        'Rendering': {
            description: 'Visualizes the virtual band members and their performances in a 3D environment.',
            tasks: ['MB-003', 'MB-010', 'MB-011'],
            technologies: 'Game engine (Unity/Godot/Unreal), 3D modeling, Animation',
            status: 'Not Started'
        },
        'Infrastructure': {
            description: 'Hardware and network setup that enables communication between audio processing and rendering machines.',
            tasks: ['MB-012', 'MB-013', 'MB-014', 'MB-015', 'MB-016', 'MB-017', 'MB-018'],
            technologies: 'Mac Mini M4, Mac Studio M4, Ethernet networking, Python',
            status: '3 Completed, 4 Not Started'
        },
        'OSC Communication': {
            description: 'Handles low-latency messaging between the audio processing machine and the rendering machine.',
            tasks: ['MB-009'],
            technologies: 'Open Sound Control (OSC), UDP networking, Python',
            status: 'Not Started'
        }
    };
    
    // Add mouse events to diagram components
    diagramComponents.forEach(component => {
        component.addEventListener('mouseenter', function(e) {
            const componentName = this.getAttribute('data-component') || this.id;
            const details = componentDetails[componentName];
            
            if (details) {
                // Create tooltip content
                let content = `<h3>${componentName}</h3>`;
                content += `<p>${details.description}</p>`;
                content += `<p><strong>Status:</strong> ${details.status}</p>`;
                content += `<p><strong>Technologies:</strong> ${details.technologies}</p>`;
                content += `<p><strong>Related Tasks:</strong> ${details.tasks.join(', ')}</p>`;
                
                tooltip.innerHTML = content;
                
                // Position tooltip near the mouse
                const rect = this.getBoundingClientRect();
                const tooltipX = rect.left + window.scrollX + rect.width / 2;
                const tooltipY = rect.top + window.scrollY - 10;
                
                tooltip.style.left = `${tooltipX}px`;
                tooltip.style.top = `${tooltipY}px`;
                tooltip.style.transform = 'translate(-50%, -100%)';
                tooltip.classList.add('visible');
            }
        });
        
        component.addEventListener('mouseleave', function() {
            tooltip.classList.remove('visible');
        });
        
        component.addEventListener('click', function() {
            const componentName = this.getAttribute('data-component') || this.id;
            const details = componentDetails[componentName];
            
            if (details && details.tasks.length > 0) {
                // Find the first task in the list
                const taskId = details.tasks[0];
                const task = allTasks.find(t => t.id === taskId);
                
                if (task) {
                    showTaskDetails(task.id);
                }
            }
        });
    });
}

// Load all dashboard data
function loadDashboardData() {
    // Show loading state
    showLoading();
    
    // Fetch tasks, statistics, and component data
    Promise.all([
        fetch('/api/tasks').then(response => response.json()),
        fetch('/api/statistics').then(response => response.json()),
        fetch('/api/components').then(response => response.json())
    ])
    .then(([tasks, statistics, components]) => {
        // Filter out MB-001 if it exists
        tasks = tasks.filter(task => task.id !== 'MB-001');
        
        // Store all tasks globally
        allTasks = tasks;
        
        // Update the dashboard sections
        updateOverview(statistics);
        updateTaskBoard(tasks);
        updateComponentProgress(components);
        updateGanttChart(tasks);
        
        // Hide loading state
        hideLoading();
    })
    .catch(error => {
        console.error('Error loading dashboard data:', error);
        hideLoading();
        showError('Failed to load dashboard data. Please try again.');
    });
}

// Update the overview section with statistics
function updateOverview(statistics) {
    // Update statistics
    document.getElementById('total-tasks').textContent = statistics.total_tasks;
    document.getElementById('completion-rate').textContent = statistics.completion_rate;
    
    // Update chart
    updateStatusChart(statistics);
}

// Create or update the status chart
function updateStatusChart(statistics) {
    const ctx = document.getElementById('status-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (statusChart) {
        statusChart.destroy();
    }
    
    // Create new chart
    statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Not Started', 'In Progress', 'Blocked', 'Completed'],
            datasets: [{
                data: [
                    statistics.not_started,
                    statistics.in_progress,
                    statistics.blocked,
                    statistics.completed
                ],
                backgroundColor: [
                    '#3498db',  // Blue for Not Started
                    '#f39c12',  // Orange for In Progress
                    '#e74c3c',  // Red for Blocked
                    '#2ecc71'   // Green for Completed
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%', // Adjusted cutout percentage for better appearance
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#e0e0e0',
                        font: {
                            size: 11
                        },
                        padding: 15 // Increased padding for better spacing
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 10
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    });
}

// Update the task board with tasks
function updateTaskBoard(tasks) {
    // Clear existing tasks
    document.getElementById('not-started-tasks').innerHTML = '';
    document.getElementById('in-progress-tasks').innerHTML = '';
    document.getElementById('blocked-tasks').innerHTML = '';
    document.getElementById('completed-tasks').innerHTML = '';
    
    // Group tasks by status
    const notStarted = tasks.filter(task => task.status === 'Not Started');
    const inProgress = tasks.filter(task => task.status === 'In Progress');
    const blocked = tasks.filter(task => task.status === 'Blocked');
    const completed = tasks.filter(task => task.status === 'Completed');
    
    // Render tasks in each column
    notStarted.forEach(task => {
        document.getElementById('not-started-tasks').appendChild(createTaskCard(task));
    });
    
    inProgress.forEach(task => {
        document.getElementById('in-progress-tasks').appendChild(createTaskCard(task));
    });
    
    blocked.forEach(task => {
        document.getElementById('blocked-tasks').appendChild(createTaskCard(task));
    });
    
    completed.forEach(task => {
        document.getElementById('completed-tasks').appendChild(createTaskCard(task));
    });
    
    // Ensure the board columns are evenly sized
    const boardColumns = document.querySelectorAll('.board-column');
    const boardContainer = document.querySelector('.board-container');
    const availableWidth = boardContainer.offsetWidth;
    const columnWidth = Math.floor(availableWidth / boardColumns.length) - 20; // 20px for gap
    
    boardColumns.forEach(column => {
        column.style.minWidth = `${columnWidth}px`;
        column.style.maxWidth = `${columnWidth}px`;
    });
}

// Create a task card element
function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.dataset.taskId = task.id;
    
    // Add border color based on component
    let borderColor = 'var(--border-blue)';
    let textColor = 'var(--text-blue)';
    
    if (task.component === 'Rendering') {
        borderColor = 'var(--border-purple)';
        textColor = 'var(--text-purple)';
    } else if (task.component === 'Infrastructure') {
        borderColor = 'var(--border-orange)';
        textColor = 'var(--text-orange)';
    } else if (task.component === 'Agent System') {
        borderColor = 'var(--border-blue)';
        textColor = 'var(--text-blue)';
    } else if (task.component === 'Audio Analysis') {
        borderColor = 'var(--border-purple)';
        textColor = 'var(--text-purple)';
    } else if (task.component === 'MIDI Generation') {
        borderColor = 'var(--border-green)';
        textColor = 'var(--text-green)';
    } else if (task.component === 'OSC Communication') {
        borderColor = 'var(--warning-color)';
        textColor = 'var(--warning-color)';
    }
    
    card.style.borderLeftColor = borderColor;
    
    // Add priority class
    const priorityClass = `priority-${task.priority.toLowerCase()}`;
    
    // Truncate title if too long
    const title = task.title.length > 40 ? task.title.substring(0, 37) + '...' : task.title;
    
    card.innerHTML = `
        <h4 style="color: ${textColor}">${title}</h4>
        <div class="task-id">${task.id}</div>
        <div class="task-meta">
            <span class="task-component">${task.component}</span>
            <span class="task-priority ${priorityClass}">${task.priority}</span>
        </div>
    `;
    
    // Add click event to show task details
    card.addEventListener('click', () => {
        showTaskDetails(task.id);
    });
    
    return card;
}

// Update the component progress section
function updateComponentProgress(components) {
    const componentGrid = document.getElementById('component-grid');
    componentGrid.innerHTML = '';
    
    // Process each component
    Object.entries(components).forEach(([componentName, tasks]) => {
        // Skip if no tasks
        if (tasks.length === 0) return;
        
        // Calculate completion percentage
        const totalTasks = tasks.length;
        const completedTasks = tasks.filter(task => task.status === 'Completed').length;
        const completionPercentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
        
        // Determine border color
        let borderColor = 'var(--border-blue)';
        let textColor = 'var(--text-blue)';
        if (componentName === 'Rendering') {
            borderColor = 'var(--border-purple)';
            textColor = 'var(--text-purple)';
        } else if (componentName === 'Infrastructure') {
            borderColor = 'var(--border-orange)';
            textColor = 'var(--text-orange)';
        } else if (componentName === 'MIDI Generation') {
            borderColor = 'var(--border-green)';
            textColor = 'var(--text-green)';
        } else if (componentName === 'OSC Communication') {
            borderColor = 'var(--warning-color)';
            textColor = 'var(--warning-color)';
        }
        
        // Create component card
        const componentCard = document.createElement('div');
        componentCard.className = 'component-card';
        componentCard.style.borderLeft = `4px solid ${borderColor}`;
        
        componentCard.innerHTML = `
            <h3 style="color: ${textColor}">${componentName}</h3>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${completionPercentage}%; background-color: ${borderColor}"></div>
            </div>
            <div class="component-stats">
                <span>${completedTasks}/${totalTasks} tasks completed</span>
                <span>${completionPercentage}%</span>
            </div>
        `;
        
        componentGrid.appendChild(componentCard);
    });
}

// Update the Gantt chart
function updateGanttChart(tasks) {
    const ganttChart = document.getElementById('gantt-chart');
    const ganttHeader = document.getElementById('gantt-header');
    
    // Clear existing content
    ganttChart.innerHTML = '';
    ganttHeader.innerHTML = '';
    
    // Sort tasks by ID (numeric part)
    const sortedTasks = [...tasks].sort((a, b) => {
        const idA = parseInt(a.id.replace('MB-', ''));
        const idB = parseInt(b.id.replace('MB-', ''));
        return idA - idB;
    });
    
    // Create tick marks instead of month headers
    const ticksContainer = document.createElement('div');
    ticksContainer.className = 'gantt-ticks';
    
    // Add 10 tick marks
    for (let i = 0; i < 10; i++) {
        const tick = document.createElement('div');
        tick.className = 'gantt-tick';
        ticksContainer.appendChild(tick);
    }
    
    ganttHeader.appendChild(ticksContainer);
    
    // Add tasks to the Gantt chart
    sortedTasks.forEach(task => {
        const row = document.createElement('div');
        row.className = 'gantt-row';
        row.dataset.taskId = task.id;
        
        // Determine color based on component - match task card colors
        let barColor = 'var(--border-blue)';
        let textColor = 'var(--text-blue)';
        
        if (task.component === 'Rendering') {
            barColor = 'var(--border-purple)';
            textColor = 'var(--text-purple)';
        } else if (task.component === 'Infrastructure') {
            barColor = 'var(--border-orange)';
            textColor = 'var(--text-orange)';
        } else if (task.component === 'Audio Analysis') {
            barColor = 'var(--border-purple)';
            textColor = 'var(--text-purple)';
        } else if (task.component === 'MIDI Generation') {
            barColor = 'var(--border-green)';
            textColor = 'var(--text-green)';
        } else if (task.component === 'OSC Communication') {
            barColor = 'var(--warning-color)';
            textColor = 'var(--warning-color)';
        }
        
        // Create label
        const label = document.createElement('div');
        label.className = 'gantt-label';
        label.style.color = textColor;
        label.textContent = task.id + ': ' + task.title;
        row.appendChild(label);
        
        // Create timeline
        const timeline = document.createElement('div');
        timeline.className = 'gantt-timeline';
        
        // Create bar - position based on task ID and status
        const bar = document.createElement('div');
        bar.className = 'gantt-bar';
        bar.dataset.taskId = task.id;
        bar.style.backgroundColor = barColor;
        
        // Set bar position and width based on task status
        let startPercent = 0;
        let widthPercent = 0;
        
        if (task.status === 'Completed') {
            // Completed tasks are in the past
            startPercent = 5;
            widthPercent = 15;
        } else if (task.status === 'In Progress') {
            // In progress tasks start in the past and extend to the future
            startPercent = 15;
            widthPercent = 20;
        } else {
            // Not started tasks are in the future
            const idNum = parseInt(task.id.replace('MB-', ''));
            startPercent = 20 + (idNum * 2); // Space them out based on ID
            widthPercent = 15;
        }
        
        bar.style.left = startPercent + '%';
        bar.style.width = widthPercent + '%';
        
        timeline.appendChild(bar);
        row.appendChild(timeline);
        
        ganttChart.appendChild(row);
    });
}

// Show task details
function showTaskDetails(taskId) {
    // Find the task
    const task = allTasks.find(t => t.id === taskId);
    if (!task) return;
    
    // Update selected task
    selectedTaskId = taskId;
    
    // Highlight selected task card
    document.querySelectorAll('.task-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.task-card[data-task-id="${taskId}"]`)?.classList.add('selected');
    
    // Highlight selected Gantt bar
    document.querySelectorAll('.gantt-bar').forEach(bar => {
        bar.classList.remove('selected');
    });
    document.querySelector(`.gantt-bar[data-task-id="${taskId}"]`)?.classList.add('selected');
    
    // Determine text color based on component
    let textColor = 'var(--text-blue)';
    if (task.component === 'Rendering') {
        textColor = 'var(--text-purple)';
    } else if (task.component === 'Infrastructure') {
        textColor = 'var(--text-orange)';
    } else if (task.component === 'MIDI Generation') {
        textColor = 'var(--text-green)';
    } else if (task.component === 'OSC Communication') {
        textColor = 'var(--warning-color)';
    }
    
    // Update task details section
    const detailsContent = document.getElementById('task-details-content');
    detailsContent.innerHTML = `
        <div class="task-details-grid">
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Title</div>
                <div class="detail-value">${task.title}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">ID</div>
                <div class="detail-value">${task.id}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Status</div>
                <div class="detail-value">${task.status}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Priority</div>
                <div class="detail-value">${task.priority}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Component</div>
                <div class="detail-value">${task.component}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Effort</div>
                <div class="detail-value">${task.effort}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Description</div>
                <div class="detail-value">${task.description}</div>
            </div>
            ${task.dependencies ? `
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Dependencies</div>
                <div class="detail-value">${task.dependencies}</div>
            </div>
            ` : ''}
            ${task.notes ? `
            <div class="detail-item">
                <div class="detail-label" style="color: ${textColor}">Notes</div>
                <div class="detail-value">${task.notes}</div>
            </div>
            ` : ''}
        </div>
    `;
    
    // Scroll to details section
    document.getElementById('task-details-section').scrollIntoView({ behavior: 'smooth' });
}

// Update the last updated timestamp
function updateTimestamp() {
    const now = new Date();
    document.getElementById('last-updated').textContent = now.toLocaleString();
}

// Show loading state
function showLoading() {
    // Add loading class to body
    document.body.classList.add('loading');
    
    // Disable refresh button
    document.getElementById('refresh-btn').disabled = true;
}

// Hide loading state
function hideLoading() {
    // Remove loading class from body
    document.body.classList.remove('loading');
    
    // Enable refresh button
    document.getElementById('refresh-btn').disabled = false;
}

// Show error message
function showError(message) {
    // Create error element if it doesn't exist
    let errorElement = document.getElementById('error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = 'error-message';
        errorElement.className = 'error-message';
        document.querySelector('.container').prepend(errorElement);
    }
    
    // Set error message
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}
