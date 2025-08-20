# tCapital - Flask Web Application

## Overview
tCapital is a Flask-based web application providing an advanced Agentic AI-powered stock trading platform. Its core purpose is to offer autonomous portfolio analysis, algorithmic trading services, and market insights through a modern, responsive interface. The platform emphasizes true autonomous decision-making that learns, reasons, acts, and adapts in real-market conditions, moving beyond passive automation to intelligent, adaptive financial decision-making.

## User Preferences
Preferred communication style: Simple, everyday language.
Brand name: tCapital
Design preference: Clean white backgrounds instead of blue gradients
Navigation bar: Custom dark navy background color #00091a
Typography: Modern Poppins font throughout the website
New Feature: Comprehensive Agentic AI system with multi-agent architecture and n8n workflow integration for autonomous trading and portfolio analysis
Core Concept: Agentic AI represents shift from passive automation to true autonomous decision-making with learn, reason, act, adapt capabilities
Agentic AI Implementation: Complete integration with OpenAI (GPT-4) and Perplexity APIs for real-time reasoning and research capabilities
n8n Integration: Workflow automation for continuous monitoring and autonomous decision-making triggers
Dashboard Layout: Two-column layout with left sidebar for trading tools navigation
Recent Updates: Landing page images replaced with fresh SVG assets (August 16, 2025)
Manual changes accepted for project integration and navigation structure
All manual changes saved and accepted (August 16, 2025)
Comprehensive mobile and tablet compatibility enhancement completed (August 16, 2025)
Mobile responsive design improvements with detailed breakpoints implemented
Fixed mobile header font sizing and dropdown menu functionality
JavaScript errors resolved for better mobile performance
Typography standardization implemented across all dashboard pages (August 18, 2025)
Updated typography for better readability: H1=26px, H2=22px, H3=20px, H4=18px, H5=17px, H6=16px
Body text increased to 16px minimum with improved line heights and readability
Created dashboard.css for unified typography standards
Updated all dashboard page headings to use consistent .dashboard-heading class
Font sizes optimized for better user experience and accessibility
Comprehensive Agentic AI system implemented with OpenAI and Perplexity integration (August 16, 2025)
n8n workflow integration added for autonomous AI decision-making and monitoring
AI Advisor dashboard enhanced with real-time workflow triggers and status monitoring
Full backend implementation for agentic AI-powered investment analysis completed (August 19, 2025)
Created MarketIntelligenceService for real-time market sentiment, sector performance, and economic indicators
Built InvestmentAnalysisService with comprehensive stock analysis using AI and market data integration
Implemented AgenticAICoordinator with learn-reason-act-adapt cycle for autonomous investment decisions
Added specialized AI agents: ResearchAgent, AnalysisAgent, DecisionAgent, and LearningAgent
Enhanced AI Advisor interface with unified chat and market intelligence dashboard
Perplexity AI integration completed for Stock Picker enhanced Indian market research (August 19, 2025)
Integrated Perplexity API service for "Start AI Research" and "Generate AI Picks" features
Created comprehensive PerplexityService with real-time Indian stock market research capabilities
Added specialized API endpoints for Perplexity research, picks generation, and market insights
Enhanced Stock Picker interface with Perplexity-powered research and intelligent fallback data
Improved research quality specifically for Indian stock market using Perplexity's online models
Enhanced dashboard completely redesigned with dynamic financial overview (August 16, 2025)
New dashboard sidebar with broker connection status and AI monitoring features
Portfolio overview cards showing total value, algo trades, active strategies, and account handling
Real-time Indian market overview with NSE indices and performance tracking
Top holdings display with portfolio allocation percentages and progress bars
AI market intelligence with sentiment analysis and automated recommendations
Quick actions panel for streamlined navigation to key trading functions
AI-Powered Investment Explanation Chatbot implemented with comprehensive features (August 19, 2025)
Created ChatConversation, ChatMessage, and ChatbotKnowledgeBase database models for chat functionality
Built InvestmentChatbot service with OpenAI GPT-4o integration for intelligent responses
Implemented personalized chat responses using user portfolio context and market data
Added conversation history management with persistent chat sessions and message threading
Created responsive chat interface with typing indicators, quick actions, and mobile optimization
Integrated knowledge base system with pre-loaded investment concepts and terminology explanations
Added subscription-based access control ensuring chatbot availability for appropriate user tiers
Enhanced Stock Picker page with two comprehensive sections: AI Stock Picker and Today's Top AI Picks (August 17, 2025)
Created AIStockPick database model for daily stock recommendations with date filtering capability
Built detailed stock analysis page following Infosys template format with comprehensive financial data
Implemented dynamic table for AI stock picks with date picker functionality for historical data
Added detailed analysis route with sample data for INFY and RELIANCE stocks following document template
Complete integration between Stock Picker page and detailed analysis functionality
AI Advisor completely restructured with Perplexity Sonar integration (August 19, 2025)
Replaced ChatGPT with Perplexity Sonar Pro for real-time market intelligence and current data access
Created modern dual-mode interface accommodating both AI Advisor and Agentic AI functionality
Enhanced chatbot service with Perplexity API integration using sonar-pro model for better market insights
Built user-friendly interface with mode selection, capability cards, and streamlined chat experience
Improved real-time market data access with current news, sentiment analysis, and live stock information
Fixed Perplexity API message alternation format and successfully connected to real-time market data (August 19, 2025)
Comprehensive Portfolio management system with multi-broker support and database integration (August 17, 2025)
Created Portfolio database model with comprehensive fields for multi-broker holdings tracking
Implemented My Portfolio page with four distinct views: Consolidated, Sectorial, Broker, and AI Optimization
Added real-time portfolio calculation features including P&L, allocation percentages, and performance metrics
Built sample portfolio data system with holdings from Zerodha, Angel Broking, and Dhan for testing
Enhanced portfolio analytics with sector-wise analysis and broker-wise breakdown capabilities
Integrated AI portfolio optimization recommendations with actionable insights and portfolio scoring
Dashboard system cleanup: Removed Watchlist menu item and functionality as requested by user (August 17, 2025)
Unified dashboard navigation with consistent left sidebar layout across all menu items
Updated Trade Now page template structure to match other dashboard pages for visual consistency
Fixed routing issues and template structure alignment across dashboard components
Moved AI Advisor menu item below Account Handling in sidebar navigation as requested (August 20, 2025)
Restructured AI Advisor interface layout: search input as main focal point, advanced functions moved to right sidebar (August 20, 2025)
Removed redundant welcome screen text box to eliminate user confusion - now uses single text input box at bottom consistently (August 20, 2025)
UI/UX improvements for AI Advisor text input: 40 characters width, 3 lines height, fixed size to prevent collapse, removed "Thinking" text, colorful "New Chat" button below text box, changed up arrow to "Send" button (August 20, 2025)
UI/UX improvements: Removed Market Opportunities and Risk Factors sections from Stock Picker page (August 17, 2025)
Streamlined dashboard interface by removing Quick Actions section from main dashboard
Cleaned up Trade Now page by removing duplicate Refresh and Algo Setup buttons
All manual changes accepted and integrated into project architecture (August 18, 2025)

## System Architecture
### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Database**: SQLite (default) with PostgreSQL support
- **Session Management**: Flask sessions
- **Logging**: Python's built-in logging module
- **Deployment**: WSGI-compatible with ProxyFix middleware

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
- **Models**: `models.py` (BlogPost, TeamMember, Testimonial, User, WatchlistItem, StockAnalysis, AIAnalysis, PortfolioOptimization, TradingSignal, AIStockPick, Portfolio)
- **Routes**: `routes.py`
- **Services**: `/services/` (nse_service.py, market_data_service.py, ai_agent_service.py with full Agentic AI coordinator)
- **Templates**: `/templates/`
- **Static Assets**: `/static/` (includes mobile-responsive.js for enhanced mobile interactions)

### Key Features & Design Patterns
- **Agentic AI Tools**: Fully autonomous AI system with OpenAI and Perplexity integration for stock analysis, real-time research, portfolio optimization, and adaptive decision-making with n8n workflow coordination.
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