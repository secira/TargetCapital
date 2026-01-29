/**
 * Advanced WebSocket Client for Target Capital
 * React-style WebSocket management with automatic reconnection and state management
 */

class WebSocketClient {
    constructor(options = {}) {
        this.url = options.url;
        this.protocols = options.protocols || [];
        this.autoReconnect = options.autoReconnect !== false;
        this.reconnectInterval = options.reconnectInterval || 1000;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        this.heartbeatInterval = options.heartbeatInterval || 30000;
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.messageQueue = [];
        this.listeners = new Map();
        this.connectionState = 'disconnected';
        this.heartbeatTimer = null;
        
        // Bind methods
        this.connect = this.connect.bind(this);
        this.disconnect = this.disconnect.bind(this);
        this.send = this.send.bind(this);
        this.on = this.on.bind(this);
        this.off = this.off.bind(this);
    }
    
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            return Promise.resolve();
        }
        
        return new Promise((resolve, reject) => {
            try {
                console.log(`🔌 Connecting to WebSocket: ${this.url}`);
                this.connectionState = 'connecting';
                this.emit('connecting');
                
                this.ws = new WebSocket(this.url, this.protocols);
                
                this.ws.onopen = (event) => {
                    console.log(`✅ WebSocket connected: ${this.url}`);
                    this.connectionState = 'connected';
                    this.reconnectAttempts = 0;
                    this.reconnectInterval = 1000; // Reset interval
                    
                    // Send queued messages
                    this.flushMessageQueue();
                    
                    // Start heartbeat
                    this.startHeartbeat();
                    
                    this.emit('open', event);
                    resolve();
                };
                
                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        
                        // Handle heartbeat responses
                        if (data.type === 'pong') {
                            return;
                        }
                        
                        this.emit('message', data, event);
                        
                        // Emit specific message type events
                        if (data.type) {
                            this.emit(data.type, data, event);
                        }
                        
                    } catch (error) {
                        console.error('WebSocket message parse error:', error);
                        this.emit('error', error);
                    }
                };
                
                this.ws.onclose = (event) => {
                    console.log(`🔌 WebSocket disconnected: ${this.url}`);
                    this.connectionState = 'disconnected';
                    this.stopHeartbeat();
                    
                    this.emit('close', event);
                    
                    // Auto-reconnect if enabled and not a clean close
                    if (this.autoReconnect && !event.wasClean) {
                        this.scheduleReconnect();
                    }
                };
                
                this.ws.onerror = (error) => {
                    console.error(`❌ WebSocket error: ${this.url}`, error);
                    this.connectionState = 'error';
                    this.emit('error', error);
                    reject(error);
                };
                
                // Connection timeout
                setTimeout(() => {
                    if (this.connectionState === 'connecting') {
                        this.ws.close();
                        reject(new Error('WebSocket connection timeout'));
                    }
                }, 10000);
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    disconnect() {
        this.autoReconnect = false;
        this.stopHeartbeat();
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.connectionState = 'disconnected';
        this.emit('disconnect');
    }
    
    send(data) {
        const message = JSON.stringify(data);
        
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
            return true;
        } else {
            // Queue message for when connection is restored
            this.messageQueue.push(message);
            
            // Attempt to connect if not connecting
            if (this.connectionState === 'disconnected') {
                this.connect();
            }
            
            return false;
        }
    }
    
    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(message);
            }
        }
    }
    
    scheduleReconnect() {
        // Auto-reconnect disabled to ensure connections are user-driven
        console.log('🔄 Auto-reconnect disabled');
    }
    
    startHeartbeat() {
        // Heartbeat disabled
    }
    
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    // Event system
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
        
        return () => this.off(event, callback); // Return unsubscribe function
    }
    
    off(event, callback) {
        const callbacks = this.listeners.get(event);
        if (callbacks) {
            callbacks.delete(callback);
        }
    }
    
    emit(event, ...args) {
        const callbacks = this.listeners.get(event);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(...args);
                } catch (error) {
                    console.error(`WebSocket event handler error for ${event}:`, error);
                }
            });
        }
    }
    
    // Getters
    get readyState() {
        return this.ws ? this.ws.readyState : WebSocket.CLOSED;
    }
    
    get isConnected() {
        return this.readyState === WebSocket.OPEN;
    }
    
    get state() {
        return {
            connectionState: this.connectionState,
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            queuedMessages: this.messageQueue.length
        };
    }
}

// React-style hook simulation for WebSocket
function useWebSocket(url, options = {}) {
    const client = new WebSocketClient({ url, ...options });
    
    // Auto-connect
    client.connect().catch(console.error);
    
    return {
        send: client.send,
        disconnect: client.disconnect,
        on: client.on,
        off: client.off,
        state: client.state,
        client
    };
}

// Market Data WebSocket Hook
function useMarketData(symbols = []) {
    const [marketData, setMarketData] = useState({});
    const [connectionState, setConnectionState] = useState('disconnected');
    
    const ws = useWebSocket('ws://localhost:8001', {
        onOpen: () => {
            setConnectionState('connected');
            // Subscribe to symbols
            ws.send({
                type: 'subscribe',
                symbols: symbols
            });
        },
        onClose: () => setConnectionState('disconnected'),
        onMessage: (data) => {
            if (data.type === 'market_data') {
                setMarketData(prev => ({ ...prev, ...data.data }));
            }
        }
    });
    
    return { marketData, connectionState, subscribe: ws.send };
}

// Trading WebSocket Hook
function useTradingUpdates() {
    const [orders, setOrders] = useState([]);
    const [portfolio, setPortfolio] = useState({});
    const [connectionState, setConnectionState] = useState('disconnected');
    
    const ws = useWebSocket('ws://localhost:8002', {
        onOpen: () => setConnectionState('connected'),
        onClose: () => setConnectionState('disconnected'),
        onMessage: (data) => {
            switch (data.type) {
                case 'order_update':
                    setOrders(prev => {
                        const updated = [...prev];
                        const index = updated.findIndex(o => o.id === data.order.id);
                        if (index >= 0) {
                            updated[index] = data.order;
                        } else {
                            updated.push(data.order);
                        }
                        return updated;
                    });
                    break;
                case 'portfolio_update':
                    setPortfolio(data.portfolio);
                    break;
            }
        }
    });
    
    return { orders, portfolio, connectionState, placeOrder: ws.send };
}

// Simple state management (React useState simulation)
function useState(initialValue) {
    let value = initialValue;
    const listeners = new Set();
    
    const setValue = (newValue) => {
        const oldValue = value;
        value = typeof newValue === 'function' ? newValue(oldValue) : newValue;
        
        // Notify all listeners
        listeners.forEach(listener => listener(value, oldValue));
    };
    
    const subscribe = (listener) => {
        listeners.add(listener);
        return () => listeners.delete(listener);
    };
    
    return [
        () => value,
        setValue,
        subscribe
    ];
}

// Export for global usage
window.Target CapitalWebSocket = {
    WebSocketClient,
    useWebSocket,
    useMarketData,
    useTradingUpdates,
    useState
};