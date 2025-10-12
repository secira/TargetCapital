# Target Capital - Flask Web Application

## Overview
Target Capital is a Flask-based web application providing an advanced Agentic AI-powered stock trading platform. Its core purpose is to offer autonomous portfolio analysis, algorithmic trading services, and market insights through a modern, responsive interface. The platform emphasizes true autonomous decision-making that learns, reasons, acts, and adapts in real-market conditions, moving beyond passive automation to intelligent, adaptive financial decision-making. The project vision includes significant market potential for intelligent, adaptive financial decision-making tools.

## User Preferences
Preferred communication style: Simple, everyday language.
Brand name: Target Capital
Design preference: Clean white backgrounds instead of blue gradients
Navigation bar: Custom dark navy background color #00091a
Typography: Modern Poppins font throughout the website
Payment Integration: Razorpay payment system fully integrated with updated pricing (Trader ₹1,999, Trader Plus ₹2,999, Premium ₹4,999)
New Feature: Comprehensive Agentic AI system with multi-agent architecture and n8n workflow integration for autonomous trading and portfolio analysis
Core Concept: Agentic AI represents shift from passive automation to true autonomous decision-making with learn, reason, act, adapt capabilities
Agentic AI Implementation: Complete integration with OpenAI (GPT-4) and Perplexity APIs for real-time reasoning and research capabilities
n8n Integration: Workflow automation for continuous monitoring and autonomous decision-making triggers
Dashboard Layout: Two-column layout with left sidebar for trading tools navigation
Manual changes accepted for project integration and navigation structure
All manual changes accepted and integrated (August 2025)
Comprehensive mobile and tablet compatibility enhancement
Mobile responsive design improvements with detailed breakpoints implemented
Typography standardization implemented across all dashboard pages
Comprehensive Agentic AI system implemented with OpenAI and Perplexity integration
n8n workflow integration added for autonomous AI decision-making and monitoring
AI Advisor dashboard enhanced with real-time workflow triggers and status monitoring
Full backend implementation for agentic AI-powered investment analysis
Perplexity AI integration completed for Stock Picker enhanced Indian market research
Enhanced dashboard completely redesigned with dynamic financial overview
New dashboard sidebar with broker connection status and AI monitoring features
Comprehensive 12-broker integration system implemented with full API support
Portfolio overview cards showing total value, algo trades, active strategies, and account handling
Real-time Indian market overview with NSE indices and performance tracking
Top holdings display with portfolio allocation percentages and progress bars
AI market intelligence with sentiment analysis and automated recommendations
Quick actions panel for streamlined navigation to key trading functions
AI-Powered Investment Explanation Chatbot implemented with comprehensive features
Enhanced Stock Picker page with two comprehensive sections: AI Stock Picker and Today's Top AI Picks
Real-time NSE Data Integration and TradingView Professional Charts Implementation
Removed TradingView notification messages by creating custom chart implementation
AI Advisor completely restructured with Perplexity Sonar integration
Comprehensive Portfolio management system with multi-broker support and database integration
Dashboard system cleanup: Removed Watchlist menu item and functionality
Unified dashboard navigation with consistent left sidebar layout across all menu items
Updated Trade Now page template structure to match other dashboard pages for visual consistency
Removed Stock Analysis menu and functionality - charts now work wherever stocks/indices are displayed
Moved AI Advisor menu item below Account Handling in sidebar navigation
Restructured AI Advisor interface layout: search input as main focal point, advanced functions moved to right sidebar
Removed redundant welcome screen text box to eliminate user confusion - now uses single text input box at bottom consistently
UI/UX improvements for AI Advisor text input: 40 characters width, 3 lines height, fixed size to prevent collapse, removed "Thinking" text, colorful "New Chat" button below text box, changed up arrow to "Send" button
Fixed sidebar navigation to correctly point to AI Advisor (/dashboard/ai-advisor) instead of AI Chat - ensuring users access the proper Perplexity-style interface
UI/UX improvements: Removed Market Opportunities and Risk Factors sections from Stock Picker page
Streamlined dashboard interface by removing Quick Actions section from main dashboard
Cleaned up Trade Now page by removing duplicate Refresh and Algo Setup buttons
Complete Trading Signal System with Admin Module and WhatsApp/Telegram Integration implemented
Comprehensive Broker Management System Fully Fixed and Operational: Fixed database model compatibility, encryption key management, foreign key constraints, and API integration for seamless broker account addition with all 12 brokers supported
Unified Portfolio Analyzer System Implemented: Complete AI-powered portfolio analysis with multi-broker data syncing, manual holdings upload, risk profiling questionnaire, comprehensive portfolio health scoring, sector/asset allocation analysis, risk metrics calculation, AI-driven recommendations, and rebalancing suggestions
Razorpay Payment System Integration: Complete payment processing with subscription management, secure checkout flow, payment verification, success/failure handling, billing history, admin panel, and webhook support. Pricing updated to Target Plus ₹1,999, Target Pro ₹2,999, Premium ₹4,999
Updated Subscription Model: Target Plus users can connect 1 broker for portfolio analysis only (no trading); Target Pro supports up to 3 brokers with trade execution limited to 1 primary broker; HNI Account supports unlimited brokers with trade execution limited to 1 primary broker; pricing structure optimized for user growth path
**Multi-Asset Portfolio System**: Complete implementation supporting 11 asset classes (Equities, Mutual Funds, Fixed Income, F&O, NPS, Real Estate, Gold, ETFs, Crypto, ESOP, Private Equity) with unified views across up to 3 brokers, asset-specific filtering, real-time market data integration, comprehensive test suite (200+ test cases), performance optimization with strategic database indexing, and production-ready deployment with safe database migrations
**Knowledge Base Implementation**: Renamed "Blog" to "Knowledge Base" with 5 comprehensive trading education articles covering Day Trading, Swing Trading, Technical Indicators, Options & Futures, and Trading Psychology (October 2025)

## System Architecture
### Production Backend Architecture
- **Primary Framework**: Flask (Python web framework) for web interface and dashboard
- **Trading Engine**: FastAPI with async/await for high-performance trading operations
- **Real-time Data**: WebSocket-based market data streaming service
- **Background Processing**: Celery with Redis for algorithmic trading and portfolio analysis
- **Load Balancer**: Production-grade traffic distribution and rate limiting
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Database**: PostgreSQL (production) with Redis caching layer
- **Message Queue**: Redis for real-time data distribution and task queuing
- **Session Management**: Flask sessions with Redis backing
- **Logging**: Structured logging with performance metrics
- **Deployment**: Multi-service architecture with health monitoring and auto-scaling support

### Frontend Architecture
- **Template Engine**: Jinja2
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Inter)
- **JavaScript**: Vanilla JavaScript (ES6+)
- **Responsive Design**: Mobile-first approach using Bootstrap's grid system with comprehensive breakpoints (1024px tablets, 768px mobile, 576px small mobile, 375px tiny screens)
- **UI/UX Decisions**: Clean white backgrounds, subtle shadows, rounded elements, modern typography (Poppins/Inter), getquin.com and arvat.ai inspired layouts for various pages.

### Application Structure
- **Entry Point**: `main.py`
- **Application Factory**: `app.py`
- **Models**: `models.py` (BlogPost, TeamMember, Testimonial, User, WatchlistItem, StockAnalysis, AIAnalysis, PortfolioOptimization, TradingSignal, AIStockPick, Portfolio), `models_broker.py` (BrokerAccount, BrokerHolding, BrokerPosition, BrokerOrder, BrokerSyncLog, ExecutedTrade)
- **Routes**: `routes.py`, `routes_broker.py`
- **Services**: `/services/` (nse_service.py, market_data_service.py, ai_agent_service.py with full Agentic AI coordinator)
- **Templates**: `/templates/`
- **Static Assets**: `/static/` (includes mobile-responsive.js for enhanced mobile interactions)

### Key Features & Design Patterns
- **Agentic AI Tools**: Fully autonomous AI system with OpenAI and Perplexity integration for stock analysis, real-time research, portfolio optimization, and adaptive decision-making with n8n workflow coordination.
- **Multi-Broker Integration**: Complete support for 12 major Indian brokers with unified API interface: Dhan (free API), Zerodha (₹500/month), Angel One (free API), Upstox (official SDK), FYERS (official SDK), Groww (REST API), ICICIDirect (REST API), HDFC Securities (REST API), Kotak Securities (REST API), 5Paisa (free API), Choice India (REST API), and Goodwill (REST API). Broker Management is now accessible to all user types without subscription restrictions.
- **Trading Infrastructure**: Direct order execution, portfolio synchronization, and real-time balance tracking across all connected broker accounts with encrypted credential storage.
- **Comprehensive Page Structure**: Includes Home, About, Services (Trading Signals, Stock Research, Portfolio Analysis, Algorithmic Trading, Account Management), Blog, Authentication, Dashboard (Stock Analysis, Watchlist, NSE India Stocks, AI Advisor), Pricing, Company (Careers, In the News, Partners), Support (Help Center, Privacy Policy, Terms of Service, Risk Disclosure, Compliance), and Contact pages.
- **Navigation**: Enhanced menu structure with dropdowns, dedicated pricing link, and professional organization.
- **Data Flow**: Flask's URL routing, SQLAlchemy for database operations, Jinja2 for rendering, and JavaScript for client-side interactions.

## External Dependencies
### Python Packages
- Flask
- Flask-SQLAlchemy
- Werkzeug
- NSEPython
- Pandas
- Requests

### Frontend Libraries
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Google Fonts (Inter)

### Infrastructure Dependencies
- Database: SQLite (development) / PostgreSQL (production)
- Web server: Any WSGI-compatible server
- OpenAI API
- Perplexity API
- n8n
- WhatsApp Business API
- Telegram Bot API
- TradingView (for charts, though custom implementation avoids direct API credentials)