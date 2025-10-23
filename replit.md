# Target Capital - Flask Web Application

## Overview
Target Capital is an advanced Agentic AI-powered stock trading platform built with Flask. It provides autonomous portfolio analysis, algorithmic trading services, and market insights through a modern, responsive interface. The platform aims for true autonomous decision-making that learns, reasons, acts, and adapts in real-market conditions, moving beyond passive automation to intelligent, adaptive financial decision-making. The project envisions significant market potential for such intelligent financial tools.

## User Preferences
Preferred communication style: Simple, everyday language.
Brand name: Target Capital
Design preference: Clean white backgrounds instead of blue gradients
Navigation bar: Custom dark navy background color #00091a
Typography: Modern Poppins font throughout the website
Payment Integration: Razorpay payment system fully integrated with updated pricing (Target Plus ₹1,499, Target Pro ₹2,999, Premium ₹4,999)
New Feature: Comprehensive Agentic AI system with multi-agent architecture and n8n workflow integration for autonomous trading and portfolio analysis
Core Concept: Agentic AI represents shift from passive automation to true autonomous decision-making with learn, reason, act, adapt capabilities
Agentic AI Implementation: Complete integration with OpenAI (GPT-4) and Perplexity APIs for real-time reasoning and research capabilities
n8n Integration: Workflow automation for continuous monitoring and autonomous decision-making triggers
Dashboard Layout: Two-column layout with left sidebar for trading tools navigation
Manual changes accepted for project integration and navigation structure
All manual changes accepted and integrated
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
Razorpay Payment System Integration: Complete payment processing with subscription management, secure checkout flow, payment verification, success/failure handling, billing history, admin panel, and webhook support. Pricing updated to Target Plus ₹1,499, Target Pro ₹2,999, Premium ₹4,999
Updated Subscription Model: Target Plus users can connect 1 broker for portfolio analysis only (no trading); Target Pro supports up to 3 brokers with trade execution limited to 1 primary broker; HNI Account supports unlimited brokers with trade execution limited to 1 primary broker; pricing structure optimized for user growth path
Multi-Asset Portfolio System: Complete implementation supporting 11 asset classes (Equities, Mutual Funds, Fixed Income, F&O, NPS, Real Estate, Gold, ETFs, Crypto, ESOP, Private Equity) with unified views across up to 3 brokers, asset-specific filtering, real-time market data integration, comprehensive test suite (200+ test cases), performance optimization with strategic database indexing, and production-ready deployment with safe database migrations
Knowledge Base Implementation: Renamed "Blog" to "Knowledge Base" with 5 comprehensive trading education articles covering Day Trading, Swing Trading, Technical Indicators, Options & Futures, and Trading Psychology
Authentication System: Simplified three-method authentication:
- Google OAuth: Direct Google authentication via blueprint:flask_google_oauth for seamless social login
- Mobile Number + OTP: Passwordless authentication designed for Indian market via Twilio SMS
- Email/Password: Traditional username/email and password login with secure password hashing
- Users can register/login with any of the three methods
- Complete profile flow after mobile registration to add email/password
- Twilio SMS integration operational with proper rate limiting and security
- Mobile-first approach with passwordless login option for quick access
- All three methods unified under single User model with flexible nullable fields

RAG-Powered Research Assistant System:
- Menu Changes: "Trading Signals" renamed to "Smart Signals", "AI Advisor" renamed to "Research Assistant", "HNI Account" menu removed and features integrated into Dashboard
- Research Assistant Archive System: Complete sidebar implementation with Daily/Weekly/Monthly tabs, Stock/Sector/Strategy filters, conversation history management, and Execute Trade button integration for seamless trade execution from AI recommendations
- AI Status Section Removed: Cleaned up sidebar navigation by removing redundant AI Status and "Agentic AI Active" indicators
- Portfolio Hub Menu: New consolidated menu structure organizing all portfolio-related features:
  - Broker Management (moved from standalone section)
  - Banks (FDs & Cash) - placeholder for future implementation
  - Asset class sub-menus: Equities, Mutual Funds, Fixed Income, Real Estate, Gold & Commodities, Cryptocurrency
- Vector Database: pgvector extension enabled in PostgreSQL for semantic search capabilities
- Database Models: ResearchConversation, ResearchMessage, VectorDocument, SourceCitation, SignalPerformance
- Enhanced Smart Signals: Added sector and category fields for filtering, performance tracking with accuracy metrics
- Research Flow: User query → Vector search → Context assembly → LLM response with citations → Trade execution option
- Data Sources: Stock data, financial news, earnings reports, user research notes, portfolio context
- AI Integration: GPT-3.5-turbo for research, Perplexity for real-time web data, with planned GPT-4 upgrade
- Trade Execution: Pre-filled form flow with user review before broker execution
- Archive System: Daily/Weekly/Monthly tabs with performance tracking and Stock/Sector/Strategy filters
- Compliance: SEBI Research Analyst registration in progress, proper disclaimers and audit trails

Broker-Specific Holdings Tracking:
- Database Enhancement: Added `broker_account_id` foreign key to all 8 manual holdings tables for broker-specific tracking
- Tables Updated: ManualEquityHolding, ManualMutualFundHolding, ManualFixedDepositHolding, ManualRealEstateHolding, ManualCommodityHolding, ManualCryptocurrencyHolding, ManualInsuranceHolding, ManualFuturesOptionsHolding
- Functionality: Users can now specify which broker holds their manually-entered assets, enabling same stock/asset across multiple brokers to be tracked separately
- Benefits: Broker-specific sell/trade actions, accurate broker-wise portfolio reports, future broker-specific tax reporting capabilities
- Backward Compatibility: Field is nullable, so existing manual holdings continue to work without requiring broker assignment
- Performance: Indexed for optimal query performance with foreign key constraints ensuring data integrity

## System Architecture
### Production Backend Architecture
- **Primary Frameworks**: Flask (web interface), FastAPI (high-performance trading operations).
- **Real-time Data**: WebSocket-based market data streaming.
- **Background Processing**: Celery with Redis.
- **Load Balancing**: Production-grade traffic distribution and rate limiting.
- **Database**: PostgreSQL with Redis caching.
- **ORM**: SQLAlchemy with Flask-SQLAlchemy.
- **Session Management**: Flask sessions with Redis.
- **Deployment**: Multi-service architecture with health monitoring and auto-scaling.

### Frontend Architecture
- **Template Engine**: Jinja2.
- **CSS Framework**: Bootstrap 5.3.0.
- **Icons**: Font Awesome 6.4.0.
- **Fonts**: Google Fonts (Inter).
- **JavaScript**: Vanilla JavaScript (ES6+).
- **Responsive Design**: Mobile-first approach using Bootstrap's grid system with comprehensive breakpoints (1024px, 768px, 576px, 375px).
- **UI/UX Decisions**: Clean white backgrounds, subtle shadows, rounded elements, modern typography (Poppins/Inter), inspired by getquin.com and arvat.ai.

### Key Features & Design Patterns
- **Agentic AI Tools**: Autonomous AI system with OpenAI and Perplexity integration for analysis, research, optimization, and adaptive decision-making, coordinated by n8n.
- **Multi-Broker Integration**: Support for 12 major Indian brokers with unified API, direct order execution, portfolio synchronization, and encrypted credential storage.
- **Comprehensive Page Structure**: Includes Home, About, Services, Blog (now Knowledge Base), Authentication, Dashboard (Research Assistant, Stock Analysis, Watchlist, NSE India Stocks), Pricing, Company info, Support, and Contact pages.
- **Authentication**: Three methods: Google OAuth, Mobile Number + OTP (Twilio), and Email/Password.
- **RAG-Powered Research Assistant**: Semantic search via pgvector, LLM responses with citations, trade execution options, and archive system for recommendations.
- **Multi-Asset Portfolio System**: Supports 11 asset classes across multiple brokers, with asset-specific filtering and real-time data.
- **Broker-Specific Holdings**: Manual holdings tables enhanced to track assets per broker account.

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
- Twilio (for SMS OTP)
- WhatsApp Business API
- Telegram Bot API
- Razorpay API
- TradingView (for charts, custom implementation)