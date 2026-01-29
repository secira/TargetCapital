/**
 * React-style Hooks for Target Capital Trading Platform
 * Simplified for production - all data fetching is user-initiated
 */

// Simple state management
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
                this.listeners.get(key).forEach(cb => cb(nextValue, currentValue));
            }
        };
        
        return [() => this.states.get(key), setState];
    }
};

window.StateManager = StateManager;

// React-style useState hook
function useState(initialValue) {
    const stateId = `state_${Date.now()}_${Math.random()}`;
    return StateManager.createState(stateId, initialValue);
}

// React-style useEffect hook
function useEffect(callback, dependencies = []) {
    let cleanup = null;
    let lastDeps = [];
    
    const runEffect = () => {
        const changed = dependencies.length !== lastDeps.length ||
                       dependencies.some((d, i) => d !== lastDeps[i]);
        
        if (changed) {
            if (cleanup) cleanup();
            cleanup = callback();
            lastDeps = [...dependencies];
        }
    };
    
    runEffect();
    return () => { if (cleanup) cleanup(); };
}

// Notification hook
function useNotifications() {
    const [getNotifications, setNotifications] = useState([]);
    
    const addNotification = (message, type = 'info', duration = 5000) => {
        const notification = { id: Date.now(), message, type, timestamp: new Date() };
        setNotifications(prev => [...(prev || []), notification]);
        
        if (duration > 0) {
            setTimeout(() => removeNotification(notification.id), duration);
        }
        return notification.id;
    };
    
    const removeNotification = (id) => {
        setNotifications(prev => (prev || []).filter(n => n.id !== id));
    };
    
    return { notifications: getNotifications, addNotification, removeNotification };
}

// Export for global usage
window.TargetCapitalHooks = { useState, useEffect, useNotifications };
window.CapitalHooks = window.TargetCapitalHooks;
