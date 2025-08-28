/**
 * Mobile Navigation Enhancement
 * Touch-optimized navigation for mobile devices
 */

class MobileNavigation {
    constructor() {
        this.isMenuOpen = false;
        this.touchStartY = 0;
        this.scrollThreshold = 100;
        this.lastScrollY = 0;
        
        this.init();
    }
    
    init() {
        this.setupMobileMenu();
        this.setupNavbarScroll();
        this.setupTouchGestures();
        this.setupKeyboardNavigation();
        
        console.log('📱 Mobile navigation initialized');
    }
    
    setupMobileMenu() {
        // Create mobile menu button if it doesn't exist
        this.ensureMobileMenuButton();
        
        // Handle menu toggle
        const menuBtn = document.querySelector('.mobile-menu-btn, .navbar-toggler');
        const navCollapse = document.querySelector('#navbarNav, .navbar-collapse');
        
        if (menuBtn && navCollapse) {
            menuBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleMobileMenu();
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (this.isMenuOpen && e.target && typeof e.target.closest === 'function' && !e.target.closest('.navbar')) {
                    this.closeMobileMenu();
                }
            });
            
            // Close menu on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isMenuOpen) {
                    this.closeMobileMenu();
                }
            });
        }
        
        // Handle dropdown menus on mobile
        this.setupMobileDropdowns();
    }
    
    ensureMobileMenuButton() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        let menuBtn = navbar.querySelector('.mobile-menu-btn');
        if (!menuBtn) {
            menuBtn = navbar.querySelector('.navbar-toggler');
            if (menuBtn) {
                menuBtn.classList.add('mobile-menu-btn');
            }
        }
        
        if (menuBtn) {
            // Ensure proper ARIA attributes
            menuBtn.setAttribute('aria-label', 'Toggle navigation menu');
            menuBtn.setAttribute('aria-expanded', 'false');
            menuBtn.setAttribute('aria-controls', 'navbarNav');
        }
    }
    
    setupMobileDropdowns() {
        const dropdownToggles = document.querySelectorAll('.nav-link.dropdown-toggle');
        
        dropdownToggles.forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                if (window.innerWidth < 992) { // Mobile/tablet breakpoint
                    e.preventDefault();
                    this.toggleDropdown(toggle);
                }
            });
        });
    }
    
    toggleDropdown(toggle) {
        const dropdown = toggle.nextElementSibling;
        if (!dropdown) return;
        
        const isOpen = dropdown.classList.contains('show');
        
        // Close all other dropdowns
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            if (menu !== dropdown) {
                menu.classList.remove('show');
                menu.previousElementSibling?.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Toggle current dropdown
        if (isOpen) {
            dropdown.classList.remove('show');
            toggle.setAttribute('aria-expanded', 'false');
        } else {
            dropdown.classList.add('show');
            toggle.setAttribute('aria-expanded', 'true');
        }
    }
    
    toggleMobileMenu() {
        const menuBtn = document.querySelector('.mobile-menu-btn, .navbar-toggler');
        const navCollapse = document.querySelector('#navbarNav, .navbar-collapse');
        
        if (!menuBtn || !navCollapse) return;
        
        this.isMenuOpen = !this.isMenuOpen;
        
        if (this.isMenuOpen) {
            this.openMobileMenu();
        } else {
            this.closeMobileMenu();
        }
    }
    
    openMobileMenu() {
        const menuBtn = document.querySelector('.mobile-menu-btn, .navbar-toggler');
        const navCollapse = document.querySelector('#navbarNav, .navbar-collapse');
        
        navCollapse.classList.add('show', 'collapsing');
        menuBtn.classList.add('active');
        menuBtn.setAttribute('aria-expanded', 'true');
        
        // Add backdrop for better UX
        this.createBackdrop();
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Focus management
        setTimeout(() => {
            const firstLink = navCollapse.querySelector('a');
            firstLink?.focus();
        }, 300);
        
        // Remove collapsing class after animation
        setTimeout(() => {
            navCollapse.classList.remove('collapsing');
        }, 350);
        
        this.isMenuOpen = true;
    }
    
    closeMobileMenu() {
        const menuBtn = document.querySelector('.mobile-menu-btn, .navbar-toggler');
        const navCollapse = document.querySelector('#navbarNav, .navbar-collapse');
        
        navCollapse.classList.add('collapsing');
        navCollapse.classList.remove('show');
        menuBtn.classList.remove('active');
        menuBtn.setAttribute('aria-expanded', 'false');
        
        // Remove backdrop
        this.removeBackdrop();
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Close all dropdowns
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
            menu.previousElementSibling?.setAttribute('aria-expanded', 'false');
        });
        
        // Remove collapsing class after animation
        setTimeout(() => {
            navCollapse.classList.remove('collapsing');
        }, 350);
        
        this.isMenuOpen = false;
    }
    
    createBackdrop() {
        if (document.querySelector('.mobile-nav-backdrop')) return;
        
        const backdrop = document.createElement('div');
        backdrop.className = 'mobile-nav-backdrop';
        backdrop.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1020;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(backdrop);
        
        // Trigger animation
        requestAnimationFrame(() => {
            backdrop.style.opacity = '1';
        });
        
        // Close menu when backdrop is clicked
        backdrop.addEventListener('click', () => {
            this.closeMobileMenu();
        });
    }
    
    removeBackdrop() {
        const backdrop = document.querySelector('.mobile-nav-backdrop');
        if (backdrop) {
            backdrop.style.opacity = '0';
            setTimeout(() => {
                backdrop.remove();
            }, 300);
        }
    }
    
    setupNavbarScroll() {
        let ticking = false;
        
        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.updateNavbarOnScroll();
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    updateNavbarOnScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        const currentScrollY = window.scrollY;
        const scrollingDown = currentScrollY > this.lastScrollY;
        const scrolledPastThreshold = currentScrollY > this.scrollThreshold;
        
        // Hide/show navbar based on scroll direction
        if (scrollingDown && scrolledPastThreshold && !this.isMenuOpen) {
            navbar.classList.add('navbar-hidden');
        } else if (!scrollingDown || currentScrollY <= this.scrollThreshold) {
            navbar.classList.remove('navbar-hidden');
        }
        
        // Add shadow when scrolled
        if (currentScrollY > 10) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
        
        this.lastScrollY = currentScrollY;
    }
    
    setupTouchGestures() {
        let startY = 0;
        let currentY = 0;
        let isDragging = false;
        
        document.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
            isDragging = false;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (!startY) return;
            
            currentY = e.touches[0].clientY;
            const deltaY = startY - currentY;
            
            // Detect significant vertical swipe
            if (Math.abs(deltaY) > 50) {
                isDragging = true;
                
                // Swipe up - hide navbar
                if (deltaY > 0 && window.scrollY > this.scrollThreshold) {
                    const navbar = document.querySelector('.navbar');
                    navbar?.classList.add('navbar-hidden');
                }
                
                // Swipe down - show navbar
                if (deltaY < 0) {
                    const navbar = document.querySelector('.navbar');
                    navbar?.classList.remove('navbar-hidden');
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            startY = 0;
            currentY = 0;
            isDragging = false;
        }, { passive: true });
    }
    
    setupKeyboardNavigation() {
        // Enhanced keyboard navigation for accessibility
        document.addEventListener('keydown', (e) => {
            const navbar = document.querySelector('.navbar');
            if (!navbar) return;
            
            // Tab navigation enhancement
            if (e.key === 'Tab') {
                this.handleTabNavigation(e);
            }
            
            // Arrow key navigation in dropdowns
            if (['ArrowDown', 'ArrowUp', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
                this.handleArrowNavigation(e);
            }
            
            // Enter/Space for dropdown toggles
            if ((e.key === 'Enter' || e.key === ' ') && e.target.classList.contains('dropdown-toggle')) {
                e.preventDefault();
                this.toggleDropdown(e.target);
            }
        });
    }
    
    handleTabNavigation(e) {
        const focusableElements = document.querySelectorAll(
            '.navbar a, .navbar button, .navbar [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        // Trap focus within navbar when menu is open
        if (this.isMenuOpen) {
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }
    
    handleArrowNavigation(e) {
        const activeElement = document.activeElement;
        
        // Navigation within dropdown menus
        if (activeElement.closest('.dropdown-menu')) {
            e.preventDefault();
            const dropdown = activeElement.closest('.dropdown-menu');
            const items = dropdown.querySelectorAll('a, button');
            const currentIndex = Array.from(items).indexOf(activeElement);
            
            let nextIndex;
            if (e.key === 'ArrowDown') {
                nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
            } else if (e.key === 'ArrowUp') {
                nextIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
            }
            
            if (nextIndex !== undefined) {
                items[nextIndex].focus();
            }
        }
        
        // Navigation between main nav items
        if (activeElement.closest('.navbar-nav') && !activeElement.closest('.dropdown-menu')) {
            const navItems = document.querySelectorAll('.navbar-nav > .nav-item > a, .navbar-nav > .nav-item > button');
            const currentIndex = Array.from(navItems).indexOf(activeElement);
            
            let nextIndex;
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                nextIndex = currentIndex < navItems.length - 1 ? currentIndex + 1 : 0;
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                nextIndex = currentIndex > 0 ? currentIndex - 1 : navItems.length - 1;
            }
            
            if (nextIndex !== undefined) {
                e.preventDefault();
                navItems[nextIndex].focus();
            }
        }
    }
    
    // Public API
    
    openMenu() {
        if (!this.isMenuOpen) {
            this.toggleMobileMenu();
        }
    }
    
    closeMenu() {
        if (this.isMenuOpen) {
            this.toggleMobileMenu();
        }
    }
    
    isMenuActive() {
        return this.isMenuOpen;
    }
}

// Add required CSS for mobile navigation
const mobileNavCSS = `
    .navbar-hidden {
        transform: translateY(-100%) !important;
        transition: transform 0.3s ease;
    }
    
    .navbar-scrolled {
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.95) !important;
    }
    
    .mobile-menu-btn.active span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }
    
    .mobile-menu-btn.active span:nth-child(2) {
        opacity: 0;
    }
    
    .mobile-menu-btn.active span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -6px);
    }
    
    @media (max-width: 991.98px) {
        .navbar-collapse {
            position: fixed;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            max-height: calc(100vh - 80px);
            overflow-y: auto;
            z-index: 1021;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .navbar-collapse.show {
            transform: translateX(0);
        }
        
        .navbar-collapse.collapsing {
            transition: transform 0.35s ease;
        }
        
        .dropdown-menu.show {
            display: block;
            position: static;
            float: none;
            width: auto;
            margin-top: 0;
            background-color: rgba(0, 0, 0, 0.02);
            border: none;
            border-radius: 0;
            box-shadow: none;
        }
        
        .nav-link.dropdown-toggle::after {
            transition: transform 0.3s ease;
        }
        
        .nav-link.dropdown-toggle[aria-expanded="true"]::after {
            transform: rotate(180deg);
        }
    }
    
    /* Touch target optimization */
    @media (max-width: 991.98px) {
        .navbar-nav .nav-link {
            padding: 1rem 1.5rem !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .dropdown-item {
            padding: 0.75rem 2rem !important;
        }
    }
`;

// Inject CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = mobileNavCSS;
document.head.appendChild(styleSheet);

// Initialize mobile navigation
document.addEventListener('DOMContentLoaded', () => {
    window.mobileNav = new MobileNavigation();
});

// Export for global access
window.MobileNavigation = MobileNavigation;