/**
 * LangGraph Visual Agent Workflow Components
 * Displays multi-agent workflows for Portfolio and Trading
 */

class PortfolioAgentWorkflow {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.agents = [
            { 
                id: 'fetch', 
                name: 'Data Fetcher', 
                icon: 'database', 
                status: 'pending',
                description: 'Retrieves portfolio data from connected brokers and manual holdings',
                role: 'Data Collection',
                model: 'System Process',
                config: {
                    sources: ['Broker APIs', 'Manual Holdings Database', 'Market Data APIs'],
                    caching: 'Enabled for 5 minutes',
                    timeout: '30 seconds'
                }
            },
            { 
                id: 'risk', 
                name: 'Risk Analyzer', 
                icon: 'shield-alt', 
                status: 'pending', 
                temp: '0.1',
                description: 'Conservative risk assessment focusing on portfolio volatility and diversification',
                role: 'Risk Management Specialist',
                model: 'GPT-4-turbo',
                config: {
                    temperature: '0.1 (Conservative)',
                    focus: 'Risk metrics, volatility analysis, diversification score',
                    output: 'Portfolio risk profile with actionable risk reduction strategies'
                }
            },
            { 
                id: 'sector', 
                name: 'Sector Analyzer', 
                icon: 'chart-pie', 
                status: 'pending', 
                temp: '0.4',
                description: 'Balanced analysis of sector allocation and concentration risks',
                role: 'Sector Diversification Expert',
                model: 'GPT-4-turbo',
                config: {
                    temperature: '0.4 (Balanced)',
                    focus: 'Sector concentration, allocation balance, industry exposure',
                    output: 'Sector-wise breakdown with rebalancing recommendations'
                }
            },
            { 
                id: 'allocation', 
                name: 'Asset Allocator', 
                icon: 'layer-group', 
                status: 'pending', 
                temp: '0.4',
                description: 'Optimal asset allocation across 11 asset classes based on user preferences',
                role: 'Strategic Asset Allocation Advisor',
                model: 'GPT-4-turbo',
                config: {
                    temperature: '0.4 (Balanced)',
                    focus: 'Asset class distribution, allocation optimization, portfolio balance',
                    output: 'Ideal allocation targets with rebalancing actions'
                }
            },
            { 
                id: 'opportunity', 
                name: 'Opportunity Finder', 
                icon: 'lightbulb', 
                status: 'pending', 
                temp: '0.7',
                description: 'Creative investment opportunities based on market trends and user preferences',
                role: 'Growth Opportunity Specialist',
                model: 'GPT-4-turbo',
                config: {
                    temperature: '0.7 (Creative)',
                    focus: 'Emerging opportunities, market trends, growth potential',
                    output: 'Personalized investment recommendations with rationale'
                }
            },
            { 
                id: 'coordinator', 
                name: 'Coordinator', 
                icon: 'project-diagram', 
                status: 'pending',
                description: 'Synthesizes all agent outputs into comprehensive portfolio optimization report',
                role: 'Portfolio Optimization Coordinator',
                model: 'GPT-4-turbo',
                config: {
                    temperature: '0.3 (Synthesis)',
                    focus: 'Comprehensive analysis integration, actionable recommendations',
                    output: 'Final portfolio optimization report with executive summary'
                }
            }
        ];
        this.render();
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="langgraph-workflow portfolio-workflow">
                <div class="workflow-header">
                    <h5><i class="fas fa-robot me-2"></i>Multi-Agent Portfolio Optimizer</h5>
                    <p class="text-muted">4 specialized AI agents working in parallel</p>
                </div>
                <div class="agents-container">
                    ${this.agents.map((agent, index) => this.renderAgent(agent, index)).join('')}
                </div>
            </div>
        `;
    }

    renderAgent(agent, index) {
        const statusClass = {
            'pending': 'agent-pending',
            'in_progress': 'agent-progress',
            'completed': 'agent-completed',
            'error': 'agent-error'
        }[agent.status] || 'agent-pending';

        const statusIcon = {
            'pending': 'clock',
            'in_progress': 'spinner fa-spin',
            'completed': 'check-circle',
            'error': 'exclamation-circle'
        }[agent.status] || 'clock';

        return `
            <div class="agent-card ${statusClass} agent-clickable" data-agent-id="${agent.id}" onclick="window.showAgentConfig('${agent.id}')" title="Click to view agent configuration">
                <div class="agent-number">${index + 1}</div>
                <div class="agent-icon">
                    <i class="fas fa-${agent.icon}"></i>
                </div>
                <div class="agent-info">
                    <h6>${agent.name}</h6>
                    ${agent.temp ? `<span class="badge badge-temp">Temp: ${agent.temp}</span>` : ''}
                </div>
                <div class="agent-status">
                    <i class="fas fa-${statusIcon}"></i>
                </div>
                <div class="agent-info-icon">
                    <i class="fas fa-info-circle"></i>
                </div>
                ${index < this.agents.length - 1 ? '<div class="agent-arrow"><i class="fas fa-arrow-down"></i></div>' : ''}
            </div>
        `;
    }
    
    getAgent(agentId) {
        return this.agents.find(a => a.id === agentId);
    }

    updateAgent(agentId, status, message = '') {
        const agent = this.agents.find(a => a.id === agentId);
        if (agent) {
            agent.status = status;
            agent.message = message;
            this.render();
        }
    }

    reset() {
        this.agents.forEach(agent => agent.status = 'pending');
        this.render();
    }

    async runWorkflow() {
        this.reset();
        
        for (const agent of this.agents) {
            this.updateAgent(agent.id, 'in_progress');
            await this.simulateAgent(agent);
            this.updateAgent(agent.id, 'completed');
        }
    }

    simulateAgent(agent) {
        // Simulate agent processing time
        const baseTime = 1000;
        const variance = Math.random() * 1000;
        return new Promise(resolve => setTimeout(resolve, baseTime + variance));
    }
}

class SignalPipelineWorkflow {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.stages = [
            { 
                id: 'scan', 
                name: 'Market Scanner', 
                icon: 'radar', 
                description: 'Scanning NSE/BSE markets', 
                status: 'pending',
                fullDescription: 'Scans Indian stock markets (NSE/BSE) using Perplexity Sonar Pro for real-time opportunities',
                model: 'Perplexity Sonar Pro',
                config: {
                    markets: ['NSE', 'BSE'],
                    filters: ['Volume > avg', 'Price action breakouts', 'News catalysts'],
                    timeframe: 'Intraday + Swing trading',
                    output: 'List of potential trading opportunities'
                }
            },
            { 
                id: 'generate', 
                name: 'Signal Generator', 
                icon: 'cogs', 
                description: 'Creating trading signals', 
                status: 'pending',
                fullDescription: 'Generates detailed trading signals with entry, target, and stop-loss prices',
                model: 'GPT-4-turbo + NSE Data',
                config: {
                    analysis: ['Technical indicators', 'Price levels', 'Risk-reward calculation'],
                    signalType: ['BUY', 'SELL', 'HOLD'],
                    components: 'Entry price, target price, stop-loss, position size',
                    output: 'Structured trading signals with complete execution details'
                }
            },
            { 
                id: 'validate', 
                name: 'Validator', 
                icon: 'check-double', 
                description: 'Validating risk parameters', 
                status: 'pending',
                fullDescription: 'Applies strict quality gates to ensure only high-probability signals pass through',
                model: 'Risk Validation Engine',
                config: {
                    minRiskReward: '1:2 ratio',
                    maxStopLoss: '5% of entry price',
                    minConfidence: '70% probability',
                    qualityChecks: ['Valid price levels', 'Realistic targets', 'Proper risk management'],
                    output: 'Only signals meeting all quality criteria'
                }
            },
            { 
                id: 'broker', 
                name: 'Broker Checker', 
                icon: 'handshake', 
                description: 'Checking compatibility', 
                status: 'pending',
                fullDescription: 'Verifies signal compatibility with user\'s connected brokers and subscription plan',
                model: 'System Validation',
                config: {
                    checks: ['Broker support for symbol', 'Segment availability', 'Plan permissions'],
                    brokers: ['Dhan', 'Zerodha', 'Angel One', 'Groww', 'Upstox'],
                    planRules: 'Target Pro+ for live execution',
                    output: 'Broker-compatible signals with execution readiness status'
                }
            },
            { 
                id: 'execution', 
                name: 'Execution Planner', 
                icon: 'calendar-check', 
                description: 'Creating execution strategy', 
                status: 'pending',
                fullDescription: 'Creates detailed execution strategy with timing and order management',
                model: 'Execution Engine',
                config: {
                    orderTypes: ['Limit orders', 'Stop-loss orders', 'Target orders'],
                    timing: 'Market hours validation (9:15 AM - 3:30 PM)',
                    notifications: ['WhatsApp', 'Telegram', 'In-app'],
                    output: 'Complete execution plan with scheduled orders'
                }
            }
        ];
        this.metrics = {
            scanned: 0,
            generated: 0,
            validated: 0,
            ready: 0
        };
        this.render();
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="langgraph-workflow signal-workflow">
                <div class="workflow-header">
                    <h5><i class="fas fa-project-diagram me-2"></i>Smart Trading Signal Pipeline</h5>
                    <p class="text-muted">5-stage validation process for quality signals</p>
                </div>
                <div class="pipeline-metrics">
                    <div class="metric">
                        <div class="metric-value">${this.metrics.scanned}</div>
                        <div class="metric-label">Scanned</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${this.metrics.generated}</div>
                        <div class="metric-label">Generated</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${this.metrics.validated}</div>
                        <div class="metric-label">Validated</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${this.metrics.ready}</div>
                        <div class="metric-label">Ready</div>
                    </div>
                </div>
                <div class="stages-container">
                    ${this.stages.map((stage, index) => this.renderStage(stage, index)).join('')}
                </div>
            </div>
        `;
    }

    renderStage(stage, index) {
        const statusClass = {
            'pending': 'stage-pending',
            'in_progress': 'stage-progress',
            'completed': 'stage-completed',
            'skipped': 'stage-skipped',
            'error': 'stage-error'
        }[stage.status] || 'stage-pending';

        const statusIcon = {
            'pending': 'circle',
            'in_progress': 'spinner fa-spin',
            'completed': 'check-circle',
            'skipped': 'times-circle',
            'error': 'exclamation-circle'
        }[stage.status] || 'circle';

        return `
            <div class="stage-card ${statusClass} stage-clickable" data-stage-id="${stage.id}" onclick="window.showStageConfig('${stage.id}')" title="Click to view stage configuration">
                <div class="stage-number">${index + 1}</div>
                <div class="stage-content">
                    <div class="stage-icon">
                        <i class="fas fa-${stage.icon}"></i>
                    </div>
                    <div class="stage-info">
                        <h6>${stage.name}</h6>
                        <p class="stage-description">${stage.description}</p>
                    </div>
                    <div class="stage-status">
                        <i class="fas fa-${statusIcon}"></i>
                    </div>
                </div>
                <div class="stage-info-icon">
                    <i class="fas fa-info-circle"></i>
                </div>
                ${index < this.stages.length - 1 ? '<div class="stage-arrow"><i class="fas fa-arrow-right"></i></div>' : ''}
            </div>
        `;
    }
    
    getStage(stageId) {
        return this.stages.find(s => s.id === stageId);
    }

    updateStage(stageId, status, message = '') {
        const stage = this.stages.find(s => s.id === stageId);
        if (stage) {
            stage.status = status;
            if (message) stage.description = message;
            this.render();
        }
    }

    updateMetrics(metrics) {
        this.metrics = { ...this.metrics, ...metrics };
        this.render();
    }

    reset() {
        this.stages.forEach(stage => {
            stage.status = 'pending';
            stage.description = stage.originalDescription || stage.description;
        });
        this.metrics = { scanned: 0, generated: 0, validated: 0, ready: 0 };
        this.render();
    }

    async runPipeline() {
        this.reset();
        
        for (let i = 0; i < this.stages.length; i++) {
            const stage = this.stages[i];
            this.updateStage(stage.id, 'in_progress');
            await this.simulateStage(stage);
            
            // Simulate conditional logic
            if (stage.id === 'generate' && Math.random() < 0.1) {
                this.updateStage(stage.id, 'completed', 'No signals generated');
                // Skip remaining stages
                for (let j = i + 1; j < this.stages.length; j++) {
                    this.updateStage(this.stages[j].id, 'skipped');
                }
                break;
            }
            
            this.updateStage(stage.id, 'completed');
        }
    }

    simulateStage(stage) {
        const baseTime = 1500;
        const variance = Math.random() * 1000;
        return new Promise(resolve => setTimeout(resolve, baseTime + variance));
    }
}

// CSS Styles
const styles = `
<style>
.langgraph-workflow {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin-bottom: 24px;
}

.workflow-header {
    margin-bottom: 24px;
    text-align: center;
}

.workflow-header h5 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #1a1a1a;
}

.workflow-header p {
    font-size: 14px;
    margin: 0;
}

/* Portfolio Agent Cards */
.agents-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.agent-card {
    display: flex;
    align-items: center;
    padding: 16px;
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    background: #f8f9fa;
    position: relative;
    transition: all 0.3s ease;
}

.agent-clickable {
    cursor: pointer;
}

.agent-clickable:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.agent-info-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 16px;
    color: #4299e1;
    opacity: 0.6;
    transition: opacity 0.3s ease;
}

.agent-clickable:hover .agent-info-icon {
    opacity: 1;
}

.agent-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #6c757d;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    margin-right: 16px;
}

.agent-icon {
    font-size: 24px;
    color: #6c757d;
    margin-right: 16px;
}

.agent-info {
    flex: 1;
}

.agent-info h6 {
    margin: 0 0 4px 0;
    font-size: 16px;
    font-weight: 600;
}

.badge-temp {
    font-size: 11px;
    padding: 2px 8px;
    background: #e3f2fd;
    color: #1976d2;
    border-radius: 4px;
}

.agent-status {
    font-size: 24px;
    margin-left: 16px;
}

.agent-arrow {
    position: absolute;
    bottom: -24px;
    left: 50%;
    transform: translateX(-50%);
    color: #ccc;
    font-size: 20px;
}

.agent-pending {
    border-color: #e0e0e0;
}

.agent-progress {
    border-color: #2196f3;
    background: #e3f2fd;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.agent-progress .agent-number {
    background: #2196f3;
}

.agent-progress .agent-icon {
    color: #2196f3;
}

.agent-progress .agent-status {
    color: #2196f3;
}

.agent-completed {
    border-color: #4caf50;
    background: #e8f5e9;
}

.agent-completed .agent-number {
    background: #4caf50;
}

.agent-completed .agent-icon {
    color: #4caf50;
}

.agent-completed .agent-status {
    color: #4caf50;
}

.agent-error {
    border-color: #f44336;
    background: #ffebee;
}

/* Signal Pipeline */
.pipeline-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.metric {
    text-align: center;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #2196f3;
    line-height: 1;
}

.metric-label {
    font-size: 12px;
    color: #666;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stages-container {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding: 8px 0;
}

.stage-card {
    min-width: 200px;
    flex-shrink: 0;
    padding: 16px;
    border-radius: 8px;
    border: 2px solid #e0e0e0;
    background: #f8f9fa;
    position: relative;
    transition: all 0.3s ease;
}

.stage-clickable {
    cursor: pointer;
}

.stage-clickable:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.stage-info-icon {
    position: absolute;
    top: 8px;
    left: 8px;
    font-size: 14px;
    color: #4299e1;
    opacity: 0.6;
    transition: opacity 0.3s ease;
}

.stage-clickable:hover .stage-info-icon {
    opacity: 1;
}

.stage-number {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #6c757d;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
}

.stage-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.stage-icon {
    font-size: 32px;
    color: #6c757d;
    text-align: center;
}

.stage-info h6 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
}

.stage-description {
    margin: 0;
    font-size: 12px;
    color: #666;
}

.stage-status {
    text-align: center;
    font-size: 24px;
}

.stage-arrow {
    position: absolute;
    right: -20px;
    top: 50%;
    transform: translateY(-50%);
    color: #ccc;
    font-size: 20px;
}

.stage-pending {
    border-color: #e0e0e0;
}

.stage-progress {
    border-color: #2196f3;
    background: #e3f2fd;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

.stage-progress .stage-icon,
.stage-progress .stage-status {
    color: #2196f3;
}

.stage-completed {
    border-color: #4caf50;
    background: #e8f5e9;
}

.stage-completed .stage-icon,
.stage-completed .stage-status {
    color: #4caf50;
}

.stage-skipped {
    border-color: #ff9800;
    background: #fff3e0;
    opacity: 0.7;
}

.stage-error {
    border-color: #f44336;
    background: #ffebee;
}

@media (max-width: 768px) {
    .pipeline-metrics {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .stages-container {
        flex-direction: column;
    }
    
    .stage-arrow {
        display: none;
    }
}
</style>
`;

// Inject styles
if (!document.getElementById('langgraph-visual-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'langgraph-visual-styles';
    styleElement.innerHTML = styles;
    document.head.appendChild(styleElement);
}

// Global functions for showing agent/stage configuration
window.showAgentConfig = function(agentId) {
    const workflow = window.portfolioWorkflow;
    if (!workflow) return;
    
    const agent = workflow.getAgent(agentId);
    if (!agent) return;
    
    const modal = document.getElementById('agentConfigModal');
    if (!modal) {
        createAgentConfigModal();
        showAgentConfig(agentId);
        return;
    }
    
    // Populate modal content
    document.getElementById('agentModalTitle').innerHTML = `<i class="fas fa-${agent.icon} me-2"></i>${agent.name}`;
    document.getElementById('agentModalRole').textContent = agent.role;
    document.getElementById('agentModalDescription').textContent = agent.description;
    document.getElementById('agentModalModel').textContent = agent.model;
    
    // Build configuration list
    let configHTML = '<ul class="list-unstyled">';
    for (const [key, value] of Object.entries(agent.config)) {
        const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
        if (Array.isArray(value)) {
            configHTML += `<li><strong>${label}:</strong> ${value.join(', ')}</li>`;
        } else {
            configHTML += `<li><strong>${label}:</strong> ${value}</li>`;
        }
    }
    configHTML += '</ul>';
    document.getElementById('agentModalConfig').innerHTML = configHTML;
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
};

window.showStageConfig = function(stageId) {
    const workflow = window.signalWorkflow;
    if (!workflow) return;
    
    const stage = workflow.getStage(stageId);
    if (!stage) return;
    
    const modal = document.getElementById('stageConfigModal');
    if (!modal) {
        createStageConfigModal();
        showStageConfig(stageId);
        return;
    }
    
    // Populate modal content
    document.getElementById('stageModalTitle').innerHTML = `<i class="fas fa-${stage.icon} me-2"></i>${stage.name}`;
    document.getElementById('stageModalDescription').textContent = stage.fullDescription;
    document.getElementById('stageModalModel').textContent = stage.model;
    
    // Build configuration list
    let configHTML = '<ul class="list-unstyled">';
    for (const [key, value] of Object.entries(stage.config)) {
        const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
        if (Array.isArray(value)) {
            configHTML += `<li><strong>${label}:</strong> ${value.join(', ')}</li>`;
        } else {
            configHTML += `<li><strong>${label}:</strong> ${value}</li>`;
        }
    }
    configHTML += '</ul>';
    document.getElementById('stageModalConfig').innerHTML = configHTML;
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
};

function createAgentConfigModal() {
    const modalHTML = `
        <div class="modal fade" id="agentConfigModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="agentModalTitle"></h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <h6 class="text-primary"><i class="fas fa-user-tag me-1"></i> Role</h6>
                            <p id="agentModalRole" class="mb-0"></p>
                        </div>
                        <div class="mb-3">
                            <h6 class="text-primary"><i class="fas fa-info-circle me-1"></i> Description</h6>
                            <p id="agentModalDescription" class="mb-0"></p>
                        </div>
                        <div class="mb-3">
                            <h6 class="text-primary"><i class="fas fa-brain me-1"></i> AI Model</h6>
                            <p id="agentModalModel" class="mb-0"></p>
                        </div>
                        <div class="mb-0">
                            <h6 class="text-primary"><i class="fas fa-cog me-1"></i> Configuration</h6>
                            <div id="agentModalConfig"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function createStageConfigModal() {
    const modalHTML = `
        <div class="modal fade" id="stageConfigModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title" id="stageModalTitle"></h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <h6 class="text-success"><i class="fas fa-info-circle me-1"></i> Description</h6>
                            <p id="stageModalDescription" class="mb-0"></p>
                        </div>
                        <div class="mb-3">
                            <h6 class="text-success"><i class="fas fa-microchip me-1"></i> Model/Engine</h6>
                            <p id="stageModalModel" class="mb-0"></p>
                        </div>
                        <div class="mb-0">
                            <h6 class="text-success"><i class="fas fa-sliders-h me-1"></i> Pipeline Configuration</h6>
                            <div id="stageModalConfig"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

// Export for global use
window.PortfolioAgentWorkflow = PortfolioAgentWorkflow;
window.SignalPipelineWorkflow = SignalPipelineWorkflow;
