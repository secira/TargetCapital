/**
 * Demo WebSocket Simulator for React Integration Testing
 * Simulates WebSocket behavior for development and testing
 */

class DemoWebSocketSimulator {
    constructor() {
        this.isActive = false;
        this.marketDataInterval = null;
        this.tradingSignalInterval = null;
        this.performanceInterval = null;
        
        // Event listeners for demo mode
        this.listeners = new Map();
        
        console.log('🎭 Demo WebSocket Simulator initialized');
    }
    
    start() {
        if (this.isActive) return;
        
        this.isActive = true;
        console.log('🚀 Starting Demo WebSocket simulation...');
        
        // Update connection status  
        this.updateRealtimeStatus('Connected', 'success');
        
        // Start market data simulation
        this.startMarketDataSimulation();
        
        // Start trading signal simulation  
        this.startTradingSignalSimulation();
        
        // Start performance monitoring
        this.startPerformanceMonitoring();
        
        // Show initial notification
        // this.showDemoNotification();
        
        // Initial state
        this.updateRealtimeStatus('Connected', 'success');
    }
    
    stop() {
        this.isActive = false;
        
        // Clear all intervals
        [this.marketDataInterval, this.tradingSignalInterval, this.performanceInterval]
            .filter(Boolean)
            .forEach(clearInterval);
        
        console.log('🛑 Demo WebSocket simulation stopped');
    }
    
    startMarketDataSimulation() {
        // Update market data every 3 seconds
        this.marketDataInterval = setInterval(() => {
            const marketData = this.generateMarketData();
            this.updateMarketDisplays(marketData);
            
            // Emit event for React components
            this.emit('market_data', marketData);
            
        }, 3000);
        
        // Initial update
        setTimeout(() => {
            const initialData = this.generateMarketData();
            this.updateMarketDisplays(initialData);
        }, 500);
    }
    
    startTradingSignalSimulation() {
        // Generate new trading signal every 20 seconds
        this.tradingSignalInterval = setInterval(() => {
            const signal = this.generateTradingSignal();
            this.updateTradingSignals(signal);
            
            // Emit event for React components
            this.emit('trading_signal', signal);
            
        }, 20000);
    }
    
    startPerformanceMonitoring() {
        // Update performance metrics every 15 seconds
        this.performanceInterval = setInterval(() => {
            const metrics = this.generatePerformanceMetrics();
            this.updatePerformanceDisplay(metrics);
            
            // Emit event for React components
            this.emit('performance_update', metrics);
            
        }, 15000);
        
        // Initial metrics update
        setTimeout(() => {
            const initialMetrics = this.generatePerformanceMetrics();
            this.updatePerformanceDisplay(initialMetrics);
        }, 1000);
    }
    
    generateMarketData() {
        const indices = {
            'NIFTY 50': {
                value: this.simulatePrice(25041.10),
                change: this.simulateChange()
            },
            'BANK NIFTY': {
                value: this.simulatePrice(51234.80),
                change: this.simulateChange()
            },
            'NIFTY IT': {
                value: this.simulatePrice(43687.25),
                change: this.simulateChange()
            },
            'SENSEX': {
                value: this.simulatePrice(81523.45),
                change: this.simulateChange()
            }
        };
        
        const stocks = {
            'RELIANCE': {
                price: this.simulatePrice(2845.60),
                change: this.simulateChange(),
                volume: `${(Math.random() * 3 + 1).toFixed(1)}M`
            },
            'TCS': {
                price: this.simulatePrice(4125.30),
                change: this.simulateChange(),
                volume: `${(Math.random() * 2 + 0.5).toFixed(1)}M`
            },
            'INFY': {
                price: this.simulatePrice(1756.25),
                change: this.simulateChange(),
                volume: `${(Math.random() * 4 + 1).toFixed(1)}M`
            }
        };
        
        return { indices, stocks, timestamp: new Date().toISOString() };
    }
    
    simulatePrice(basePrice) {
        const variance = (Math.random() - 0.5) * 0.02; // ±1% variance
        const newPrice = basePrice * (1 + variance);
        return newPrice.toLocaleString('en-IN', { 
            minimumFractionDigits: 2, 
            maximumFractionDigits: 2 
        });
    }
    
    simulateChange() {
        const change = (Math.random() - 0.5) * 6; // -3% to +3%
        return parseFloat(change.toFixed(2));
    }
    
    generateTradingSignal() {
        const symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'SBIN', 'ITC', 'WIPRO'];
        const actions = ['BUY', 'SELL', 'HOLD'];
        const strategies = [
            'Momentum Strategy',
            'Mean Reversion',
            'Breakout Pattern',
            'Volume Analysis',
            'Technical Indicator',
            'AI Pattern Recognition'
        ];
        
        return {
            id: Date.now(),
            symbol: symbols[Math.floor(Math.random() * symbols.length)],
            action: actions[Math.floor(Math.random() * actions.length)],
            confidence: Math.floor(Math.random() * 35) + 65, // 65-100%
            strategy: strategies[Math.floor(Math.random() * strategies.length)],
            timestamp: new Date()
        };
    }
    
    generatePerformanceMetrics() {
        return {
            latency: Math.floor(Math.random() * 50) + 10, // 10-60ms
            throughput: Math.floor(Math.random() * 1000) + 500, // 500-1500 req/sec
            memory: Math.floor(Math.random() * 100) + 50, // 50-150MB
            wsConnections: Math.floor(Math.random() * 5) + 2, // 2-7 connections
            lastUpdate: new Date().toLocaleTimeString()
        };
    }
    
    updateMarketDisplays(data) {
        // Update market indices
        const marketCard = document.querySelector('[data-component="realtime-market"]');
        if (marketCard) {
            const cardBody = marketCard.querySelector('.card-body');
            
            // Update card header status
            const statusBadge = marketCard.querySelector('.badge');
            if (statusBadge) {
                statusBadge.className = 'badge bg-success';
                statusBadge.textContent = 'Live Demo';
            }
            
            // Update card content with simulated data
            if (cardBody) {
                cardBody.innerHTML = this.renderMarketData(data);
            }
        }
        
        // Update individual index displays
        Object.entries(data.indices).forEach(([symbol, indexData]) => {
            const elementId = symbol.toLowerCase().replace(' ', '');
            const priceElement = document.getElementById(`${elementId}-price`);
            const changeElement = document.getElementById(`${elementId}-change`);
            
            if (priceElement) priceElement.textContent = indexData.value;
            if (changeElement) {
                const isPositive = indexData.change >= 0;
                changeElement.className = `text-${isPositive ? 'success' : 'danger'}`;
                changeElement.innerHTML = `
                    <i class="fas fa-arrow-${isPositive ? 'up' : 'down'} me-1"></i>
                    ${isPositive ? '+' : ''}${indexData.change}%
                `;
            }
        });
    }
    
    renderMarketData(data) {
        return `
            <div class="row">
                ${Object.entries(data.indices).map(([symbol, indexData]) => `
                    <div class="col-md-6 mb-3">
                        <div class="d-flex justify-content-between align-items-center p-3 bg-light rounded index-card cursor-pointer" 
                             style="transition: all 0.2s ease; border: 1px solid #e1e5e9;">
                            <div>
                                <h6 class="fw-bold mb-1">${symbol}</h6>
                                <small class="text-muted">Live Demo</small>
                            </div>
                            <div class="text-end">
                                <div class="fw-bold fs-5">${indexData.value}</div>
                                <small class="text-${indexData.change >= 0 ? 'success' : 'danger'}">
                                    <i class="fas fa-arrow-${indexData.change >= 0 ? 'up' : 'down'} me-1"></i>
                                    ${indexData.change >= 0 ? '+' : ''}${indexData.change}%
                                </small>
                                <div class="mt-1">
                                    <i class="fas fa-wifi text-success small" title="Live demo data"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    updateTradingSignals(signal) {
        const signalsCard = document.querySelector('[data-component="ai-signals"]');
        if (!signalsCard) return;
        
        const timeline = signalsCard.querySelector('.timeline');
        if (!timeline) return;
        
        // Create new signal item
        const signalItem = document.createElement('div');
        signalItem.className = 'timeline-item mb-3';
        signalItem.innerHTML = `
            <div class="timeline-marker bg-${signal.action === 'BUY' ? 'success' : signal.action === 'SELL' ? 'danger' : 'warning'}"></div>
            <div class="timeline-content">
                <h6 class="mb-1">AI Signal: ${signal.action} ${signal.symbol}</h6>
                <p class="mb-1 small">${signal.strategy} - ${signal.confidence}% confidence</p>
                <small class="text-muted">Just now (Demo)</small>
            </div>
        `;
        
        // Add to beginning of timeline
        timeline.insertBefore(signalItem, timeline.firstChild);
        
        // Keep only latest 5 signals visible
        const items = timeline.querySelectorAll('.timeline-item');
        if (items.length > 5) {
            for (let i = 5; i < items.length; i++) {
                items[i].remove();
            }
        }
    }
    
    updateRealtimeStatus(message, type) {
        const statusElement = document.querySelector('[data-component="realtime-status"] .badge');
        if (statusElement) {
            statusElement.className = `badge bg-${type}`;
            statusElement.textContent = message;
        }
    }
    
    updatePerformanceDisplay(metrics) {
        const metricsElement = document.querySelector('[data-component="performance-metrics"]');
        if (!metricsElement) return;
        
        metricsElement.innerHTML = `
            <div class="d-flex flex-wrap gap-3">
                <small class="text-muted">
                    <i class="fas fa-tachometer-alt me-1"></i>
                    ${metrics.latency}ms latency
                </small>
                <small class="text-muted">
                    <i class="fas fa-memory me-1"></i>
                    ${metrics.memory}MB
                </small>
                <small class="text-muted">
                    <i class="fas fa-plug me-1"></i>
                    ${metrics.wsConnections} connections
                </small>
                <small class="text-muted">Updated: ${metrics.lastUpdate}</small>
            </div>
        `;
    }
    
    // Event system for React-style component communication
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
    }
    
    emit(event, data) {
        const callbacks = this.listeners.get(event);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Demo event handler error:`, error);
                }
            });
        }
    }
}

// Auto-start demo mode disabled - all requests must be user-initiated
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎭 Demo simulator available but not auto-started');
});

function updatePortfolioWithDemoData() {
    // Update portfolio value with realistic demo data
    const portfolioValueElement = document.getElementById('totalPortfolioValue');
    const portfolioChangeElement = document.getElementById('portfolioChange');
    
    if (portfolioValueElement) {
        // Simulate growing portfolio
        const baseValue = 1845680;
        const variance = (Math.random() - 0.4) * 0.05; // Slightly positive bias
        const newValue = Math.floor(baseValue * (1 + variance));
        
        portfolioValueElement.textContent = `₹${newValue.toLocaleString('en-IN')}`;
        
        if (portfolioChangeElement) {
            const change = Math.floor((newValue - baseValue));
            const changePercent = ((change / baseValue) * 100).toFixed(2);
            const isPositive = change >= 0;
            
            portfolioChangeElement.className = `text-${isPositive ? 'success' : 'danger'}`;
            portfolioChangeElement.textContent = `${isPositive ? '+' : ''}₹${Math.abs(change).toLocaleString('en-IN')} (${isPositive ? '+' : ''}${changePercent}%) • Demo`;
        }
    }
    
    // Update other metrics
    const algoTradesElement = document.getElementById('algoTrades');
    if (algoTradesElement) {
        const baseValue = parseInt(algoTradesElement.textContent) || 245;
        const newValue = baseValue + Math.floor(Math.random() * 3); // 0-2 new trades
        algoTradesElement.textContent = newValue;
    }
}

// Export for global access
window.DemoWebSocketSimulator = DemoWebSocketSimulator;