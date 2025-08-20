/**
 * TradingView Widget Integration for tCapital
 * Provides embedded TradingView charts without requiring API credentials
 */

class TradingViewWidget {
    constructor() {
        this.widgetConfigs = {
            default: {
                height: 500,
                colorTheme: "light",
                isTransparent: false,
                locale: "en",
                timezone: "Asia/Kolkata",
                toolbar_bg: "#f1f3f6",
                enable_publishing: false,
                hide_top_toolbar: false,
                hide_legend: false,
                save_image: true,
                studies: ["RSI", "MACD", "BB"],
                theme: "Light"
            }
        };
    }

    /**
     * Create TradingView widget for NSE stocks
     */
    createStockWidget(containerId, symbol, options = {}) {
        const config = {
            ...this.widgetConfigs.default,
            ...options,
            container_id: containerId,
            symbol: `NSE:${symbol}`,
            interval: "D",
            range: "6M",
            allow_symbol_change: false,
            details: false,
            hotlist: false,
            calendar: false,
            hide_legend: true,
            studies: [
                "RSI",
                "MACD", 
                "BB",
                "Volume"
            ],
            disabled_features: [
                "use_localstorage_for_settings",
                "study_templates",
                "popup_hints",
                "show_logo",
                "show_powered_by",
                "header_symbol_search",
                "symbol_search_hot_key",
                "header_resolutions",
                "header_chart_type",
                "header_settings",
                "header_indicators",
                "header_compare",
                "header_undo_redo",
                "header_screenshot",
                "header_fullscreen_button"
            ]
        };

        // Create the widget script
        const script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://s3.tradingview.com/tv.js';
        script.async = true;
        script.onload = () => {
            new TradingView.widget(config);
        };

        // Clear container and add script
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
            container.appendChild(script);
        }
    }

    /**
     * Create TradingView widget for NSE indices
     */
    createIndexWidget(containerId, indexSymbol, options = {}) {
        const indexMap = {
            'NIFTY 50': 'NSE:NIFTY',
            'BANK NIFTY': 'NSE:BANKNIFTY',
            'NIFTY BANK': 'NSE:BANKNIFTY',
            'NIFTY IT': 'NSE:CNXIT',
            'NIFTY AUTO': 'NSE:CNXAUTO'
        };

        const symbol = indexMap[indexSymbol] || 'NSE:NIFTY';
        
        const config = {
            ...this.widgetConfigs.default,
            ...options,
            container_id: containerId,
            symbol: symbol,
            interval: "15",
            range: "1D",
            allow_symbol_change: false,
            details: false,
            hotlist: false,
            calendar: false,
            hide_legend: true,
            disabled_features: [
                "use_localstorage_for_settings",
                "study_templates", 
                "popup_hints",
                "show_logo",
                "show_powered_by",
                "header_symbol_search",
                "symbol_search_hot_key",
                "header_resolutions",
                "header_chart_type",
                "header_settings",
                "header_indicators",
                "header_compare",
                "header_undo_redo",
                "header_screenshot",
                "header_fullscreen_button"
            ]
        };

        this.loadWidget(config);
    }

    /**
     * Create simple embedded chart widget
     */
    createEmbeddedWidget(containerId, symbol, height = 400) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Create iframe for TradingView chart with notifications disabled
        const iframe = document.createElement('iframe');
        iframe.src = `https://www.tradingview.com/widgetembed/?frameElementId=tradingview_widget&symbol=NSE%3A${symbol}&interval=D&hidesidetoolbar=1&hidetoptoolbar=1&symboledit=0&saveimage=0&toolbarbg=f1f3f6&studies=%5B%5D&theme=Light&style=1&timezone=Asia%2FKolkata&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%22use_localstorage_for_settings%22%2C%22study_templates%22%2C%22popup_hints%22%2C%22show_logo%22%2C%22show_powered_by%22%2C%22header_symbol_search%22%2C%22symbol_search_hot_key%22%2C%22header_resolutions%22%2C%22header_chart_type%22%2C%22header_settings%22%2C%22header_indicators%22%2C%22header_compare%22%2C%22header_undo_redo%22%2C%22header_screenshot%22%2C%22header_fullscreen_button%22%2C%22left_toolbar%22%2C%22header_widget%22%2C%22timeframes_toolbar%22%2C%22edit_buttons_in_legend%22%2C%22context_menus%22%2C%22control_bar%22%2C%22border_around_the_chart%22%5D&locale=en&utm_source=localhost&utm_medium=widget_new&utm_campaign=chart&utm_term=NSE%3A${symbol}&hide_legend=1&allow_symbol_change=0&details=0&calendar=0&hide_volume=0&hide_top_toolbar=1&hide_side_toolbar=1`;
        iframe.width = '100%';
        iframe.height = height + 'px';
        iframe.frameBorder = '0';
        iframe.allowTransparency = 'true';
        iframe.scrolling = 'no';
        iframe.style.border = 'none';

        container.innerHTML = '';
        container.appendChild(iframe);
        
        // Add event listener to hide any TradingView notifications after load
        iframe.onload = () => {
            try {
                // Hide any remaining TradingView notifications
                setTimeout(() => {
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    if (iframeDoc) {
                        const style = iframeDoc.createElement('style');
                        style.textContent = `
                            .tv-dialog, .tv-dialog__section, .tv-toast, .tv-notifications,
                            .tv-floating-tooltip, .tv-popup-widget, .tv-chart-view__watermark,
                            .tv-symbol-header__text-button, .tv-header__area-right,
                            .tv-header__logo, .tv-footer, .tv-toast-logger,
                            [data-name="legend-source-item"], .tv-toast-logger__item,
                            .tv-floating-tooltip__body { display: none !important; }
                        `;
                        iframeDoc.head.appendChild(style);
                    }
                }, 1000);
            } catch (e) {
                // Cross-origin restrictions - notifications handled by URL parameters
            }
        };
    }

    /**
     * Load widget with configuration
     */
    loadWidget(config) {
        if (typeof TradingView !== 'undefined') {
            new TradingView.widget(config);
        } else {
            // Load TradingView library if not already loaded
            const script = document.createElement('script');
            script.type = 'text/javascript';
            script.src = 'https://s3.tradingview.com/tv.js';
            script.async = true;
            script.onload = () => {
                new TradingView.widget(config);
            };
            document.head.appendChild(script);
        }
    }

    /**
     * Create market overview widget
     */
    createMarketOverviewWidget(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="tradingview-widget-container">
                <div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
                {
                    "colorTheme": "light",
                    "dateRange": "12M",
                    "showChart": true,
                    "locale": "en",
                    "width": "100%",
                    "height": "400",
                    "largeChartUrl": "",
                    "isTransparent": false,
                    "showSymbolLogo": true,
                    "showFloatingTooltip": false,
                    "plotLineColorGrowing": "rgba(41, 98, 255, 1)",
                    "plotLineColorFalling": "rgba(41, 98, 255, 1)",
                    "gridLineColor": "rgba(240, 243, 250, 0)",
                    "scaleFontColor": "rgba(106, 109, 120, 1)",
                    "belowLineFillColorGrowing": "rgba(41, 98, 255, 0.12)",
                    "belowLineFillColorFalling": "rgba(41, 98, 255, 0.12)",
                    "belowLineFillColorGrowingBottom": "rgba(41, 98, 255, 0)",
                    "belowLineFillColorFallingBottom": "rgba(41, 98, 255, 0)",
                    "symbolActiveColor": "rgba(41, 98, 255, 0.12)",
                    "tabs": [
                        {
                            "title": "Indian Indices",
                            "symbols": [
                                {"s": "NSE:NIFTY", "d": "NIFTY 50"},
                                {"s": "NSE:BANKNIFTY", "d": "BANK NIFTY"},
                                {"s": "NSE:CNXIT", "d": "NIFTY IT"},
                                {"s": "NSE:CNXAUTO", "d": "NIFTY AUTO"}
                            ],
                            "originalTitle": "Indices"
                        },
                        {
                            "title": "Top Stocks",
                            "symbols": [
                                {"s": "NSE:RELIANCE", "d": "Reliance Industries"},
                                {"s": "NSE:TCS", "d": "TCS"},
                                {"s": "NSE:HDFCBANK", "d": "HDFC Bank"},
                                {"s": "NSE:INFY", "d": "Infosys"},
                                {"s": "NSE:ICICIBANK", "d": "ICICI Bank"}
                            ],
                            "originalTitle": "Stocks"
                        }
                    ]
                }
                </script>
            </div>
        `;
    }
}

// Global instance
window.TradingViewWidget = new TradingViewWidget();

// Utility functions for easy integration
window.showTradingViewChart = function(symbol, type = 'stock') {
    const modalId = `tradingview-modal-${symbol.replace(/\s+/g, '-').toLowerCase()}`;
    
    // Remove existing modal if any
    const existingModal = document.getElementById(modalId);
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create new modal
    const modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${symbol} - Professional Chart</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-0">
                    <div id="tradingview-chart-${symbol.replace(/\s+/g, '-').toLowerCase()}" style="height: 500px;"></div>
                </div>
                <div class="modal-footer">
                    <small class="text-muted">
                        <i class="fas fa-info-circle me-1"></i>
                        Powered by TradingView Professional Charts
                    </small>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Load chart after modal is shown
    modal.addEventListener('shown.bs.modal', () => {
        const chartContainer = `tradingview-chart-${symbol.replace(/\s+/g, '-').toLowerCase()}`;
        if (type === 'index') {
            window.TradingViewWidget.createIndexWidget(chartContainer, symbol);
        } else {
            window.TradingViewWidget.createEmbeddedWidget(chartContainer, symbol, 500);
        }
    });
};