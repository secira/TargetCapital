# Target Capital - Flask Web Application

### Overview
Target Capital is an advanced AI-powered stock trading platform built with Flask, providing autonomous portfolio analysis, algorithmic trading services, and market insights. It aims for true autonomous, intelligent, and adaptive financial decision-making in real-market conditions, moving beyond passive automation. The project envisions significant market potential for such intelligent financial tools.

### User Preferences
Preferred communication style: Simple, everyday language.
Brand name: Target Capital
Design preference: Clean white backgrounds instead of blue gradients
Navigation bar: Custom dark navy background color #00091a
Typography: Modern Poppins font throughout the website
Manual changes accepted for project integration and navigation structure
Do not make changes to the file `replit.nix`
Do not make changes to the file `pt-app/pt_app.py`
Do not make changes to the file `pt-app/templates/index.html`
Do not make changes to the folder `pt-app/static/`

### System Architecture
- **Production Backend Architecture**: Flask (web interface), FastAPI (high-performance trading operations), WebSocket for real-time data, Celery with Redis for background processing, PostgreSQL with Redis caching, SQLAlchemy, and multi-service deployment with auto-scaling.
- **Frontend Architecture**: Jinja2 templating, Bootstrap 5.3.0 for CSS, Font Awesome 6.4.0 for icons, Google Fonts (Inter), and vanilla JavaScript. Employs a mobile-first responsive design with Bootstrap's grid system.
- **UI/UX Decisions**: Clean white backgrounds, subtle shadows, rounded elements, modern typography (Poppins/Inter), inspired by getquin.com and arvat.ai. Perplexity-style interface with a clean, minimalist design for the Research Assistant.
- **Key Features & Design Patterns**:
    - **Agentic AI Tools**: Autonomous AI system with OpenAI and Perplexity integration for analysis, research, optimization, and adaptive decision-making, coordinated by n8n workflows.
    - **Multi-Broker Integration**: Supports 12 major Indian brokers with unified API, direct order execution, and encrypted credential storage.
    - **Authentication**: Three methods: Google OAuth, Mobile Number + OTP (Twilio), and Email/Password, unified under a single User model.
    - **RAG-Powered Research Assistant**: Semantic search via pgvector, LLM responses with citations, trade execution options, and an archive system with daily/weekly/monthly tabs.
    - **Multi-Asset Portfolio System**: Supports 11 asset classes (Equities, Mutual Funds, Fixed Income, F&O, NPS, Real Estate, Gold, ETFs, Crypto, ESOP, Private Equity) across multiple brokers, with asset-specific filtering and real-time data.
    - **Broker-Specific Holdings**: Manual holdings tables enhanced with `broker_account_id` for tracking assets per broker account across 8 manual holding types.
    - **Unified Portfolio Analyzer System**: AI-powered analysis with multi-broker data syncing, risk profiling, health scoring, sector/asset allocation, and AI-driven recommendations.
    - **Comprehensive Trading Signal System**: Includes an Admin Module and WhatsApp/Telegram Integration.
    - **Subscription Model**: Tiered pricing (Target Plus ₹1,499, Target Pro ₹2,999, HNI ₹4,999) with varying broker connection and trading capabilities, managed via Razorpay.
    - **Knowledge Base**: Replaced "Blog" with a "Knowledge Base" containing trading education articles.

### External Dependencies
- **Python Packages**: Flask, Flask-SQLAlchemy, Werkzeug, NSEPython, Pandas, Requests.
- **Frontend Libraries**: Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter).
- **Infrastructure Dependencies**: PostgreSQL (with pgvector extension), Redis, OpenAI API (GPT-4, GPT-3.5-turbo), Perplexity API (Sonar), n8n, Twilio, WhatsApp Business API, Telegram Bot API, Razorpay API, TradingView (custom implementation).