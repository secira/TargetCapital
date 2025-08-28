/**
 * Mobile Performance Optimization & Progressive Web App Features
 * Production-ready mobile experience enhancements
 */

class MobilePerformanceManager {
    constructor() {
        this.touchStartTime = 0;
        this.scrollTimeout = null;
        this.resizeTimeout = null;
        this.intersectionObserver = null;
        this.performanceMetrics = {};
        
        this.init();
    }
    
    init() {
        console.log('🚀 Initializing mobile performance optimizations');
        
        // Initialize performance monitoring
        this.initPerformanceMonitoring();
        
        // Setup mobile-specific optimizations
        this.setupTouchOptimizations();
        this.setupScrollOptimizations();
        this.setupResizeOptimizations();
        this.setupLazyLoading();
        this.setupPrefetching();
        
        // Initialize PWA features
        this.initPWAFeatures();
        
        // Setup offline handling
        this.setupOfflineHandling();
        
        // Setup adaptive loading
        this.setupAdaptiveLoading();
        
        console.log('✅ Mobile performance optimizations ready');
    }
    
    initPerformanceMonitoring() {
        // Performance Observer for real-time metrics
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.entryType === 'navigation') {
                        this.trackNavigationMetrics(entry);
                    } else if (entry.entryType === 'largest-contentful-paint') {
                        this.trackLCP(entry);
                    } else if (entry.entryType === 'first-input') {
                        this.trackFID(entry);
                    } else if (entry.entryType === 'layout-shift') {
                        this.trackCLS(entry);
                    }
                }
            });
            
            try {
                observer.observe({ entryTypes: ['navigation', 'largest-contentful-paint', 'first-input', 'layout-shift'] });
            } catch (e) {
                console.log('Performance Observer not fully supported');
            }
        }
        
        // Track page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                this.calculatePagePerformance();
            }, 1000);
        });
    }
    
    trackNavigationMetrics(entry) {
        this.performanceMetrics.navigation = {
            dns: entry.domainLookupEnd - entry.domainLookupStart,
            tcp: entry.connectEnd - entry.connectStart,
            ttfb: entry.responseStart - entry.requestStart,
            download: entry.responseEnd - entry.responseStart,
            domLoad: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
            totalLoad: entry.loadEventEnd - entry.loadEventStart
        };
    }
    
    trackLCP(entry) {
        this.performanceMetrics.lcp = entry.startTime;
        console.log(`📊 LCP: ${entry.startTime.toFixed(2)}ms`);
    }
    
    trackFID(entry) {
        this.performanceMetrics.fid = entry.processingStart - entry.startTime;
        console.log(`📊 FID: ${this.performanceMetrics.fid.toFixed(2)}ms`);
    }
    
    trackCLS(entry) {
        if (!this.performanceMetrics.cls) this.performanceMetrics.cls = 0;
        if (!entry.hadRecentInput) {
            this.performanceMetrics.cls += entry.value;
        }
    }
    
    calculatePagePerformance() {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
            const metrics = {
                loadTime: navigation.loadEventEnd - navigation.loadEventStart,
                domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
                firstPaint: this.getFirstPaint(),
                firstContentfulPaint: this.getFirstContentfulPaint()
            };
            
            console.log('📊 Page Performance Metrics:', metrics);
            this.performanceMetrics.page = metrics;
            
            // Emit custom event for analytics
            window.dispatchEvent(new CustomEvent('performance-measured', {
                detail: { metrics: this.performanceMetrics }
            }));
        }
    }
    
    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const fpEntry = paintEntries.find(entry => entry.name === 'first-paint');
        return fpEntry ? fpEntry.startTime : null;
    }
    
    getFirstContentfulPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint');
        return fcpEntry ? fcpEntry.startTime : null;
    }
    
    setupTouchOptimizations() {
        // Prevent 300ms tap delay
        document.addEventListener('touchstart', (e) => {
            this.touchStartTime = Date.now();
        }, { passive: true });
        
        // Fast click implementation
        document.addEventListener('touchend', (e) => {
            const touchDuration = Date.now() - this.touchStartTime;
            if (touchDuration < 200) { // Quick tap
                const target = e.target.closest('[data-fast-click]');
                if (target) {
                    e.preventDefault();
                    target.click();
                }
            }
        }, { passive: false });
        
        // Prevent accidental zooming
        document.addEventListener('touchstart', (e) => {
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });
        
        // Smooth scrolling momentum
        document.addEventListener('touchmove', (e) => {
            const scrollableElement = e.target.closest('.smooth-scroll');
            if (scrollableElement) {
                e.stopPropagation();
            }
        }, { passive: true });
    }
    
    setupScrollOptimizations() {
        let isScrolling = false;
        
        document.addEventListener('scroll', () => {
            if (!isScrolling) {
                requestAnimationFrame(() => {
                    this.handleScroll();
                    isScrolling = false;
                });
                isScrolling = true;
            }
        }, { passive: true });
    }
    
    handleScroll() {
        // Throttled scroll handler
        clearTimeout(this.scrollTimeout);
        this.scrollTimeout = setTimeout(() => {
            // Hide/show navbar on scroll
            this.handleNavbarScroll();
            
            // Update scroll position for components
            this.updateScrollPosition();
            
            // Trigger lazy loading checks
            this.checkLazyLoading();
            
        }, 10);
    }
    
    handleNavbarScroll() {
        const navbar = document.querySelector('.navbar-mobile');
        if (!navbar) return;
        
        const scrollY = window.scrollY;
        const scrollingDown = scrollY > (navbar.dataset.lastScrollY || 0);
        
        if (scrollingDown && scrollY > 100) {
            navbar.classList.add('hidden');
        } else {
            navbar.classList.remove('hidden');
        }
        
        navbar.dataset.lastScrollY = scrollY;
    }
    
    updateScrollPosition() {
        // Update scroll position for interested components
        window.dispatchEvent(new CustomEvent('scroll-update', {
            detail: { scrollY: window.scrollY }
        }));
    }
    
    setupResizeOptimizations() {
        window.addEventListener('resize', () => {
            clearTimeout(this.resizeTimeout);
            this.resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 150);
        });
        
        // Handle orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.handleOrientationChange();
            }, 500);
        });
    }
    
    handleResize() {
        // Recalculate viewport units
        this.updateViewportUnits();
        
        // Update grid layouts
        this.updateResponsiveGrids();
        
        // Emit resize event for components
        window.dispatchEvent(new CustomEvent('viewport-resize', {
            detail: {
                width: window.innerWidth,
                height: window.innerHeight,
                isMobile: window.innerWidth < 768
            }
        }));
    }
    
    handleOrientationChange() {
        // Refresh viewport after orientation change
        this.updateViewportUnits();
        
        // Recalculate component sizes
        window.dispatchEvent(new CustomEvent('orientation-change'));
        
        console.log('📱 Orientation changed, refreshing layout');
    }
    
    updateViewportUnits() {
        // Fix iOS viewport height issues
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    updateResponsiveGrids() {
        const grids = document.querySelectorAll('.grid-responsive');
        grids.forEach(grid => {
            // Force reflow for CSS Grid
            grid.style.display = 'none';
            grid.offsetHeight; // Trigger reflow
            grid.style.display = '';
        });
    }
    
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.intersectionObserver = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            this.loadElement(entry.target);
                            this.intersectionObserver.unobserve(entry.target);
                        }
                    });
                },
                {
                    rootMargin: '50px 0px',
                    threshold: 0.1
                }
            );
            
            // Observe all lazy elements
            document.querySelectorAll('.lazy-load').forEach(el => {
                this.intersectionObserver.observe(el);
            });
        }
    }
    
    loadElement(element) {
        // Handle different types of lazy loading
        if (element.dataset.src) {
            // Lazy load images
            element.src = element.dataset.src;
            element.removeAttribute('data-src');
        }
        
        if (element.dataset.component) {
            // Lazy load components
            this.loadComponent(element);
        }
        
        // Add loaded class for animations
        element.classList.add('loaded');
        
        // Remove lazy-load class
        setTimeout(() => {
            element.classList.remove('lazy-load');
        }, 600);
    }
    
    loadComponent(element) {
        const componentName = element.dataset.component;
        console.log(`📦 Lazy loading component: ${componentName}`);
        
        // Trigger component initialization
        window.dispatchEvent(new CustomEvent('component-load', {
            detail: { element, componentName }
        }));
    }
    
    checkLazyLoading() {
        // Manual fallback for browsers without IntersectionObserver
        if (!this.intersectionObserver) {
            const lazyElements = document.querySelectorAll('.lazy-load');
            lazyElements.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.top < window.innerHeight + 50) {
                    this.loadElement(el);
                }
            });
        }
    }
    
    setupPrefetching() {
        // Prefetch critical resources on interaction
        document.addEventListener('mouseenter', this.handlePrefetch.bind(this), true);
        document.addEventListener('touchstart', this.handlePrefetch.bind(this), true);
    }
    
    handlePrefetch(e) {
        const link = e.target.closest('a[href]');
        if (link && link.host === location.host) {
            this.prefetchPage(link.href);
        }
    }
    
    prefetchPage(url) {
        if (this.prefetchedUrls?.has(url)) return;
        
        if (!this.prefetchedUrls) {
            this.prefetchedUrls = new Set();
        }
        
        // Create prefetch link
        const linkElement = document.createElement('link');
        linkElement.rel = 'prefetch';
        linkElement.href = url;
        document.head.appendChild(linkElement);
        
        this.prefetchedUrls.add(url);
        console.log(`🔮 Prefetching: ${url}`);
    }
    
    initPWAFeatures() {
        // Service Worker registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('✅ SW registered:', registration);
                    this.setupSWUpdates(registration);
                })
                .catch(error => {
                    console.log('❌ SW registration failed:', error);
                });
        }
        
        // Add to homescreen prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallPrompt();
        });
        
        // Handle installed event
        window.addEventListener('appinstalled', () => {
            console.log('✅ PWA installed successfully');
            this.deferredPrompt = null;
        });
    }
    
    setupSWUpdates(registration) {
        registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed') {
                    if (navigator.serviceWorker.controller) {
                        this.showUpdatePrompt();
                    }
                }
            });
        });
    }
    
    showInstallPrompt() {
        // Show custom install prompt
        const installBanner = document.createElement('div');
        installBanner.className = 'install-prompt';
        installBanner.innerHTML = `
            <div class="install-prompt-content">
                <div class="install-prompt-text">
                    <strong>Install tCapital</strong>
                    <small>Get the full app experience</small>
                </div>
                <button class="btn-touch btn-outline install-btn">Install</button>
                <button class="btn-touch btn-secondary dismiss-btn">×</button>
            </div>
        `;
        
        document.body.appendChild(installBanner);
        
        // Handle install button click
        installBanner.querySelector('.install-btn').addEventListener('click', () => {
            if (this.deferredPrompt) {
                this.deferredPrompt.prompt();
                this.deferredPrompt.userChoice.then((choiceResult) => {
                    console.log('Install choice:', choiceResult.outcome);
                    this.deferredPrompt = null;
                    installBanner.remove();
                });
            }
        });
        
        // Handle dismiss button
        installBanner.querySelector('.dismiss-btn').addEventListener('click', () => {
            installBanner.remove();
        });
    }
    
    showUpdatePrompt() {
        // Show update notification
        const updateNotification = document.createElement('div');
        updateNotification.className = 'update-notification';
        updateNotification.innerHTML = `
            <div class="update-content">
                <span>New version available!</span>
                <button class="btn-touch update-btn">Update</button>
            </div>
        `;
        
        document.body.appendChild(updateNotification);
        
        updateNotification.querySelector('.update-btn').addEventListener('click', () => {
            window.location.reload();
        });
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            updateNotification.remove();
        }, 10000);
    }
    
    setupOfflineHandling() {
        window.addEventListener('online', () => {
            console.log('🌐 Back online');
            this.showConnectionStatus('online');
            this.syncOfflineData();
        });
        
        window.addEventListener('offline', () => {
            console.log('📱 Gone offline');
            this.showConnectionStatus('offline');
        });
        
        // Check initial connection status
        if (!navigator.onLine) {
            this.showConnectionStatus('offline');
        }
    }
    
    showConnectionStatus(status) {
        const statusBanner = document.querySelector('.connection-status') || 
                           document.createElement('div');
        statusBanner.className = `connection-status ${status}`;
        
        if (status === 'offline') {
            statusBanner.innerHTML = `
                <div class="status-content">
                    <i class="fas fa-wifi-slash"></i>
                    <span>You're offline. Some features may be limited.</span>
                </div>
            `;
            document.body.appendChild(statusBanner);
        } else {
            statusBanner.innerHTML = `
                <div class="status-content">
                    <i class="fas fa-wifi"></i>
                    <span>Back online!</span>
                </div>
            `;
            setTimeout(() => {
                statusBanner.remove();
            }, 3000);
        }
    }
    
    syncOfflineData() {
        // Sync any offline changes when back online
        console.log('🔄 Syncing offline data...');
        
        // Emit sync event for components to handle
        window.dispatchEvent(new CustomEvent('sync-offline-data'));
    }
    
    setupAdaptiveLoading() {
        // Check connection quality
        if ('connection' in navigator) {
            const connection = navigator.connection;
            
            const updateConnectionInfo = () => {
                const quality = this.getConnectionQuality(connection);
                console.log(`📡 Connection: ${quality}`);
                
                // Adjust loading strategy based on connection
                this.adjustLoadingStrategy(quality);
                
                // Emit connection quality event
                window.dispatchEvent(new CustomEvent('connection-change', {
                    detail: { quality, connection }
                }));
            };
            
            connection.addEventListener('change', updateConnectionInfo);
            updateConnectionInfo(); // Initial check
        }
    }
    
    getConnectionQuality(connection) {
        const { effectiveType, downlink, rtt } = connection;
        
        if (effectiveType === '4g' && downlink > 5) return 'high';
        if (effectiveType === '4g' || (effectiveType === '3g' && downlink > 1)) return 'medium';
        return 'low';
    }
    
    adjustLoadingStrategy(quality) {
        const strategies = {
            high: {
                imageQuality: 'high',
                prefetchEnabled: true,
                animationsEnabled: true,
                backgroundSync: true
            },
            medium: {
                imageQuality: 'medium',
                prefetchEnabled: true,
                animationsEnabled: true,
                backgroundSync: false
            },
            low: {
                imageQuality: 'low',
                prefetchEnabled: false,
                animationsEnabled: false,
                backgroundSync: false
            }
        };
        
        const strategy = strategies[quality];
        
        // Apply strategy to document
        document.documentElement.dataset.connectionQuality = quality;
        document.documentElement.dataset.imageQuality = strategy.imageQuality;
        
        if (!strategy.animationsEnabled) {
            document.documentElement.classList.add('reduced-motion');
        }
        
        console.log(`⚡ Applied ${quality} quality loading strategy`);
    }
    
    // Public API for components
    getPerformanceMetrics() {
        return { ...this.performanceMetrics };
    }
    
    measureComponentLoad(componentName, startTime) {
        const loadTime = performance.now() - startTime;
        console.log(`📊 ${componentName} loaded in ${loadTime.toFixed(2)}ms`);
        
        if (!this.performanceMetrics.components) {
            this.performanceMetrics.components = {};
        }
        this.performanceMetrics.components[componentName] = loadTime;
        
        return loadTime;
    }
    
    reportCustomMetric(name, value, unit = 'ms') {
        console.log(`📊 Custom metric - ${name}: ${value}${unit}`);
        
        if (!this.performanceMetrics.custom) {
            this.performanceMetrics.custom = {};
        }
        this.performanceMetrics.custom[name] = { value, unit, timestamp: Date.now() };
    }
}

// Initialize mobile performance manager
document.addEventListener('DOMContentLoaded', () => {
    window.mobilePerformance = new MobilePerformanceManager();
});

// Export for global access
window.MobilePerformanceManager = MobilePerformanceManager;