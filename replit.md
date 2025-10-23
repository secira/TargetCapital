# Target Capital - Flask Web Application

### Overview
Target Capital is an advanced AI-powered stock trading platform built with Flask, providing autonomous portfolio analysis, algorithmic trading services, and market insights. It aims for true autonomous, intelligent, and adaptive financial decision-making in real-market conditions, moving beyond passive automation. The project envisions significant market potential for such intelligent financial tools.

### User Preferences
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
Removed redundant welcome screen text box to eliminate user confusion - now uses single text input at bottom consistently
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

Research Assistant UI/UX Redesign (October 2025):
- Perplexity-Style Interface: Clean, minimalist design inspired by Perplexity.ai with focus on simplicity and elegance
- Welcome Screen: Just a large, centered search box with "Ask anything..." placeholder - no text, no clutter, no suggestions
- Clean Color Scheme: Neutral grays (#2d2d2d for text, #fafafa for backgrounds) for a professional, distraction-free experience
- Large Search Input: 120px tall textarea on welcome screen, auto-resizes up to 400px for long queries
- Minimal Sidebar: 260px compact sidebar with simple conversation history, time filters (Today/Week/Month), and new chat button
- Message Display: Clean user messages in light gray bubbles, AI messages with small avatar and simple formatting
- Professional Citations: Minimalist citation cards with numbered badges and clean typography
- Trade Execution: Subtle trade cards with buy/sell badges and execute button
- Responsive Input: Auto-resizing textarea that adapts to content length, maximum 200px in chat mode
- Mobile Optimized: Fully responsive with collapsible sidebar and touch-friendly controls
- Visual Polish: Smooth animations, subtle hover effects, and clean transitions throughout

### System Architecture
- **Production Backend Architecture**: Flask (web interface), FastAPI (high-performance trading operations), WebSocket for real-time data, Celery with Redis for background processing, PostgreSQL with Redis caching, SQLAlchemy, and multi-service deployment with auto-scaling.
- **Frontend Architecture**: Jinja2 templating, Bootstrap 5.3.0 for CSS, Font Awesome 6.4.0 for icons, Google Fonts (Inter), and vanilla JavaScript. Employs a mobile-first responsive design with Bootstrap's grid system.
- **UI/UX Decisions**: Clean white backgrounds, subtle shadows, rounded elements, modern typography (Poppins/Inter), inspired by getquin.com and arvat.ai.
- **Key Features & Design Patterns**:
    - **Agentic AI Tools**: Autonomous AI system with OpenAI and Perplexity integration for analysis, research, optimization, and adaptive decision-making, coordinated by n8n workflows.
    - **Multi-Broker Integration**: Supports 12 major Indian brokers with unified API, direct order execution, and encrypted credential storage.
    - **Authentication**: Three methods: Google OAuth, Mobile Number + OTP (Twilio), and Email/Password.
    - **RAG-Powered Research Assistant**: Semantic search via pgvector, LLM responses with citations, trade execution options, and an archive system.
    - **Multi-Asset Portfolio System**: Supports 11 asset classes across multiple brokers, with asset-specific filtering and real-time data.
    - **Broker-Specific Holdings**: Manual holdings tables enhanced to track assets per broker account.

### External Dependencies
- **Python Packages**: Flask, Flask-SQLAlchemy, Werkzeug, NSEPython, Pandas, Requests.
- **Frontend Libraries**: Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter).
- **Infrastructure Dependencies**: PostgreSQL, Redis, OpenAI API, Perplexity API, n8n, Twilio, WhatsApp Business API, Telegram Bot API, Razorpay API, TradingView (custom implementation).