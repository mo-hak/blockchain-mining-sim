// Configuration management
let currentConfig = {};
let isSimulationRunning = false;

// DOM elements
const runButton = document.getElementById('runSimulation');
const resetButton = document.getElementById('resetConfig');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const successRateSpan = document.getElementById('successRate');
const loadingMessage = document.getElementById('loadingMessage');
const resultsContent = document.getElementById('resultsContent');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDefaultConfig();
    setupEventListeners();
});

// Load default configuration
async function loadDefaultConfig() {
    try {
        const response = await fetch('/api/config/default');
        const config = await response.json();
        currentConfig = config;
        updateFormWithConfig(config);
    } catch (error) {
        console.error('Error loading default config:', error);
    }
}

// Update form inputs with configuration
function updateFormWithConfig(config) {
    document.getElementById('num_miners').value = config.num_miners;
    document.getElementById('num_tasks').value = config.num_tasks;
    document.getElementById('reward_multiplier').value = config.reward_multiplier;
    document.getElementById('verifier_reward_multiplier').value = config.verifier_reward_multiplier;
    document.getElementById('renewable_energy_alpha').value = config.renewable_energy_alpha;
    document.getElementById('byzantine_threshold').value = config.byzantine_threshold;
    document.getElementById('byzantine_error_rate').value = config.byzantine_error_rate;
    document.getElementById('input_size_min').value = config.input_size_min;
    document.getElementById('input_size_max').value = config.input_size_max;
    document.getElementById('max_byzantine_miners').value = config.max_byzantine_miners;
    document.getElementById('fault_tolerance_enabled').checked = config.fault_tolerance_enabled;
}

// Get configuration from form
function getConfigFromForm() {
    return {
        num_miners: parseInt(document.getElementById('num_miners').value),
        num_tasks: parseInt(document.getElementById('num_tasks').value),
        reward_multiplier: parseFloat(document.getElementById('reward_multiplier').value),
        verifier_reward_multiplier: parseFloat(document.getElementById('verifier_reward_multiplier').value),
        renewable_energy_alpha: document.getElementById('renewable_energy_alpha').value,  // 'random' or numeric string
        byzantine_threshold: parseFloat(document.getElementById('byzantine_threshold').value),
        byzantine_error_rate: parseFloat(document.getElementById('byzantine_error_rate').value),
        input_size_min: parseInt(document.getElementById('input_size_min').value),
        input_size_max: parseInt(document.getElementById('input_size_max').value),
        max_byzantine_miners: parseInt(document.getElementById('max_byzantine_miners').value),
        fault_tolerance_enabled: document.getElementById('fault_tolerance_enabled').checked
    };
}

// Setup event listeners
function setupEventListeners() {
    runButton.addEventListener('click', runSimulation);
    resetButton.addEventListener('click', () => {
        loadDefaultConfig();
    });
}

// Run simulation
async function runSimulation() {
    if (isSimulationRunning) return;

    // Validate configuration
    const config = getConfigFromForm();
    if (config.input_size_min >= config.input_size_max) {
        alert('Min input size must be less than max input size');
        return;
    }

    isSimulationRunning = true;
    runButton.disabled = true;
    runButton.innerHTML = '<span class="spinner"></span> Running...';

    // Show progress section
    progressSection.style.display = 'block';
    progressBar.style.width = '0%';
    progressText.textContent = `0 / ${config.num_tasks} tasks completed`;
    successRateSpan.textContent = 'Success Rate: 0%';

    // Hide results
    resultsContent.style.display = 'none';
    loadingMessage.style.display = 'block';
    loadingMessage.textContent = 'Running simulation...';

    try {
        // Use synchronous endpoint for simplicity
        const response = await fetch('/api/simulate/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });

        if (!response.ok) {
            throw new Error('Simulation failed');
        }

        const result = await response.json();
        
        // Update progress to 100%
        updateProgress(result.summary.total_tasks, result.summary.total_tasks, result.summary.success_rate);
        
        // Display results
        displayResults(result);

    } catch (error) {
        console.error('Error running simulation:', error);
        alert('Error running simulation. Please check the console for details.');
        loadingMessage.textContent = 'Error running simulation';
    } finally {
        isSimulationRunning = false;
        runButton.disabled = false;
        runButton.textContent = 'Run Simulation';
    }
}

// Update progress display
function updateProgress(completed, total, successRate) {
    const percentage = (completed / total) * 100;
    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${completed} / ${total} tasks completed`;
    successRateSpan.textContent = `Success Rate: ${(successRate * 100).toFixed(2)}%`;
}

// Display simulation results
function displayResults(result) {
    loadingMessage.style.display = 'none';
    resultsContent.style.display = 'block';

    // Update summary statistics
    document.getElementById('statTotalTasks').textContent = result.summary.total_tasks;
    document.getElementById('statSuccessfulTasks').textContent = result.summary.successful_tasks;
    document.getElementById('statSuccessRate').textContent = `${(result.summary.success_rate * 100).toFixed(2)}%`;
    document.getElementById('statByzantineCount').textContent = result.summary.byzantine_count;

    // Create charts
    createScoresChart(result.metrics.scores);
    createTokensChart(result.miners);
    createSuccessRateChart(result.metrics.success_rate);
    createRenewableEnergyChart(result.metrics.renewable_energy);

    // Populate miners table
    populateMinersTable(result.miners);
}

// Create scores over time chart
function createScoresChart(scoresData) {
    const traces = [];
    
    // Show only top 10 miners to avoid clutter
    const minerIds = Object.keys(scoresData);
    const topMiners = minerIds.slice(0, Math.min(10, minerIds.length));
    
    for (const minerId of topMiners) {
        traces.push({
            y: scoresData[minerId],
            type: 'scatter',
            mode: 'lines',
            name: `Miner ${minerId}`,
            line: { width: 2 }
        });
    }

    const layout = {
        xaxis: { title: 'Task Iterations' },
        yaxis: { title: 'Score' },
        showlegend: true,
        legend: { orientation: 'v', x: 1.05, y: 1 },
        margin: { t: 10, r: 150, b: 50, l: 50 },
        height: 400
    };

    Plotly.newPlot('scoresChart', traces, layout, { responsive: true });
}

// Create token distribution chart
function createTokensChart(minersData) {
    const minerIds = minersData.map(m => `Miner ${m.id}`);
    const tokens = minersData.map(m => m.tokens);
    const colors = minersData.map(m => m.is_byzantine ? 'rgba(239, 68, 68, 0.7)' : 'rgba(37, 99, 235, 0.7)');

    const trace = {
        x: minerIds,
        y: tokens,
        type: 'bar',
        marker: { color: colors },
        text: tokens.map(t => t.toFixed(2)),
        textposition: 'auto'
    };

    const layout = {
        xaxis: { title: 'Miner' },
        yaxis: { title: 'Tokens' },
        margin: { t: 10, r: 20, b: 100, l: 50 },
        height: 400
    };

    Plotly.newPlot('tokensChart', [trace], layout, { responsive: true });
}

// Create success rate chart
function createSuccessRateChart(successRateData) {
    const trace = {
        y: successRateData,
        type: 'scatter',
        mode: 'lines',
        name: 'Success Rate',
        line: { color: 'rgb(16, 185, 129)', width: 3 },
        fill: 'tozeroy',
        fillcolor: 'rgba(16, 185, 129, 0.1)'
    };

    const layout = {
        xaxis: { title: 'Task Iterations' },
        yaxis: { 
            title: 'Success Rate',
            tickformat: '.0%',
            range: [0, 1]
        },
        margin: { t: 10, r: 20, b: 50, l: 50 },
        height: 400
    };

    Plotly.newPlot('successRateChart', [trace], layout, { responsive: true });
}

// Create renewable energy usage chart
function createRenewableEnergyChart(renewableEnergyData) {
    const trace = {
        y: renewableEnergyData,
        type: 'scatter',
        mode: 'lines',
        name: 'Avg Renewable Energy',
        line: { color: 'rgb(245, 158, 11)', width: 3 },
        fill: 'tozeroy',
        fillcolor: 'rgba(245, 158, 11, 0.1)'
    };

    const layout = {
        xaxis: { title: 'Task Iterations' },
        yaxis: { 
            title: 'Proportion',
            tickformat: '.0%',
            range: [0, Math.max(...renewableEnergyData) * 1.2]
        },
        margin: { t: 10, r: 20, b: 50, l: 50 },
        height: 400
    };

    Plotly.newPlot('renewableEnergyChart', [trace], layout, { responsive: true });
}

// Populate miners table
function populateMinersTable(minersData) {
    const tbody = document.getElementById('minersTableBody');
    tbody.innerHTML = '';

    for (const miner of minersData) {
        const row = document.createElement('tr');
        if (miner.is_byzantine) {
            row.classList.add('byzantine-row');
        }

        row.innerHTML = `
            <td><strong>${miner.id}</strong></td>
            <td>${miner.score.toFixed(2)}</td>
            <td>${(miner.renewable_energy * 100).toFixed(2)}%</td>
            <td>${miner.tasks_completed}</td>
            <td>${(miner.error_rate * 100).toFixed(2)}%</td>
            <td><strong>${miner.tokens.toFixed(2)}</strong></td>
            <td>
                <span class="status-badge ${miner.is_byzantine ? 'status-byzantine' : 'status-normal'}">
                    ${miner.is_byzantine ? 'Byzantine' : 'Normal'}
                </span>
            </td>
        `;

        tbody.appendChild(row);
    }
}

// Alternative: Use EventSource for streaming results (commented out for now)
/*
function runSimulationWithStreaming() {
    const config = getConfigFromForm();
    const eventSource = new EventSource('/api/simulate');

    eventSource.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'progress') {
            updateProgress(data.completed, data.total, data.success_rate);
        } else if (data.type === 'final') {
            displayResults(data);
            eventSource.close();
            isSimulationRunning = false;
            runButton.disabled = false;
            runButton.textContent = 'Run Simulation';
        }
    });

    eventSource.addEventListener('error', (error) => {
        console.error('EventSource error:', error);
        eventSource.close();
        isSimulationRunning = false;
        runButton.disabled = false;
        runButton.textContent = 'Run Simulation';
    });
}
*/


