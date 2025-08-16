# tCapital - Flask Web Application

## Overview
tCapital is a Flask-based web application providing an AI-powered stock trading platform. Its core purpose is to offer portfolio analysis, algorithmic trading services, and market insights through a modern, responsive interface. The platform aims to empower users with advanced AI tools for informed trading decisions and efficient portfolio management.

## User Preferences
Preferred communication style: Simple, everyday language.
Brand name: tCapital
Design preference: Clean white backgrounds instead of blue gradients
Navigation bar: Custom dark navy background color #00091a
Typography: Modern Poppins font throughout the website
New Feature: Agentic AI system with multi-agent architecture for autonomous trading and portfolio analysis
Core Concept: Agentic AI represents shift from passive automation to true autonomous decision-making with learn, reason, act, adapt capabilities
Dashboard Layout: Two-column layout with left sidebar for trading tools navigation
Recent Updates: Landing page images replaced with fresh SVG assets (August 16, 2025)
Manual changes accepted for project integration and navigation structure
All manual changes saved and accepted (August 16, 2025)
Comprehensive mobile and tablet compatibility enhancement completed (August 16, 2025)
Mobile responsive design improvements with detailed breakpoints implemented
Fixed mobile header font sizing and dropdown menu functionality
JavaScript errors resolved for better mobile performance

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
- **Models**: `models.py` (BlogPost, TeamMember, Testimonial, User, WatchlistItem, StockAnalysis, AIAnalysis, PortfolioOptimization)
- **Routes**: `routes.py`
- **Services**: `/services/` (nse_service.py, market_data_service.py, ai_agent_service.py)
- **Templates**: `/templates/`
- **Static Assets**: `/static/` (includes mobile-responsive.js for enhanced mobile interactions)

### Key Features & Design Patterns
- **AI-Powered Tools**: Integrated AI for stock analysis, trading signals, portfolio optimization, and an agentic AI advisor.
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