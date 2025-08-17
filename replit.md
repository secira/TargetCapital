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
Comprehensive Agentic AI system implemented with OpenAI and Perplexity integration (August 16, 2025)
n8n workflow integration added for autonomous AI decision-making and monitoring
AI Advisor dashboard enhanced with real-time workflow triggers and status monitoring
Enhanced dashboard completely redesigned with dynamic financial overview (August 16, 2025)
New dashboard sidebar with broker connection status and AI monitoring features
Portfolio overview cards showing total value, algo trades, active strategies, and account handling
Real-time Indian market overview with NSE indices and performance tracking
Top holdings display with portfolio allocation percentages and progress bars
AI market intelligence with sentiment analysis and automated recommendations
Quick actions panel for streamlined navigation to key trading functions
Enhanced Stock Picker page with two comprehensive sections: AI Stock Picker and Today's Top AI Picks (August 17, 2025)
Created AIStockPick database model for daily stock recommendations with date filtering capability
Built detailed stock analysis page following Infosys template format with comprehensive financial data
Implemented dynamic table for AI stock picks with date picker functionality for historical data
Added detailed analysis route with sample data for INFY and RELIANCE stocks following document template
Complete integration between Stock Picker page and detailed analysis functionality
Comprehensive Portfolio management system with multi-broker support and database integration (August 17, 2025)
Created Portfolio database model with comprehensive fields for multi-broker holdings tracking
Implemented My Portfolio page with four distinct views: Consolidated, Sectorial, Broker, and AI Optimization
Added real-time portfolio calculation features including P&L, allocation percentages, and performance metrics
Built sample portfolio data system with holdings from Zerodha, Angel Broking, and Dhan for testing
Enhanced portfolio analytics with sector-wise analysis and broker-wise breakdown capabilities
Integrated AI portfolio optimization recommendations with actionable insights and portfolio scoring

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