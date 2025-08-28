/**
 * Dashboard Mobile Enhancements
 * Specific mobile optimizations for the dashboard interface
 */

class DashboardMobileEnhancements {
    constructor() {
        this.sidebarOpen = false;
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.swipeThreshold = 50;
        this.isInitialized = false;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        this.setupMobileSidebar();
        this.setupSwipeGestures();
        this.setupResponsiveGrid();
        this.setupMobileCards();
        this.setupTabNavigation();
        this.setupPullToRefresh();
        
        this.isInitialized = true;
        console.log('📱 Dashboard mobile enhancements initialized');
    }
    
    setupMobileSidebar() {
        // Create mobile sidebar toggle button
        this.createSidebarToggle();
        
        // Handle sidebar interactions
        const sidebar = document.querySelector('.dashboard-sidebar');
        if (!sidebar) return;
        
        // Close sidebar when clicking outside (mobile only)
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 768 && this.sidebarOpen && e.target && typeof e.target.closest === 'function') {
                if (!e.target.closest('.dashboard-sidebar') && !e.target.closest('.sidebar-toggle')) {
                    this.closeSidebar();
                }
            }
        });
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidebarOpen) {
                this.closeSidebar();
            }
        });
    }
    
    createSidebarToggle() {
        // Check if toggle already exists
        if (document.querySelector('.sidebar-toggle')) return;
        
        const dashboardHeader = document.querySelector('.dashboard-heading')?.parentElement;
        if (!dashboardHeader) return;
        
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'btn btn-outline-secondary sidebar-toggle d-md-none me-3';
        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
        toggleBtn.setAttribute('aria-label', 'Toggle sidebar menu');
        toggleBtn.addEventListener('click', () => this.toggleSidebar());
        
        // Insert at the beginning of the header
        dashboardHeader.insertBefore(toggleBtn, dashboardHeader.firstChild);
    }
    
    toggleSidebar() {
        if (this.sidebarOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }
    
    openSidebar() {
        const sidebar = document.querySelector('.dashboard-sidebar');
        if (!sidebar) return;
        
        sidebar.classList.add('open');
        this.sidebarOpen = true;
        
        // Create backdrop
        this.createSidebarBackdrop();
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Update toggle button
        const toggle = document.querySelector('.sidebar-toggle i');
        if (toggle) {
            toggle.className = 'fas fa-times';
        }
        
        // Announce to screen readers
        this.announceToScreenReader('Sidebar opened');
    }
    
    closeSidebar() {
        const sidebar = document.querySelector('.dashboard-sidebar');
        if (!sidebar) return;
        
        sidebar.classList.remove('open');
        this.sidebarOpen = false;
        
        // Remove backdrop
        this.removeSidebarBackdrop();
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Update toggle button
        const toggle = document.querySelector('.sidebar-toggle i');
        if (toggle) {
            toggle.className = 'fas fa-bars';
        }
        
        // Announce to screen readers
        this.announceToScreenReader('Sidebar closed');
    }
    
    createSidebarBackdrop() {
        // Remove existing backdrop
        this.removeSidebarBackdrop();
        
        const backdrop = document.createElement('div');
        backdrop.className = 'sidebar-backdrop';
        backdrop.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1019;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(backdrop);
        
        // Trigger animation
        requestAnimationFrame(() => {
            backdrop.style.opacity = '1';
        });
        
        // Close sidebar when backdrop is clicked
        backdrop.addEventListener('click', () => this.closeSidebar());
    }
    
    removeSidebarBackdrop() {
        const backdrop = document.querySelector('.sidebar-backdrop');
        if (backdrop) {
            backdrop.style.opacity = '0';
            setTimeout(() => backdrop.remove(), 300);
        }
    }
    
    setupSwipeGestures() {
        let startX = 0;
        let startY = 0;
        let currentX = 0;
        let currentY = 0;
        let isDragging = false;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isDragging = false;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
            
            const deltaX = startX - currentX;
            const deltaY = startY - currentY;
            
            // Check if this is a horizontal swipe
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > this.swipeThreshold) {
                isDragging = true;
                
                // Swipe right - open sidebar (from left edge)
                if (deltaX < 0 && startX < 50 && !this.sidebarOpen) {
                    this.openSidebar();
                }
                
                // Swipe left - close sidebar
                if (deltaX > 0 && this.sidebarOpen) {
                    this.closeSidebar();
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            startX = 0;
            startY = 0;
            currentX = 0;
            currentY = 0;
            isDragging = false;
        }, { passive: true });
    }
    
    setupResponsiveGrid() {
        // Enhance the grid system for mobile
        const grids = document.querySelectorAll('.grid-responsive');
        
        grids.forEach(grid => {
            // Add mobile-specific classes
            grid.classList.add('mobile-optimized');
            
            // Handle grid item reordering on mobile
            this.optimizeGridForMobile(grid);
        });
        
        // Update grid on resize
        window.addEventListener('resize', this.debounce(() => {
            grids.forEach(grid => this.optimizeGridForMobile(grid));
        }, 250));
    }
    
    optimizeGridForMobile(grid) {
        const isMobile = window.innerWidth < 768;
        const items = grid.querySelectorAll('.grid-item');
        
        items.forEach((item, index) => {
            if (isMobile) {
                // Add mobile-specific ordering and styling
                item.style.order = this.getMobileOrder(item, index);
                item.classList.add('mobile-item');
                
                // Add touch-friendly interactions
                this.makeTouchFriendly(item);
            } else {
                // Reset for desktop
                item.style.order = '';
                item.classList.remove('mobile-item');
            }
        });
    }
    
    getMobileOrder(item, defaultOrder) {
        // Prioritize important cards on mobile
        if (item.querySelector('#totalPortfolioValue')) return 0; // Portfolio value first
        if (item.querySelector('#algoTrades')) return 1; // Algo trades second
        return defaultOrder + 2; // Others follow
    }
    
    makeTouchFriendly(item) {
        // Add touch feedback
        item.addEventListener('touchstart', () => {
            item.style.transform = 'scale(0.98)';
        }, { passive: true });
        
        item.addEventListener('touchend', () => {
            item.style.transform = '';
        }, { passive: true });
        
        item.addEventListener('touchcancel', () => {
            item.style.transform = '';
        }, { passive: true });
    }
    
    setupMobileCards() {
        const cards = document.querySelectorAll('.card-responsive, .card');
        
        cards.forEach(card => {
            // Add mobile-specific enhancements
            this.enhanceCardForMobile(card);
        });
    }
    
    enhanceCardForMobile(card) {
        // Add loading states
        this.addLoadingState(card);
        
        // Add error handling
        this.addErrorHandling(card);
        
        // Add refresh capability
        this.addPullToRefreshToCard(card);
        
        // Optimize text for mobile
        this.optimizeTextForMobile(card);
    }
    
    addLoadingState(card) {
        const loadingHTML = `
            <div class="card-loading" style="display: none;">
                <div class="d-flex justify-content-center align-items-center py-4">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <small class="text-muted">Updating...</small>
                </div>
            </div>
        `;
        
        card.insertAdjacentHTML('beforeend', loadingHTML);
    }
    
    addErrorHandling(card) {
        const errorHTML = `
            <div class="card-error" style="display: none;">
                <div class="alert alert-warning mb-0">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <small>Update failed. <a href="javascript:void(0)" class="retry-link">Retry</a></small>
                </div>
            </div>
        `;
        
        card.insertAdjacentHTML('beforeend', errorHTML);
        
        // Handle retry clicks
        const retryLink = card.querySelector('.retry-link');
        if (retryLink) {
            retryLink.addEventListener('click', () => {
                this.retryCardUpdate(card);
            });
        }
    }
    
    retryCardUpdate(card) {
        // Show loading state
        this.showCardLoading(card);
        
        // Emit retry event for components to handle
        window.dispatchEvent(new CustomEvent('card-retry', {
            detail: { card }
        }));
        
        // Auto-hide loading after timeout
        setTimeout(() => {
            this.hideCardLoading(card);
        }, 3000);
    }
    
    showCardLoading(card) {
        const loading = card.querySelector('.card-loading');
        const error = card.querySelector('.card-error');
        
        if (loading) loading.style.display = 'block';
        if (error) error.style.display = 'none';
    }
    
    hideCardLoading(card) {
        const loading = card.querySelector('.card-loading');
        if (loading) loading.style.display = 'none';
    }
    
    showCardError(card) {
        const loading = card.querySelector('.card-loading');
        const error = card.querySelector('.card-error');
        
        if (loading) loading.style.display = 'none';
        if (error) error.style.display = 'block';
    }
    
    addPullToRefreshToCard(card) {
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        let pullDistance = 0;
        const pullThreshold = 80;
        
        card.addEventListener('touchstart', (e) => {
            if (card.scrollTop === 0) {
                startY = e.touches[0].clientY;
            }
        }, { passive: true });
        
        card.addEventListener('touchmove', (e) => {
            if (!startY) return;
            
            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;
            
            if (pullDistance > 0 && card.scrollTop === 0) {
                isPulling = true;
                e.preventDefault();
                
                // Visual feedback
                const scale = Math.min(1 + pullDistance / 300, 1.1);
                card.style.transform = `scale(${scale})`;
                
                if (pullDistance > pullThreshold) {
                    card.classList.add('pull-to-refresh-ready');
                }
            }
        }, { passive: false });
        
        card.addEventListener('touchend', () => {
            if (isPulling && pullDistance > pullThreshold) {
                this.triggerCardRefresh(card);
            }
            
            // Reset
            card.style.transform = '';
            card.classList.remove('pull-to-refresh-ready');
            startY = 0;
            currentY = 0;
            isPulling = false;
            pullDistance = 0;
        }, { passive: true });
    }
    
    triggerCardRefresh(card) {
        // Show loading state
        this.showCardLoading(card);
        
        // Emit refresh event
        window.dispatchEvent(new CustomEvent('card-refresh', {
            detail: { card }
        }));
        
        // Auto-hide loading
        setTimeout(() => {
            this.hideCardLoading(card);
        }, 2000);
    }
    
    optimizeTextForMobile(card) {
        // Make text more readable on mobile
        const headings = card.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const paragraphs = card.querySelectorAll('p, small');
        
        headings.forEach(heading => {
            heading.style.lineHeight = '1.2';
            heading.style.marginBottom = '0.5rem';
        });
        
        paragraphs.forEach(p => {
            p.style.lineHeight = '1.4';
        });
    }
    
    setupTabNavigation() {
        // Enhanced tab navigation for touch devices
        const tabs = document.querySelectorAll('.nav-tabs .nav-link');
        
        tabs.forEach(tab => {
            // Add touch feedback
            tab.addEventListener('touchstart', () => {
                tab.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
            }, { passive: true });
            
            tab.addEventListener('touchend', () => {
                setTimeout(() => {
                    tab.style.backgroundColor = '';
                }, 150);
            }, { passive: true });
            
            // Swipe between tabs
            this.addSwipeToTab(tab);
        });
    }
    
    addSwipeToTab(tab) {
        let startX = 0;
        let currentX = 0;
        
        tab.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        }, { passive: true });
        
        tab.addEventListener('touchmove', (e) => {
            currentX = e.touches[0].clientX;
        }, { passive: true });
        
        tab.addEventListener('touchend', () => {
            const deltaX = startX - currentX;
            
            if (Math.abs(deltaX) > this.swipeThreshold) {
                const tabs = Array.from(document.querySelectorAll('.nav-tabs .nav-link'));
                const currentIndex = tabs.indexOf(tab);
                
                let targetIndex;
                if (deltaX > 0 && currentIndex < tabs.length - 1) {
                    targetIndex = currentIndex + 1; // Swipe left - next tab
                } else if (deltaX < 0 && currentIndex > 0) {
                    targetIndex = currentIndex - 1; // Swipe right - previous tab
                }
                
                if (targetIndex !== undefined) {
                    tabs[targetIndex].click();
                }
            }
            
            startX = 0;
            currentX = 0;
        }, { passive: true });
    }
    
    setupPullToRefresh() {
        // Global pull-to-refresh for the entire dashboard
        let startY = 0;
        let currentY = 0;
        let isPulling = false;
        let pullDistance = 0;
        const pullThreshold = 100;
        
        const dashboardMain = document.querySelector('.dashboard-main');
        if (!dashboardMain) return;
        
        dashboardMain.addEventListener('touchstart', (e) => {
            if (dashboardMain.scrollTop === 0) {
                startY = e.touches[0].clientY;
            }
        }, { passive: true });
        
        dashboardMain.addEventListener('touchmove', (e) => {
            if (!startY) return;
            
            currentY = e.touches[0].clientY;
            pullDistance = currentY - startY;
            
            if (pullDistance > 0 && dashboardMain.scrollTop === 0) {
                isPulling = true;
                
                // Visual feedback
                if (pullDistance > 20) {
                    this.showPullIndicator(pullDistance, pullThreshold);
                }
            }
        }, { passive: true });
        
        dashboardMain.addEventListener('touchend', () => {
            if (isPulling && pullDistance > pullThreshold) {
                this.triggerDashboardRefresh();
            }
            
            this.hidePullIndicator();
            
            // Reset
            startY = 0;
            currentY = 0;
            isPulling = false;
            pullDistance = 0;
        }, { passive: true });
    }
    
    showPullIndicator(distance, threshold) {
        let indicator = document.querySelector('.pull-to-refresh-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'pull-to-refresh-indicator';
            indicator.style.cssText = `
                position: fixed;
                top: 80px;
                left: 50%;
                transform: translateX(-50%);
                background: white;
                border-radius: 20px;
                padding: 10px 20px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 1000;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            `;
            document.body.appendChild(indicator);
        }
        
        const isReady = distance >= threshold;
        const progress = Math.min(distance / threshold, 1);
        
        indicator.innerHTML = `
            <div class="spinner-border spinner-border-sm" role="status" style="font-size: 12px; transform: rotate(${progress * 360}deg)">
                <span class="visually-hidden">Loading...</span>
            </div>
            <small>${isReady ? 'Release to refresh' : 'Pull to refresh'}</small>
        `;
        
        indicator.style.opacity = Math.min(progress, 1);
        indicator.style.transform = `translateX(-50%) scale(${0.8 + progress * 0.2})`;
    }
    
    hidePullIndicator() {
        const indicator = document.querySelector('.pull-to-refresh-indicator');
        if (indicator) {
            indicator.style.opacity = '0';
            indicator.style.transform = 'translateX(-50%) scale(0.8)';
            setTimeout(() => indicator.remove(), 300);
        }
    }
    
    triggerDashboardRefresh() {
        console.log('📱 Dashboard refresh triggered');
        
        // Show global loading indicator
        this.showGlobalLoading();
        
        // Emit refresh event for all components
        window.dispatchEvent(new CustomEvent('dashboard-refresh'));
        
        // Hide loading after timeout
        setTimeout(() => {
            this.hideGlobalLoading();
        }, 2000);
    }
    
    showGlobalLoading() {
        const loading = document.createElement('div');
        loading.className = 'global-loading';
        loading.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-color, #0066cc);
            color: white;
            border-radius: 20px;
            padding: 10px 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1001;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        `;
        loading.innerHTML = `
            <div class="spinner-border spinner-border-sm text-light" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            Refreshing dashboard...
        `;
        document.body.appendChild(loading);
    }
    
    hideGlobalLoading() {
        const loading = document.querySelector('.global-loading');
        if (loading) {
            loading.style.opacity = '0';
            setTimeout(() => loading.remove(), 300);
        }
    }
    
    // Utility methods
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.classList.add('visually-hidden');
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            announcement.remove();
        }, 1000);
    }
    
    // Public API
    
    refreshDashboard() {
        this.triggerDashboardRefresh();
    }
    
    openSidebarMobile() {
        if (window.innerWidth < 768) {
            this.openSidebar();
        }
    }
    
    closeSidebarMobile() {
        if (window.innerWidth < 768) {
            this.closeSidebar();
        }
    }
    
    isSidebarOpen() {
        return this.sidebarOpen;
    }
}

// Initialize dashboard mobile enhancements
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardMobile = new DashboardMobileEnhancements();
});

// Export for global access
window.DashboardMobileEnhancements = DashboardMobileEnhancements;