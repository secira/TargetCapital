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

### LangGraph AI Architecture (PRIMARY SYSTEM)
Target Capital implements **LangGraph as the primary AI architecture** for autonomous, multi-step reasoning and intelligent decision-making. This replaced the legacy agentic AI system for superior scalability, observability, and market acceptance.

#### 1. **LangGraph Research Assistant** (`services/langgraph_research_assistant.py`)
   - **Multi-Step State Graph**: Query Understanding → Context Retrieval → Market Analysis → Response Generation → Trade Suggestion
   - Integrates pgvector semantic search with Perplexity Sonar Pro real-time market data
   - Stores conversation history in PostgreSQL for context-aware interactions
   - Returns comprehensive answers with citations and actionable trade recommendations
   - **API**: `/api/research/query` (POST) - use_langgraph parameter enables LangGraph mode
   - **UI Integration**: Research Assistant page with real-time conversation display

#### 2. **Multi-Agent Portfolio Optimizer** (`services/langgraph_portfolio_optimizer.py`)
   - **4 Specialized Parallel Agents**:
     * **Risk Analyzer Agent** (Temp 0.1) - Conservative portfolio risk, volatility, diversification analysis
     * **Sector Analyzer Agent** (Temp 0.4) - Balanced sector allocation and concentration evaluation
     * **Asset Allocator Agent** (Temp 0.4) - Balanced optimal asset allocation recommendations
     * **Opportunity Finder Agent** (Temp 0.7) - Creative investment opportunities based on preferences
   - **Coordinator Agent** synthesizes all outputs into comprehensive portfolio optimization report
   - Different temperature settings per agent for diverse perspectives
   - Stores optimization reports in PostgreSQL for historical tracking
   - **API**: `/api/portfolio/optimize-langgraph` (POST) - generates multi-agent analysis
   - **UI Integration**: Portfolio page with visual 4-agent workflow display (`langgraph-visual.js`)
   - **Visual Workflow**: Real-time agent status (pending → in-progress → completed) with color-coded cards

#### 3. **Smart Trading Signal Pipeline** (`services/langgraph_signal_pipeline.py`)
   - **5-Stage Conditional Pipeline**: Market Scanner → Signal Generator → Validator → Broker Checker → Execution Planner
   - Scans Indian markets (NSE/BSE) using Perplexity for real-time opportunities
   - Generates signals with entry/target/stop-loss prices, risk-reward ratios
   - **Quality Gates**: Validates signals against risk parameters (1:2 R:R minimum, max 5% stop loss)
   - Checks broker compatibility and creates execution strategies
   - Conditional logic: only valid signals proceed through pipeline
   - Stores validated signals in PostgreSQL with pipeline metadata
   - **API**: `/api/signals/generate-langgraph` (POST) - generates daily trading signals (Admin-only)
   - **UI Integration**: Smart Signals page with visual 5-stage pipeline display (`langgraph-visual.js`)
   - **Visual Pipeline**: Real-time stage status, metrics tracking (scanned/generated/validated/ready)

#### 4. **Visual Agent Workflow System** (`static/js/langgraph-visual.js`)
   - **PortfolioAgentWorkflow**: Visual representation of 4-agent parallel execution
   - **SignalPipelineWorkflow**: Visual representation of 5-stage sequential pipeline
   - Color-coded status indicators (blue=pending, orange=in-progress, green=completed, red=error)
   - Real-time progress animations with spinning icons
   - Metrics dashboard for pipeline performance tracking
   - Temperature badge display for agent configuration transparency

#### 5. **State Persistence Layer** (PostgreSQL models):
   - `ConversationHistory` - Research assistant conversation storage with user context
   - `AgentCheckpoint` - LangGraph agent state checkpoints for resumable workflows
   - `PortfolioOptimizationReport` - Multi-agent portfolio analysis reports with timestamps
   - `TradingSignal` - Generated trading signals with execution metadata and pipeline info

#### **LangGraph Advantages Over Legacy System:**
- ✅ **Structured Multi-Step Reasoning**: Explicit state management vs. implicit coordination
- ✅ **Resumable Workflows**: Checkpoint system allows recovery from failures
- ✅ **Clear Separation of Concerns**: Each agent/step has specific, documented role
- ✅ **Enhanced Observability**: Visual workflows show real-time agent execution
- ✅ **Parallel Agent Execution**: Portfolio optimization runs 4 agents simultaneously
- ✅ **Conditional Workflows**: Quality gates ensure only valid signals proceed
- ✅ **Market Acceptance**: LangGraph is industry-standard, enhancing credibility
- ✅ **Visual Differentiation**: User-facing workflow displays set product apart

#### **Architecture Decision**: 
Replaced custom agentic AI coordinator with LangGraph/LangChain for production-grade multi-agent orchestration. Visual agent workflows provide critical user experience differentiation and transparency into AI decision-making processes.

- **Key Features & Design Patterns**:
    - **Agentic AI Tools**: Autonomous AI system with OpenAI, Perplexity, and LangGraph for analysis, research, optimization, and adaptive decision-making.
    - **Multi-Broker Integration**: Supports 12 major Indian brokers with unified API, direct order execution, and encrypted credential storage.
    - **Authentication**: Three methods: Google OAuth, Mobile Number + OTP (Twilio), and Email/Password, unified under a single User model.
    - **RAG-Powered Research Assistant**: Now powered by LangGraph with semantic search via pgvector, LLM responses with citations, trade execution options, and conversation history.
    - **Multi-Asset Portfolio System**: Supports 11 asset classes (Equities, Mutual Funds, Fixed Income, F&O, NPS, Real Estate, Gold, ETFs, Crypto, ESOP, Private Equity) across multiple brokers, with asset-specific filtering and real-time data.
    - **Broker-Specific Holdings**: Manual holdings tables enhanced with `broker_account_id` for tracking assets per broker account across 8 manual holding types.
    - **Portfolio Asset Vector Embeddings** (`services/portfolio_embedding_service.py`): Automatic vector embedding generation for all portfolio assets loaded through Portfolio Hub. All holdings (stocks from multiple brokers, F&O, mutual funds, fixed deposits, etc.) are automatically stored in pgvector database under user-specific embeddings for semantic search and enhanced AI analysis. Enables natural language queries like "my technology stocks" or "high-risk investments". Integrated with broker sync, manual entry, Excel/PDF import flows, and portfolio analysis systems.
    - **Unified Portfolio Analyzer System**: AI-powered analysis with multi-agent LangGraph optimization, multi-broker data syncing, risk profiling, health scoring, sector/asset allocation, and AI-driven recommendations. Now enhanced with vector semantic search over user's own portfolio holdings.
    - **Comprehensive Trading Signal System**: LangGraph-powered signal pipeline with validation, broker compatibility checks, and execution planning. Includes Admin Module and WhatsApp/Telegram Integration.
    - **Subscription Model**: Tiered pricing (Target Plus ₹1,499, Target Pro ₹2,999, HNI ₹4,999) with varying broker connection and trading capabilities, managed via Razorpay.
    - **Knowledge Base**: Replaced "Blog" with a "Knowledge Base" containing trading education articles.

### External Dependencies
- **Python Packages**: Flask, Flask-SQLAlchemy, Werkzeug, NSEPython, Pandas, Requests, LangGraph, LangChain, LangChain-OpenAI, LangChain-Community.
- **Frontend Libraries**: Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter).
- **Infrastructure Dependencies**: PostgreSQL (with pgvector extension), Redis, OpenAI API (GPT-4-turbo-preview for LangGraph agents), Perplexity API (Sonar Pro for market data), n8n, Twilio, WhatsApp Business API, Telegram Bot API, Razorpay API, TradingView (custom implementation).
- **AI/ML Stack**: LangGraph (agent orchestration), LangChain (LLM framework), OpenAI GPT-4-turbo (multi-agent reasoning), Perplexity Sonar (real-time market intelligence), pgvector (semantic search).