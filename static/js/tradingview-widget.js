/**
 * TradingView Chart Widget for tCapital
 * Provides professional charts with NSE data
 */

class tCapitalChartWidget {
    constructor(options) {
        this.containerId = options.containerId;
        this.symbol = options.symbol || 'RELIANCE';
        this.width = options.width || '100%';
        this.height = options.height || 500;
        this.theme = options.theme || 'light';
        this.interval = options.interval || '1D';
        this.toolbar = options.toolbar !== false;
        this.onSymbolChange = options.onSymbolChange || null;
        
        this.widget = null;
        this.datafeed = null;
        
        this.init();
    }

    init() {
        // Check if TradingView library is loaded
        if (typeof TradingView === 'undefined') {
            console.error('TradingView library not loaded');
            this.showError('TradingView library not available');
            return;
        }

        // Initialize datafeed
        this.datafeed = new tCapitalDatafeed();

        // Create widget configuration
        const widgetConfig = {
            width: this.width,
            height: this.height,
            symbol: this.symbol,
            interval: this.interval,
            container_id: this.containerId,
            datafeed: this.datafeed,
            library_path: '/static/charting_library/',
            locale: 'en',
            disabled_features: this.getDisabledFeatures(),
            enabled_features: this.getEnabledFeatures(),
            charts_storage_url: null,
            charts_storage_api_version: '1.1',
            client_id: 'tCapital',
            user_id: 'public_user',
            fullscreen: false,
            autosize: this.width === '100%',
            theme: this.theme,
            custom_css_url: '/static/css/tradingview-custom.css',
            loading_screen: {
                backgroundColor: '#ffffff',
                foregroundColor: '#000000'
            },
            favorites: {
                intervals: ['1', '5', '15', '30', '60', '1D', '1W', '1M'],
                chartTypes: ['Area', 'Line', 'Candles', 'Bars']
            }
        };

        try {
            // Create the widget
            this.widget = new TradingView.widget(widgetConfig);

            // Set up event handlers
            this.setupEventHandlers();

        } catch (error) {
            console.error('Error creating TradingView widget:', error);
            this.showError('Failed to load chart');
        }
    }

    setupEventHandlers() {
        if (!this.widget) return;

        // Widget ready event
        this.widget.onChartReady(() => {
            console.log('TradingView chart is ready');
            
            // Get chart object
            const chart = this.widget.chart();
            
            // Set up symbol change handler
            if (this.onSymbolChange) {
                chart.onSymbolChanged().subscribe(null, (symbolInfo) => {
                    this.onSymbolChange(symbolInfo);
                });
            }
        });
    }

    getDisabledFeatures() {
        return [
            // Remove features we don't need
            'study_templates',
            'volume_force_overlay',
            'left_toolbar',
            'header_compare',
            'header_symbol_search',
            'symbol_search_hot_key',
            'header_resolutions',
            'header_chart_type',
            'header_settings',
            'header_indicators',
            'header_screenshot',
            'header_fullscreen_button'
        ];
    }

    getEnabledFeatures() {
        return [
            'study_templates',
            'side_toolbar_in_fullscreen_mode',
            'header_in_fullscreen_mode'
        ];
    }

    // Change symbol programmatically
    changeSymbol(newSymbol, interval = null) {
        if (this.widget && this.widget.chart) {
            this.symbol = newSymbol;
            this.widget.chart().setSymbol(newSymbol, interval || this.interval);
        }
    }

    // Change interval
    changeInterval(newInterval) {
        if (this.widget && this.widget.chart) {
            this.interval = newInterval;
            this.widget.chart().setResolution(newInterval);
        }
    }

    // Show error message
    showError(message) {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `
                <div class="chart-error" style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: ${this.height}px;
                    background: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    color: #6c757d;
                    font-family: 'Inter', sans-serif;
                    text-align: center;
                ">
                    <div>
                        <i class="fas fa-chart-line fa-3x mb-3" style="color: #dee2e6;"></i>
                        <p style="margin: 0; font-size: 16px;">${message}</p>
                    </div>
                </div>
            `;
        }
    }

    // Destroy widget
    destroy() {
        if (this.widget && typeof this.widget.remove === 'function') {
            this.widget.remove();
        }
        this.widget = null;
        this.datafeed = null;
    }
}

// Price display widget for real-time prices
class tCapitalPriceWidget {
    constructor(options) {
        this.containerId = options.containerId;
        this.symbol = options.symbol || 'RELIANCE';
        this.showChange = options.showChange !== false;
        this.showVolume = options.showVolume !== false;
        this.updateInterval = options.updateInterval || 10000; // 10 seconds
        
        this.currentPrice = null;
        this.updateTimer = null;
        
        this.init();
    }

    init() {
        this.createPriceDisplay();
        this.startUpdates();
    }

    createPriceDisplay() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="price-widget" style="
                padding: 16px;
                background: white;
                border: 1px solid #e1e7ef;
                border-radius: 8px;
                font-family: 'Inter', sans-serif;
            ">
                <div class="price-header" style="
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 8px;
                ">
                    <h6 style="margin: 0; font-weight: 600; color: #0d1117;">${this.symbol}</h6>
                    <button class="btn-chart btn btn-sm btn-outline-primary" style="font-size: 12px;">
                        <i class="fas fa-chart-line me-1"></i>Chart
                    </button>
                </div>
                <div class="price-data">
                    <div class="price-main" style="
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        margin-bottom: 4px;
                    ">
                        <span class="current-price" style="
                            font-size: 24px;
                            font-weight: 700;
                            color: #0d1117;
                        ">Loading...</span>
                        <span class="price-change" style="
                            font-size: 14px;
                            font-weight: 500;
                            padding: 2px 6px;
                            border-radius: 4px;
                        "></span>
                    </div>
                    ${this.showVolume ? `
                    <div class="volume-info" style="
                        font-size: 12px;
                        color: #656d76;
                    ">
                        Volume: <span class="current-volume">-</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add chart button handler
        const chartBtn = container.querySelector('.btn-chart');
        if (chartBtn) {
            chartBtn.addEventListener('click', () => {
                this.showChart();
            });
        }
    }

    startUpdates() {
        // Get initial price
        this.updatePrice();
        
        // Set up periodic updates
        this.updateTimer = setInterval(() => {
            this.updatePrice();
        }, this.updateInterval);
    }

    async updatePrice() {
        try {
            const response = await fetch(`/api/tradingview/realtime?symbol=${encodeURIComponent(this.symbol)}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayPrice(data);
            }
        } catch (error) {
            console.error('Price update error:', error);
        }
    }

    displayPrice(data) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const priceElement = container.querySelector('.current-price');
        const changeElement = container.querySelector('.price-change');
        const volumeElement = container.querySelector('.current-volume');

        if (priceElement) {
            priceElement.textContent = `₹${data.price.toFixed(2)}`;
        }

        if (changeElement && this.showChange) {
            const change = data.change;
            const changePercent = data.change_percent;
            const isPositive = change >= 0;
            
            changeElement.textContent = `${isPositive ? '+' : ''}${change.toFixed(2)} (${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`;
            changeElement.style.color = isPositive ? '#16a34a' : '#dc2626';
            changeElement.style.backgroundColor = isPositive ? '#dcfce7' : '#fef2f2';
        }

        if (volumeElement && this.showVolume) {
            volumeElement.textContent = data.volume.toLocaleString();
        }
    }

    showChart() {
        // Create modal or redirect to chart page
        const modalId = `chart-modal-${this.symbol}`;
        
        // Create modal if it doesn't exist
        if (!document.getElementById(modalId)) {
            const modal = document.createElement('div');
            modal.id = modalId;
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${this.symbol} - Live Chart</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-0">
                            <div id="chart-container-${this.symbol}" style="height: 500px;"></div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        // Show modal
        const modalElement = document.getElementById(modalId);
        const modal = new bootstrap.Modal(modalElement);
        modal.show();

        // Initialize chart when modal is shown
        modalElement.addEventListener('shown.bs.modal', () => {
            new tCapitalChartWidget({
                containerId: `chart-container-${this.symbol}`,
                symbol: this.symbol,
                height: 500
            });
        });
    }

    changeSymbol(newSymbol) {
        this.symbol = newSymbol;
        
        // Update display
        const container = document.getElementById(this.containerId);
        if (container) {
            const headerElement = container.querySelector('.price-widget h6');
            if (headerElement) {
                headerElement.textContent = newSymbol;
            }
        }
        
        // Update price immediately
        this.updatePrice();
    }

    destroy() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }
    }
}

// Export for global use
window.tCapitalChartWidget = tCapitalChartWidget;
window.tCapitalPriceWidget = tCapitalPriceWidget;