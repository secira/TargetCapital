# Target Capital - Flask Web Application

### Overview
Target Capital is an AI-powered trading support platform for the Indian market, providing intelligent decision support rather than automated trading. The platform addresses the critical problem that 91% of individual F&O traders lost money in FY25, offering three core solutions:

1. **Portfolio Hub**: Multi-broker consolidated dashboard with real-time risk analytics across 11 asset classes
2. **AI Research Assistant**: RAG-powered chat-based explanations with portfolio-specific insights and cited sources
3. **Trading Support**: Transparent trading signals with full performance history, gated by experience level

**Target Market**: 15M+ Indian investors with ₹100T+ portfolios fragmented across multiple broker accounts. Fintech adoption accelerating with platforms like Zerodha, Dhan, Angel One, Upstox. Enterprise opportunity with RIAs and wealth platforms managing ₹1000s of crores.

**Subscription Model**: FREE (₹0), TARGET_PLUS (₹1,499), TARGET_PRO (₹2,499), HNI (₹4,999)

**Multi-Region Strategy**: Separate codebases planned for India (in.targetcapital.ai) and USA (usa.targetcapital.ai) due to different brokers, compliance requirements, and data sources.

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

#### 4. **Trade Support Pipeline** (`services/langgraph_trade_executor.py`) **[NEW]**
   - **6-Stage Validation Pipeline**: Subscription → Broker → Funds → Signal → Risk → Execution Planner
   - **Subscription Validator**: Ensures user has TARGET PRO (₹2,499) or HNI (₹4,999) subscription
   - **Broker Selector**: Identifies primary broker account, verifies active connection
   - **Funds Validator**: Checks available margin with 1% buffer for charges
   - **Signal Validator**: Enforces minimum 1:2 risk-reward ratio quality gate
   - **Risk Calculator**: Calculates position sizing with maximum 5% risk per trade
   - **Execution Planner**: Generates comprehensive execution plan for user confirmation
   - **User Confirmation Required**: Final approval before actual order placement
   - **APIs**: 
     * `/api/trade/validate-execution` (POST) - runs 6-stage validation pipeline
     * `/api/trade/execute-confirmed` (POST) - executes trade after user confirms
   - **UI Integration**: Visual 6-stage workflow with real-time validation status
   - **Seamless Execution**: Direct broker integration with proper risk management

#### 5. **Visual Agent Workflow System** (`static/js/langgraph-visual.js`)
   - **PortfolioAgentWorkflow**: Visual representation of 4-agent parallel execution
   - **SignalPipelineWorkflow**: Visual representation of 5-stage sequential pipeline
   - **TradeExecutionWorkflow**: Visual representation of 6-stage validation pipeline
   - Color-coded status indicators (blue=pending, orange=in-progress, green=completed, red=error)
   - Real-time progress animations with spinning icons
   - Metrics dashboard for pipeline performance tracking
   - Temperature badge display for agent configuration transparency
   - Interactive stage cards with detailed configuration modals

#### 6. **State Persistence Layer** (PostgreSQL models):
   - `ConversationHistory` - Research assistant conversation storage with user context
   - `AgentCheckpoint` - LangGraph agent state checkpoints for resumable workflows
   - `PortfolioOptimizationReport` - Multi-agent portfolio analysis reports with timestamps
   - `TradingSignal` - Generated trading signals with execution metadata and pipeline info
   - `PortfolioAssetEmbedding` - Vector embeddings for semantic portfolio search

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
    - **Subscription Model**: Tiered pricing with feature-gated access, managed via Razorpay:
      * **FREE** (₹0): Research Assistant only
      * **TARGET PLUS** (₹1,499): Research Assistant + Smart Signals (view-only) + My Portfolio + Portfolio Hub
      * **TARGET PRO** (₹2,499): All features + Trade Support with 1 Primary Broker + LangGraph 6-stage validation pipeline
      * **HNI** (₹4,999): All features + Trade Support with 1 Primary Broker + Premium support
    - **Knowledge Base**: Replaced "Blog" with a "Knowledge Base" containing trading education articles.

### External Dependencies
- **Python Packages**: Flask, Flask-SQLAlchemy, Werkzeug, NSEPython, Pandas, Requests, LangGraph, LangChain, LangChain-OpenAI, LangChain-Community.
- **Frontend Libraries**: Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter).
- **Infrastructure Dependencies**: PostgreSQL (with pgvector extension), Redis, OpenAI API (GPT-4-turbo-preview for LangGraph agents), Perplexity API (Sonar Pro for market data), n8n, Twilio, WhatsApp Business API, Telegram Bot API, Razorpay API, TradingView (custom implementation).
- **AI/ML Stack**: LangGraph (agent orchestration), LangChain (LLM framework), OpenAI GPT-4-turbo (multi-agent reasoning), Perplexity Sonar (real-time market intelligence), pgvector (semantic search).