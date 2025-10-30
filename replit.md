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

### LangGraph AI Architecture (NEW)
Target Capital now implements advanced AI agents using LangGraph for autonomous, multi-step reasoning:

1. **LangGraph Research Assistant** (`services/langgraph_research_assistant.py`)
   - Multi-step state graph: Query Understanding → Context Retrieval → Market Analysis → Response Generation → Trade Suggestion
   - Integrates pgvector semantic search with Perplexity real-time market data
   - Stores conversation history in PostgreSQL for context-aware interactions
   - Returns comprehensive answers with citations and actionable trade recommendations
   - API: `/api/research/query` (POST) - use_langgraph parameter enables LangGraph mode

2. **Multi-Agent Portfolio Optimizer** (`services/langgraph_portfolio_optimizer.py`)
   - Coordinates 4 specialized AI agents:
     * Risk Analyzer Agent - Portfolio risk, volatility, diversification analysis
     * Sector Analyzer Agent - Sector allocation and concentration evaluation
     * Asset Allocator Agent - Optimal asset allocation recommendations
     * Opportunity Finder Agent - Investment opportunities based on preferences
   - Coordinator Agent synthesizes all outputs into comprehensive portfolio optimization report
   - Different temperature settings per agent (conservative for risk, creative for opportunities)
   - Stores optimization reports in PostgreSQL for historical tracking
   - API: `/api/portfolio/optimize-langgraph` (POST) - generates multi-agent analysis

3. **Smart Trading Signal Pipeline** (`services/langgraph_signal_pipeline.py`)
   - State machine pipeline: Market Scanner → Signal Generator → Validator → Broker Checker → Execution Planner
   - Scans Indian markets (NSE/BSE) using Perplexity for real-time opportunities
   - Generates signals with entry/target/stop-loss prices, risk-reward ratios
   - Validates signals against risk parameters (1:2 R:R minimum, max 5% stop loss)
   - Checks broker compatibility and creates execution strategies
   - Stores validated signals in PostgreSQL with pipeline metadata
   - API: `/api/signals/generate-langgraph` (POST) - generates daily trading signals

4. **State Persistence Layer** (PostgreSQL models):
   - `ConversationHistory` - Research assistant conversation storage
   - `AgentCheckpoint` - LangGraph agent state checkpoints for resumable workflows
   - `PortfolioOptimizationReport` - Multi-agent portfolio analysis reports
   - `TradingSignal` - Generated trading signals with execution metadata

**LangGraph Benefits:**
- Structured multi-step reasoning with explicit state management
- Resumable workflows via checkpoint system
- Clear separation of concerns (each agent/step has specific role)
- Enhanced observability and debugging
- Parallel agent execution for portfolio optimization
- Conditional workflows (e.g., only suggest trades when appropriate)

- **Key Features & Design Patterns**:
    - **Agentic AI Tools**: Autonomous AI system with OpenAI, Perplexity, and LangGraph for analysis, research, optimization, and adaptive decision-making.
    - **Multi-Broker Integration**: Supports 12 major Indian brokers with unified API, direct order execution, and encrypted credential storage.
    - **Authentication**: Three methods: Google OAuth, Mobile Number + OTP (Twilio), and Email/Password, unified under a single User model.
    - **RAG-Powered Research Assistant**: Now powered by LangGraph with semantic search via pgvector, LLM responses with citations, trade execution options, and conversation history.
    - **Multi-Asset Portfolio System**: Supports 11 asset classes (Equities, Mutual Funds, Fixed Income, F&O, NPS, Real Estate, Gold, ETFs, Crypto, ESOP, Private Equity) across multiple brokers, with asset-specific filtering and real-time data.
    - **Broker-Specific Holdings**: Manual holdings tables enhanced with `broker_account_id` for tracking assets per broker account across 8 manual holding types.
    - **Unified Portfolio Analyzer System**: AI-powered analysis with multi-agent LangGraph optimization, multi-broker data syncing, risk profiling, health scoring, sector/asset allocation, and AI-driven recommendations.
    - **Comprehensive Trading Signal System**: LangGraph-powered signal pipeline with validation, broker compatibility checks, and execution planning. Includes Admin Module and WhatsApp/Telegram Integration.
    - **Subscription Model**: Tiered pricing (Target Plus ₹1,499, Target Pro ₹2,999, HNI ₹4,999) with varying broker connection and trading capabilities, managed via Razorpay.
    - **Knowledge Base**: Replaced "Blog" with a "Knowledge Base" containing trading education articles.

### External Dependencies
- **Python Packages**: Flask, Flask-SQLAlchemy, Werkzeug, NSEPython, Pandas, Requests, LangGraph, LangChain, LangChain-OpenAI, LangChain-Community.
- **Frontend Libraries**: Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter).
- **Infrastructure Dependencies**: PostgreSQL (with pgvector extension), Redis, OpenAI API (GPT-4-turbo-preview for LangGraph agents), Perplexity API (Sonar Pro for market data), n8n, Twilio, WhatsApp Business API, Telegram Bot API, Razorpay API, TradingView (custom implementation).
- **AI/ML Stack**: LangGraph (agent orchestration), LangChain (LLM framework), OpenAI GPT-4-turbo (multi-agent reasoning), Perplexity Sonar (real-time market intelligence), pgvector (semantic search).