/**
 * User Progress Tracking for tCapital Onboarding
 * Tracks learning milestones and engagement
 */

class OnboardingProgressTracker {
    constructor() {
        this.storageKey = 'tcapital_learning_progress';
        this.milestones = this.initializeMilestones();
        this.userProgress = this.loadProgress();
        this.achievements = [];
        this.init();
    }

    init() {
        this.trackPageVisits();
        this.trackFeatureUsage();
        this.bindProgressEvents();
    }

    initializeMilestones() {
        return {
            'first_visit': {
                name: 'Welcome Explorer',
                description: 'First time visiting tCapital',
                points: 10,
                icon: '👋',
                completed: false
            },
            'onboarding_completed': {
                name: 'Platform Navigator',
                description: 'Completed the guided tour',
                points: 50,
                icon: '🗺️',
                completed: false
            },
            'dashboard_explored': {
                name: 'Data Detective',
                description: 'Explored the dashboard features',
                points: 25,
                icon: '📊',
                completed: false
            },
            'ai_advisor_used': {
                name: 'AI Whisperer',
                description: 'Asked your first AI question',
                points: 30,
                icon: '🤖',
                completed: false
            },
            'stock_picker_used': {
                name: 'Stock Hunter',
                description: 'Used the AI Stock Picker',
                points: 35,
                icon: '🎯',
                completed: false
            },
            'broker_connected': {
                name: 'Account Master',
                description: 'Connected your first broker account',
                points: 75,
                icon: '🔗',
                completed: false
            },
            'portfolio_viewed': {
                name: 'Portfolio Pro',
                description: 'Viewed your portfolio analysis',
                points: 40,
                icon: '💼',
                completed: false
            },
            'trading_signals_viewed': {
                name: 'Signal Seeker',
                description: 'Checked trading signals',
                points: 45,
                icon: '📈',
                completed: false
            },
            'learning_streak_3': {
                name: 'Learning Enthusiast',
                description: '3 consecutive days of platform usage',
                points: 100,
                icon: '🔥',
                completed: false
            },
            'learning_streak_7': {
                name: 'Dedication Master',
                description: '7 consecutive days of platform usage',
                points: 200,
                icon: '🏆',
                completed: false
            }
        };
    }

    loadProgress() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            const progress = JSON.parse(saved);
            // Merge with default milestones to handle new additions
            Object.keys(this.milestones).forEach(key => {
                if (progress.milestones && progress.milestones[key]) {
                    this.milestones[key].completed = progress.milestones[key].completed;
                }
            });
            return progress;
        }
        
        return {
            totalPoints: 0,
            level: 1,
            visitDays: [],
            featuresUsed: [],
            milestones: this.milestones,
            startDate: new Date().toISOString()
        };
    }

    saveProgress() {
        this.userProgress.milestones = this.milestones;
        localStorage.setItem(this.storageKey, JSON.stringify(this.userProgress));
    }

    trackPageVisits() {
        const today = new Date().toDateString();
        if (!this.userProgress.visitDays.includes(today)) {
            this.userProgress.visitDays.push(today);
            this.checkStreakMilestones();
            this.saveProgress();
        }

        // Track first visit silently without triggering popups
        if (!this.milestones.first_visit.completed) {
            this.milestones.first_visit.completed = true;
            this.userProgress.totalPoints += this.milestones.first_visit.points;
            this.updateLevel();
            this.saveProgress();
            // Don't show achievement notification for first visit to avoid annoyance
        }
    }

    trackFeatureUsage() {
        // Track dashboard exploration
        if (window.location.pathname.includes('/dashboard') && !this.milestones.dashboard_explored.completed) {
            setTimeout(() => {
                this.completeMilestone('dashboard_explored');
            }, 5000); // After 5 seconds on dashboard
        }

        // Track specific feature usage based on current page
        const pathname = window.location.pathname;
        
        if (pathname.includes('/ai-advisor') && !this.milestones.ai_advisor_used.completed) {
            this.completeMilestone('ai_advisor_used');
        }
        
        if (pathname.includes('/stock-picker') && !this.milestones.stock_picker_used.completed) {
            this.completeMilestone('stock_picker_used');
        }
        
        if (pathname.includes('/trading-signals') && !this.milestones.trading_signals_viewed.completed) {
            this.completeMilestone('trading_signals_viewed');
        }
        
        if (pathname.includes('/portfolio') && !this.milestones.portfolio_viewed.completed) {
            this.completeMilestone('portfolio_viewed');
        }
    }

    bindProgressEvents() {
        // Listen for custom events from other parts of the application
        document.addEventListener('tcapital:onboarding:completed', () => {
            this.completeMilestone('onboarding_completed');
        });

        document.addEventListener('tcapital:broker:connected', () => {
            this.completeMilestone('broker_connected');
        });

        document.addEventListener('tcapital:ai:question_asked', () => {
            if (!this.milestones.ai_advisor_used.completed) {
                this.completeMilestone('ai_advisor_used');
            }
        });
    }

    completeMilestone(milestoneKey) {
        if (this.milestones[milestoneKey] && !this.milestones[milestoneKey].completed) {
            this.milestones[milestoneKey].completed = true;
            this.userProgress.totalPoints += this.milestones[milestoneKey].points;
            this.updateLevel();
            this.showAchievement(this.milestones[milestoneKey]);
            this.saveProgress();
            
            // Notify AI companion about achievement
            if (window.aiCompanion) {
                window.aiCompanion.celebrateAchievement(this.milestones[milestoneKey]);
            }
        }
    }

    updateLevel() {
        const pointsForNextLevel = [0, 100, 300, 600, 1000, 1500, 2200, 3000];
        let newLevel = 1;
        
        for (let i = 0; i < pointsForNextLevel.length; i++) {
            if (this.userProgress.totalPoints >= pointsForNextLevel[i]) {
                newLevel = i + 1;
            }
        }
        
        if (newLevel > this.userProgress.level) {
            this.userProgress.level = newLevel;
            this.showLevelUp(newLevel);
        }
    }

    checkStreakMilestones() {
        const visitDays = this.userProgress.visitDays.sort();
        let currentStreak = 1;
        
        for (let i = visitDays.length - 2; i >= 0; i--) {
            const current = new Date(visitDays[i + 1]);
            const previous = new Date(visitDays[i]);
            const dayDiff = (current - previous) / (1000 * 60 * 60 * 24);
            
            if (dayDiff === 1) {
                currentStreak++;
            } else {
                break;
            }
        }
        
        if (currentStreak >= 3 && !this.milestones.learning_streak_3.completed) {
            this.completeMilestone('learning_streak_3');
        }
        
        if (currentStreak >= 7 && !this.milestones.learning_streak_7.completed) {
            this.completeMilestone('learning_streak_7');
        }
    }

    showAchievement(milestone) {
        // Disable all auto-popup notifications to avoid annoying users
        // Achievements are tracked silently in the background
        return;
    }

    showLevelUp(newLevel) {
        // Disable level up notifications to avoid annoying users
        // Level changes are tracked silently in the background
        return;
    }

    getProgressSummary() {
        const completedMilestones = Object.values(this.milestones).filter(m => m.completed);
        const totalMilestones = Object.values(this.milestones).length;
        
        return {
            level: this.userProgress.level,
            totalPoints: this.userProgress.totalPoints,
            completedMilestones: completedMilestones.length,
            totalMilestones: totalMilestones,
            completionPercentage: Math.round((completedMilestones.length / totalMilestones) * 100),
            currentStreak: this.getCurrentStreak(),
            milestonesDetails: this.milestones
        };
    }

    getCurrentStreak() {
        const visitDays = this.userProgress.visitDays.sort();
        let currentStreak = 1;
        
        for (let i = visitDays.length - 2; i >= 0; i--) {
            const current = new Date(visitDays[i + 1]);
            const previous = new Date(visitDays[i]);
            const dayDiff = (current - previous) / (1000 * 60 * 60 * 24);
            
            if (dayDiff === 1) {
                currentStreak++;
            } else {
                break;
            }
        }
        
        return currentStreak;
    }

    createProgressWidget() {
        const progress = this.getProgressSummary();
        
        const progressHTML = `
            <div class="learning-progress-widget">
                <div class="progress-header">
                    <h5>🎓 Learning Progress</h5>
                    <span class="level-badge">Level ${progress.level}</span>
                </div>
                <div class="progress-stats">
                    <div class="stat">
                        <span class="stat-value">${progress.totalPoints}</span>
                        <span class="stat-label">Points</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${progress.completedMilestones}/${progress.totalMilestones}</span>
                        <span class="stat-label">Achievements</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${progress.currentStreak}</span>
                        <span class="stat-label">Day Streak</span>
                    </div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress.completionPercentage}%"></div>
                </div>
                <p class="progress-text">${progress.completionPercentage}% Complete</p>
            </div>
        `;
        
        return progressHTML;
    }
}

// Initialize progress tracking when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.progressTracker = new OnboardingProgressTracker();
    
    // DISABLED: Learning Progress widget removed per user request
    // The widget was blocking the screen and confusing users
    /*
    // Add progress widget to dashboard if present
    const dashboard = document.querySelector('.dashboard-main');
    if (dashboard && window.location.pathname.includes('/dashboard')) {
        const progressWidget = document.createElement('div');
        progressWidget.innerHTML = window.progressTracker.createProgressWidget();
        progressWidget.className = 'progress-widget-container';
        
        // Insert after the dashboard header
        const dashboardHeader = dashboard.querySelector('.border-bottom');
        if (dashboardHeader) {
            dashboardHeader.insertAdjacentElement('afterend', progressWidget);
        }
    }
    */
});