/**
 * React-style Hooks for tCapital Trading Platform
 * Provides React-like state management and effects for enhanced scalability
 */

// Simple state management system
if (!window.StateManager) {
const StateManager = {
    states: new Map(),
    listeners: new Map(),
    
    createState(key, initialValue) {
        this.states.set(key, initialValue);
        this.listeners.set(key, new Set());
        
        const setState = (newValue) => {
            const currentValue = this.states.get(key);
            const nextValue = typeof newValue === 'function' ? newValue(currentValue) : newValue;
            
            if (nextValue !== currentValue) {
                this.states.set(key, nextValue);
                this.notifyListeners(key, nextValue, currentValue);
            }
        };
        
        const getState = () => this.states.get(key);
        
        const subscribe = (callback) => {
            this.listeners.get(key).add(callback);
            return () => this.listeners.get(key).delete(callback);
        };
        
        return [getState, setState, subscribe];
    },
    
    notifyListeners(key, newValue, oldValue) {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(newValue, oldValue);
                } catch (error) {
                    console.error(`State listener error for ${key}:`, error);
                }
            });
        }
    }
};
window.StateManager = StateManager;
}

// React-style useState hook
function useState(initialValue) {
    const stateId = `state_${Date.now()}_${Math.random()}`;
    return StateManager.createState(stateId, initialValue);
}

// React-style useEffect hook
function useEffect(callback, dependencies = []) {
    const effectId = `effect_${Date.now()}_${Math.random()}`;
    let cleanup = null;
    let lastDependencies = [];
    
    const runEffect = () => {
        // Check if dependencies changed
        const depsChanged = dependencies.length !== lastDependencies.length ||
                           dependencies.some((dep, index) => dep !== lastDependencies[index]);
        
        if (depsChanged) {
            // Cleanup previous effect
            if (cleanup && typeof cleanup === 'function') {
                cleanup();
            }
            
            // Run new effect
            cleanup = callback();
            lastDependencies = [...dependencies];
        }
    };
    
    // Run immediately
    runEffect();
    
    // Return cleanup function
    return () => {
        if (cleanup && typeof cleanup === 'function') {
            cleanup();
        }
    };
}

// Market Data Hook with React-style API
function useMarketDataStream(symbols = []) {
    const [getMarketData, setMarketData] = useState({});
    const [getConnectionState, setConnectionState] = useState('disconnected');
    const [getLastUpdate, setLastUpdate] = useState(null);
    
    useEffect(() => {
        const ws = new WebSocketClient({
            url: 'ws://localhost:8001',
            autoReconnect: true
        });
        
        ws.on('open', () => {
            setConnectionState('connected');
            // Subscribe to symbols
            ws.send({
                type: 'subscribe',
                symbols: symbols
            });
        });
        
        ws.on('close', () => setConnectionState('disconnected'));
        ws.on('connecting', () => setConnectionState('connecting'));
        ws.on('error', () => setConnectionState('error'));
        
        ws.on('message', (data) => {
            if (data.type === 'market_data') {
                setMarketData(prev => ({ ...prev(), ...data.data }));
                setLastUpdate(new Date().toLocaleTimeString());
            }
        });
        
        ws.connect();
        
        // Cleanup function
        return () => {
            ws.disconnect();
        };
    }, [JSON.stringify(symbols)]);
    
    return {
        marketData: getMarketData(),
        connectionState: getConnectionState(),
        lastUpdate: getLastUpdate(),
        subscribe: (newSymbols) => {
            // Update subscription
        }
    };
}

// Portfolio Hook with real-time updates
function usePortfolioData(userId) {
    const [getPortfolio, setPortfolio] = useState({});
    const [getIsLoading, setIsLoading] = useState(true);
    const [getError, setError] = useState(null);
    
    useEffect(() => {
        let ws = null;
        
        const loadInitialData = async () => {
            try {
                // OAUTH DEBUG: Skip portfolio API call temporarily
                console.log('🔄 OAuth callback mode - skipping portfolio data load in hooks');
                setIsLoading(false);
                return;
            } catch (error) {
                setError('Failed to load portfolio data');
            } finally {
                setIsLoading(false);
            }
        };
        
        const connectWebSocket = () => {
            ws = new WebSocketClient({
                url: 'ws://localhost:8003',
                autoReconnect: true
            });
            
            ws.on('message', (data) => {
                if (data.type === 'portfolio_update' && data.userId === userId) {
                    setPortfolio(prev => ({ ...prev(), ...data.portfolio }));
                }
            });
            
            ws.connect();
        };
        
        loadInitialData();
        connectWebSocket();
        
        return () => {
            if (ws) {
                ws.disconnect();
            }
        };
    }, [userId]);
    
    return {
        portfolio: getPortfolio(),
        isLoading: getIsLoading(),
        error: getError()
    };
}

// Trading Orders Hook
function useTradingOrders(userId) {
    const [getOrders, setOrders] = useState([]);
    const [getPendingOrders, setPendingOrders] = useState([]);
    const [getIsSubmitting, setIsSubmitting] = useState(false);
    
    const submitOrder = async (orderData) => {
        setIsSubmitting(true);
        
        try {
            const response = await fetch('http://localhost:8000/api/orders', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    ...orderData,
                    userId: userId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Add to pending orders for immediate UI feedback
                setPendingOrders(prev => [...prev(), {
                    ...orderData,
                    id: result.orderId,
                    status: 'pending',
                    timestamp: new Date().toISOString()
                }]);
                
                return { success: true, orderId: result.orderId };
            } else {
                throw new Error(result.message || 'Order submission failed');
            }
            
        } catch (error) {
            console.error('Order submission error:', error);
            return { success: false, error: error.message };
        } finally {
            setIsSubmitting(false);
        }
    };
    
    // Listen for order updates via WebSocket
    useEffect(() => {
        const ws = new WebSocketClient({
            url: 'ws://localhost:8002',
            autoReconnect: true
        });
        
        ws.on('message', (data) => {
            if (data.type === 'order_update' && data.userId === userId) {
                setOrders(prev => {
                    const updated = [...prev()];
                    const index = updated.findIndex(o => o.id === data.order.id);
                    
                    if (index >= 0) {
                        updated[index] = data.order;
                    } else {
                        updated.push(data.order);
                    }
                    
                    return updated;
                });
                
                // Remove from pending if completed
                if (data.order.status !== 'pending') {
                    setPendingOrders(prev => 
                        prev().filter(o => o.id !== data.order.id)
                    );
                }
            }
        });
        
        ws.connect();
        
        return () => ws.disconnect();
    }, [userId]);
    
    return {
        orders: getOrders(),
        pendingOrders: getPendingOrders(),
        isSubmitting: getIsSubmitting(),
        submitOrder
    };
}

// AI Analysis Hook
function useAIAnalysis() {
    const [getAnalysis, setAnalysis] = useState({});
    const [getIsAnalyzing, setIsAnalyzing] = useState(false);
    
    const analyzeSymbol = async (symbol, analysisType = 'comprehensive') => {
        setIsAnalyzing(true);
        
        try {
            const response = await fetch('/api/ai-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol: symbol,
                    analysis_type: analysisType
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                setAnalysis(prev => ({
                    ...prev(),
                    [symbol]: result.analysis
                }));
                return result.analysis;
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            console.error('AI analysis error:', error);
            return { error: error.message };
        } finally {
            setIsAnalyzing(false);
        }
    };
    
    return {
        analysis: getAnalysis(),
        isAnalyzing: getIsAnalyzing(),
        analyzeSymbol
    };
}

// Performance monitoring hook
function usePerformanceMonitor() {
    const [getMetrics, setMetrics] = useState({});
    
    useEffect(() => {
        const monitor = () => {
            const metrics = {
                connectionTime: performance.timing.connectEnd - performance.timing.connectStart,
                domLoadTime: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                pageLoadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                memory: performance.memory ? {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit
                } : null
            };
            
            setMetrics(metrics);
        };
        
        // Monitor performance after page load
        if (document.readyState === 'complete') {
            monitor();
        } else {
            window.addEventListener('load', monitor);
        }
        
        // Monitor performance every 30 seconds
        const interval = setInterval(monitor, 30000);
        
        return () => {
            clearInterval(interval);
            window.removeEventListener('load', monitor);
        };
    }, []);
    
    return getMetrics();
}

// Real-time notifications hook
function useNotifications() {
    const [getNotifications, setNotifications] = useState([]);
    
    const addNotification = (message, type = 'info', duration = 5000) => {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date()
        };
        
        setNotifications(prev => [...prev(), notification]);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                removeNotification(notification.id);
            }, duration);
        }
        
        return notification.id;
    };
    
    const removeNotification = (id) => {
        setNotifications(prev => prev().filter(n => n.id !== id));
    };
    
    const clearAll = () => {
        setNotifications([]);
    };
    
    return {
        notifications: getNotifications(),
        addNotification,
        removeNotification,
        clearAll
    };
}

// Connection status hook for multiple WebSockets
function useConnectionStatus() {
    const [getStatuses, setStatuses] = useState({});
    
    const updateStatus = (serviceName, status) => {
        setStatuses(prev => ({
            ...prev(),
            [serviceName]: status
        }));
    };
    
    const isAllConnected = () => {
        const statuses = getStatuses();
        return Object.values(statuses).every(status => status === 'connected');
    };
    
    const getOverallStatus = () => {
        const statuses = Object.values(getStatuses());
        
        if (statuses.every(s => s === 'connected')) return 'connected';
        if (statuses.some(s => s === 'connecting')) return 'connecting';
        if (statuses.some(s => s === 'error')) return 'error';
        return 'disconnected';
    };
    
    return {
        statuses: getStatuses(),
        updateStatus,
        isAllConnected,
        overallStatus: getOverallStatus()
    };
}

// Export hooks and utilities
window.tCapitalHooks = {
    useState,
    useEffect,
    useMarketDataStream,
    usePortfolioData,
    useTradingOrders,
    useAIAnalysis,
    usePerformanceMonitor,
    useNotifications,
    useConnectionStatus,
    StateManager
};

// Auto-initialize performance monitoring
document.addEventListener('DOMContentLoaded', () => {
    // Start global performance monitoring
    const performanceHook = usePerformanceMonitor();
    
    // Log performance metrics
    setTimeout(() => {
        console.log('📊 Performance Metrics:', performanceHook);
    }, 2000);
});
}