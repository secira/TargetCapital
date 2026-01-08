/**
 * React-style Dashboard Components for Target Capital
 * High-performance real-time dashboard with WebSocket integration
 */

// Dashboard App - Main React-style component
class DashboardApp {
    constructor() {
        this.state = {
            user: null,
            marketData: {},
            portfolio: {},
            tradingSignals: [],
            connectionStatus: {},
            notifications: [],
            isLoading: true
        };
        
        this.components = new Map();
        this.websockets = new Map();
        this.init();
    }
    
    async init() {
        try {
            // Initialize WebSocket connections
            await this.initializeWebSockets();
            
            // Load initial data
            await this.loadInitialData();
            
            // Mount components
            this.mountComponents();
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
            this.setState({ isLoading: false });
            
        } catch (error) {
            console.error('Dashboard initialization error:', error);
            this.setState({ isLoading: false });
        }
    }
    
    async initializeWebSockets() {
        try {
            // Market data WebSocket
            const marketWS = new WebSocketClient({
                url: 'ws://localhost:8001',
                autoReconnect: true,
                maxReconnectAttempts: 5
            });
            
            marketWS.on('open', () => {
                this.updateConnectionStatus('market', 'connected');
                console.log('✅ Market data WebSocket connected');
                // Subscribe to major indices and popular stocks
                marketWS.send({
                    type: 'subscribe',
                    symbols: ['NIFTY', 'BANKNIFTY', 'SENSEX', 'RELIANCE', 'TCS', 'INFY']
                });
            });
            
            marketWS.on('message', (data) => {
                if (data.type === 'market_data') {
                    this.setState({
                        marketData: { ...this.state.marketData, ...data.data }
                    });
                    console.log('📊 Market data updated via WebSocket');
                }
            });
            
            marketWS.on('close', () => {
                this.updateConnectionStatus('market', 'disconnected');
                console.log('🔌 Market WebSocket disconnected');
            });
            
            marketWS.on('error', () => {
                this.updateConnectionStatus('market', 'error');
                console.log('❌ Market WebSocket error - switching to demo mode');
                this.enableDemoMode();
            });
            
            this.websockets.set('market', marketWS);
            
            // Trading updates WebSocket (optional for demo)
            const tradingWS = new WebSocketClient({
                url: 'ws://localhost:8002',
                autoReconnect: true,
                maxReconnectAttempts: 3
            });
            
            tradingWS.on('open', () => {
                this.updateConnectionStatus('trading', 'connected');
                console.log('✅ Trading WebSocket connected');
            });
            
            tradingWS.on('close', () => {
                this.updateConnectionStatus('trading', 'disconnected');
            });
            
            tradingWS.on('error', () => {
                this.updateConnectionStatus('trading', 'demo');
                console.log('🎭 Trading WebSocket in demo mode');
            });
            
            tradingWS.on('message', (data) => {
                switch (data.type) {
                    case 'order_update':
                        this.handleOrderUpdate(data.order);
                        break;
                    case 'portfolio_update':
                        this.setState({ portfolio: data.portfolio });
                        break;
                    case 'trading_signal':
                        this.handleTradingSignal(data.signal);
                        break;
                }
            });
            
            this.websockets.set('trading', tradingWS);
            
            // Try to connect - if it fails, use demo mode
            try {
                await Promise.all([
                    marketWS.connect().catch(() => console.log('Market WS demo mode')),
                    tradingWS.connect().catch(() => console.log('Trading WS demo mode'))
                ]);
            } catch (error) {
                console.log('🎭 WebSocket connections failed - enabling enhanced demo mode');
                this.enableDemoMode();
            }
            
        } catch (error) {
            console.log('🎭 WebSocket initialization failed - using demo mode');
            this.enableDemoMode();
        }
    }
    
    enableDemoMode() {
        console.log('🎭 Enabling enhanced demo mode with simulated real-time data');
        
        // Simulate market data updates
        setInterval(() => {
            const demoMarketData = this.generateDemoMarketData();
            this.setState({ marketData: demoMarketData });
            console.log('📊 Demo market data updated');
        }, 5000);
        
        // Simulate trading signals
        setInterval(() => {
            const demoSignal = this.generateDemoSignal();
            this.handleTradingSignal(demoSignal);
        }, 15000);
        
        // Update connection status
        this.updateConnectionStatus('market', 'demo');
        this.updateConnectionStatus('trading', 'demo');
    }
    
    generateDemoMarketData() {
        const baseValues = {
            'NIFTY': 25041.10,
            'BANKNIFTY': 51234.80,
            'SENSEX': 81523.45,
            'RELIANCE': 2845.60,
            'TCS': 4125.30,
            'INFY': 1756.25
        };
        
        const marketData = { indices: {}, stocks: {} };
        
        Object.entries(baseValues).forEach(([symbol, baseValue]) => {
            const change = (Math.random() - 0.5) * 4; // -2% to +2%
            const newValue = baseValue * (1 + change / 100);
            
            if (['NIFTY', 'BANKNIFTY', 'SENSEX'].includes(symbol)) {
                marketData.indices[symbol] = {
                    value: newValue.toFixed(2),
                    change: change.toFixed(2)
                };
            } else {
                marketData.stocks[symbol] = {
                    price: newValue.toFixed(2),
                    change: change.toFixed(2),
                    volume: `${(Math.random() * 5 + 1).toFixed(1)}M`
                };
            }
        });
        
        return marketData;
    }
    
    generateDemoSignal() {
        const symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'SBIN', 'ITC'];
        const actions = ['BUY', 'SELL', 'HOLD'];
        const reasons = [
            'Strong momentum detected',
            'Technical breakout pattern',
            'Volume spike observed',
            'Support level holding',
            'Resistance broken',
            'AI pattern recognition'
        ];
        
        return {
            id: Date.now(),
            symbol: symbols[Math.floor(Math.random() * symbols.length)],
            action: actions[Math.floor(Math.random() * actions.length)],
            confidence: Math.floor(Math.random() * 40) + 60, // 60-100%
            reason: reasons[Math.floor(Math.random() * reasons.length)],
            timestamp: new Date()
        };
    }
    
    async loadInitialData() {
        try {
            // Load user data
            const userResponse = await fetch('/api/user/profile');
            if (userResponse.ok) {
                const userData = await userResponse.json();
                this.setState({ user: userData.user });
            }
            
            // Load portfolio data
            const portfolioResponse = await fetch('/api/portfolio');
            if (portfolioResponse.ok) {
                const portfolioData = await portfolioResponse.json();
                this.setState({ portfolio: portfolioData.portfolio });
            }
            
            // Load trading signals
            const signalsResponse = await fetch('/api/trading-signals');
            if (signalsResponse.ok) {
                const signalsData = await signalsResponse.json();
                this.setState({ tradingSignals: signalsData.signals });
            }
            
        } catch (error) {
            console.error('Initial data load error:', error);
        }
    }
    
    mountComponents() {
        // Mount real-time market component
        const marketElement = document.querySelector('[data-component="realtime-market"]');
        if (marketElement) {
            const marketComponent = new RealTimeMarketData(marketElement, {
                initialData: this.state.marketData
            });
            this.components.set('market', marketComponent);
        }
        
        // Mount portfolio component
        const portfolioElement = document.querySelector('[data-component="portfolio"]');
        if (portfolioElement) {
            const portfolioComponent = new Portfolio(portfolioElement, {
                initialData: this.state.portfolio
            });
            this.components.set('portfolio', portfolioComponent);
        }
        
        // Mount AI signals component
        const signalsElement = document.querySelector('[data-component="ai-signals"]');
        if (signalsElement) {
            const signalsComponent = new AITradingSignals(signalsElement, {
                initialData: this.state.tradingSignals
            });
            this.components.set('signals', signalsComponent);
        }
    }
    
    startRealTimeUpdates() {
        // Refresh critical data every 30 seconds
        setInterval(() => {
            this.refreshCriticalData();
        }, 30000);
        
        // Refresh market data every 10 seconds during market hours
        setInterval(() => {
            if (this.isMarketOpen()) {
                this.refreshMarketData();
            }
        }, 10000);
    }
    
    async refreshCriticalData() {
        try {
            const [portfolioRes, signalsRes] = await Promise.all([
                fetch('/api/portfolio'),
                fetch('/api/trading-signals')
            ]);
            
            if (portfolioRes.ok) {
                const portfolioData = await portfolioRes.json();
                this.setState({ portfolio: portfolioData.portfolio });
            }
            
            if (signalsRes.ok) {
                const signalsData = await signalsRes.json();
                this.setState({ tradingSignals: signalsData.signals });
            }
            
        } catch (error) {
            console.error('Critical data refresh error:', error);
        }
    }
    
    async refreshMarketData() {
        const marketWS = this.websockets.get('market');
        if (marketWS && marketWS.isConnected) {
            marketWS.send({
                type: 'refresh_data',
                timestamp: Date.now()
            });
        }
    }
    
    isMarketOpen() {
        const now = new Date();
        const hour = now.getHours();
        const minute = now.getMinutes();
        const day = now.getDay();
        
        // Indian market hours: 9:15 AM to 3:30 PM, Monday to Friday
        const isWeekday = day >= 1 && day <= 5;
        const isMarketHours = (hour > 9 || (hour === 9 && minute >= 15)) && 
                             (hour < 15 || (hour === 15 && minute <= 30));
        
        return isWeekday && isMarketHours;
    }
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notifyComponents();
    }
    
    notifyComponents() {
        // Notify all components of state changes
        for (const [name, component] of this.components) {
            if (component.onStateChange) {
                component.onStateChange(this.state);
            }
        }
    }
    
    updateConnectionStatus(service, status) {
        const connectionStatus = { ...this.state.connectionStatus };
        connectionStatus[service] = status;
        this.setState({ connectionStatus });
    }
    
    handleOrderUpdate(order) {
        // Update portfolio if order affects it
        if (order.status === 'filled') {
            this.refreshCriticalData();
        }
        
        // Show notification
        this.addNotification(
            `Order ${order.status}: ${order.symbol} ${order.side} ${order.quantity}`,
            order.status === 'filled' ? 'success' : 'info'
        );
    }
    
    handleTradingSignal(signal) {
        // Add new signal to the list
        const signals = [...this.state.tradingSignals];
        signals.unshift(signal);
        
        // Keep only latest 50 signals
        if (signals.length > 50) {
            signals.splice(50);
        }
        
        this.setState({ tradingSignals: signals });
        
        // Suppress initial connection signal if it contains specific text
        if (signal.message === 'Market Data Connected') return;
        
        // Send to non-intrusive signal manager instead of popup
        if (signal.confidence >= 80 && window.signalManager) {
            window.signalManager.handleNewSignal(signal);
        }
    }
    
    addNotification(message, type = 'info', duration = 5000) {
        // Suppress "Market Data Connected" and "Market data updated" notifications
        if (message.includes('Market Data Connected') || message.includes('Market data updated')) {
            return;
        }
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date()
        };
        
        const notifications = [...this.state.notifications, notification];
        this.setState({ notifications });
        
        // Auto-remove
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification.id);
            }, duration);
        }
        
        // Show toast notification
        this.showToast(message, type);
    }
    
    removeNotification(id) {
        const notifications = this.state.notifications.filter(n => n.id !== id);
        this.setState({ notifications });
    }
    
    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hide
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    getConnectionStatusSummary() {
        const statuses = Object.values(this.state.connectionStatus);
        const connected = statuses.filter(s => s === 'connected').length;
        const total = statuses.length;
        
        if (connected === total && total > 0) return 'all-connected';
        if (connected > 0) return 'partial-connected';
        return 'disconnected';
    }
    
    destroy() {
        // Cleanup all WebSocket connections
        for (const [name, ws] of this.websockets) {
            ws.disconnect();
        }
        
        // Cleanup all components
        for (const [name, component] of this.components) {
            if (component.destroy) {
                component.destroy();
            }
        }
        
        this.websockets.clear();
        this.components.clear();
    }
}

// Real-time Status Component
class RealTimeStatus {
    constructor(element) {
        this.element = element;
        this.render();
        
        // Update every second
        setInterval(() => this.render(), 1000);
    }
    
    render() {
        if (!this.element || !window.dashboardApp) return;
        
        const app = window.dashboardApp;
        const statusSummary = app.getConnectionStatusSummary();
        const marketOpen = app.isMarketOpen();
        
        const statusConfig = {
            'all-connected': { color: 'success', text: 'All Systems Online', icon: 'check-circle' },
            'partial-connected': { color: 'warning', text: 'Partial Connection', icon: 'exclamation-triangle' },
            'disconnected': { color: 'danger', text: 'Connection Issues', icon: 'times-circle' }
        };
        
        const config = statusConfig[statusSummary];
        
        this.element.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="me-3">
                    <span class="badge bg-${config.color}">
                        <i class="fas fa-${config.icon} me-1"></i>
                        ${config.text}
                    </span>
                </div>
                <div>
                    <span class="badge bg-${marketOpen ? 'success' : 'secondary'}">
                        <i class="fas fa-clock me-1"></i>
                        Market ${marketOpen ? 'Open' : 'Closed'}
                    </span>
                </div>
            </div>
        `;
    }
}

// Performance Metrics Component
class PerformanceMetrics {
    constructor(element) {
        this.element = element;
        this.metrics = {};
        this.startMonitoring();
    }
    
    startMonitoring() {
        // Monitor performance every 10 seconds
        setInterval(() => {
            this.collectMetrics();
            this.render();
        }, 10000);
        
        // Initial collection
        this.collectMetrics();
        this.render();
    }
    
    collectMetrics() {
        // Collect various performance metrics
        this.metrics = {
            pageLoadTime: this.getPageLoadTime(),
            memoryUsage: this.getMemoryUsage(),
            connectionLatency: this.getConnectionLatency(),
            wsConnections: this.getWebSocketCount(),
            lastUpdate: new Date().toLocaleTimeString()
        };
    }
    
    getPageLoadTime() {
        if (performance.timing) {
            return performance.timing.loadEventEnd - performance.timing.navigationStart;
        }
        return 0;
    }
    
    getMemoryUsage() {
        if (performance.memory) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024)
            };
        }
        return null;
    }
    
    getConnectionLatency() {
        // Simplified latency calculation
        return Math.random() * 50 + 10; // 10-60ms simulation
    }
    
    getWebSocketCount() {
        return window.dashboardApp ? window.dashboardApp.websockets.size : 0;
    }
    
    render() {
        if (!this.element) return;
        
        const { pageLoadTime, memoryUsage, connectionLatency, wsConnections, lastUpdate } = this.metrics;
        
        this.element.innerHTML = `
            <div class="performance-metrics">
                <h6 class="mb-3">⚡ Performance Metrics</h6>
                
                <div class="row">
                    <div class="col-6 mb-2">
                        <div class="metric-item">
                            <small class="text-muted">Page Load</small>
                            <div class="fw-bold">${pageLoadTime}ms</div>
                        </div>
                    </div>
                    <div class="col-6 mb-2">
                        <div class="metric-item">
                            <small class="text-muted">Latency</small>
                            <div class="fw-bold">${Math.round(connectionLatency)}ms</div>
                        </div>
                    </div>
                    <div class="col-6 mb-2">
                        <div class="metric-item">
                            <small class="text-muted">Memory</small>
                            <div class="fw-bold">${memoryUsage ? `${memoryUsage.used}MB` : 'N/A'}</div>
                        </div>
                    </div>
                    <div class="col-6 mb-2">
                        <div class="metric-item">
                            <small class="text-muted">WS Conn</small>
                            <div class="fw-bold">${wsConnections}</div>
                        </div>
                    </div>
                </div>
                
                <div class="text-end mt-2">
                    <small class="text-muted">Updated: ${lastUpdate}</small>
                </div>
            </div>
        `;
    }
}

// Initialize Dashboard App when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main dashboard app
    window.dashboardApp = new DashboardApp();
    
    // Initialize status component
    const statusElement = document.querySelector('[data-component="realtime-status"]');
    if (statusElement) {
        new RealTimeStatus(statusElement);
    }
    
    // Initialize performance metrics
    const metricsElement = document.querySelector('[data-component="performance-metrics"]');
    if (metricsElement) {
        new PerformanceMetrics(metricsElement);
    }
    
    // Handle page visibility for performance optimization
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            // Page is hidden, reduce update frequency
            console.log('📱 Page hidden - reducing update frequency');
        } else {
            // Page is visible, resume normal updates
            console.log('📱 Page visible - resuming normal updates');
            if (window.dashboardApp) {
                window.dashboardApp.refreshCriticalData();
            }
        }
    });
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboardApp) {
        window.dashboardApp.destroy();
    }
});

// Export for global access
window.TargeTarget CapitalDashboard = {
    DashboardApp,
    RealTimeStatus,
    PerformanceMetrics
};

// Backward compatibility alias
window.Target CapitalDashboard = window.TargeTarget CapitalDashboard;