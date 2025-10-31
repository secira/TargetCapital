/**
 * LangGraph Visual Agent Workflow Components
 * Displays multi-agent workflows for Portfolio and Trading
 */

class PortfolioAgentWorkflow {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.agents = [
            { id: 'fetch', name: 'Data Fetcher', icon: 'database', status: 'pending' },
            { id: 'risk', name: 'Risk Analyzer', icon: 'shield-alt', status: 'pending', temp: '0.1' },
            { id: 'sector', name: 'Sector Analyzer', icon: 'chart-pie', status: 'pending', temp: '0.4' },
            { id: 'allocation', name: 'Asset Allocator', icon: 'layer-group', status: 'pending', temp: '0.4' },
            { id: 'opportunity', name: 'Opportunity Finder', icon: 'lightbulb', status: 'pending', temp: '0.7' },
            { id: 'coordinator', name: 'Coordinator', icon: 'project-diagram', status: 'pending' }
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
            <div class="agent-card ${statusClass}" data-agent-id="${agent.id}">
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
                ${index < this.agents.length - 1 ? '<div class="agent-arrow"><i class="fas fa-arrow-down"></i></div>' : ''}
            </div>
        `;
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
            { id: 'scan', name: 'Market Scanner', icon: 'radar', description: 'Scanning NSE/BSE markets', status: 'pending' },
            { id: 'generate', name: 'Signal Generator', icon: 'cogs', description: 'Creating trading signals', status: 'pending' },
            { id: 'validate', name: 'Validator', icon: 'check-double', description: 'Validating risk parameters', status: 'pending' },
            { id: 'broker', name: 'Broker Checker', icon: 'handshake', description: 'Checking compatibility', status: 'pending' },
            { id: 'execution', name: 'Execution Planner', icon: 'calendar-check', description: 'Creating execution strategy', status: 'pending' }
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
            <div class="stage-card ${statusClass}" data-stage-id="${stage.id}">
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
                ${index < this.stages.length - 1 ? '<div class="stage-arrow"><i class="fas fa-arrow-right"></i></div>' : ''}
            </div>
        `;
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

// Export for global use
window.PortfolioAgentWorkflow = PortfolioAgentWorkflow;
window.SignalPipelineWorkflow = SignalPipelineWorkflow;
