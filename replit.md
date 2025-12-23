# Target Capital - Flask Web Application

### Overview
Target Capital is an AI-powered trading support platform for the Indian market, designed to provide intelligent decision support. It aims to address the high rate of losses among individual F&O traders by offering three core solutions: Portfolio Hub for consolidated multi-broker dashboards and risk analytics, an AI Research Assistant for RAG-powered, portfolio-specific insights, and Trading Support with transparent, experience-gated signals. The platform targets 15M+ Indian investors and plans a multi-region strategy.

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
The platform utilizes a multi-service backend with Flask for the web interface and FastAPI for high-performance trading operations, supported by WebSocket for real-time data, Celery with Redis for background tasks, and PostgreSQL with Redis caching for data storage. It employs a multi-tenant architecture with tenant isolation via `tenant_id` and a middleware for tenant resolution. The frontend uses Jinja2 templating, Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter), and vanilla JavaScript, focusing on a mobile-first, responsive design with clean white backgrounds and modern typography.

**AI Architecture (LangGraph)**:
Target Capital leverages LangGraph as its primary AI architecture for autonomous, multi-step reasoning.
-   **LangGraph Research Assistant**: A multi-step state graph for query understanding, context retrieval, market analysis, response generation, and trade suggestions, integrating pgvector and Perplexity Sonar Pro.
-   **Multi-Agent Portfolio Optimizer**: Features four specialized parallel agents (Risk Analyzer, Sector Analyzer, Asset Allocator, Opportunity Finder) orchestrated by a Coordinator Agent to synthesize optimization reports.
-   **Smart Trading Signal Pipeline**: A five-stage conditional pipeline (Market Scanner, Signal Generator, Validator, Broker Checker, Execution Planner) for generating and validating trading signals.
-   **Trade Plus Pipeline**: A six-stage validation pipeline (Subscription, Broker, Funds, Signal, Risk, Execution Planner) for trade execution, requiring user confirmation for order placement.
-   **Visual Agent Workflow System**: JavaScript-based visualizations for Portfolio Agent Workflow, Signal Pipeline Workflow, and Trade Execution Workflow, providing real-time status and metrics.
-   **State Persistence Layer**: PostgreSQL models for storing conversation history, agent checkpoints, portfolio optimization reports, trading signals, and portfolio asset embeddings.

**Key Features & Design Patterns**:
-   **Agentic AI Tools**: Utilizes OpenAI, Perplexity, and LangGraph for analysis, research, and optimization.
-   **Multi-Broker Integration**: Supports 12 major Indian brokers with unified API and encrypted credential storage.
-   **Authentication**: Supports Google OAuth, Mobile Number + OTP, and Email/Password.
-   **RAG-Powered Research Assistant**: Enhanced with LangGraph, pgvector for semantic search, LLM responses with citations, and conversation history.
-   **Multi-Asset Portfolio System**: Supports 11 asset classes across multiple brokers with asset-specific filtering and real-time data.
-   **Portfolio Asset Vector Embeddings**: Automatic generation of vector embeddings for all portfolio assets for semantic search and AI analysis.
-   **Unified Portfolio Analyzer System**: AI-powered analysis with multi-agent LangGraph optimization, risk profiling, and AI-driven recommendations.
-   **Comprehensive Trading Signal System**: LangGraph-powered signal pipeline with validation, broker compatibility checks, and execution planning.
-   **Subscription Model**: Tiered pricing with feature-gated access (FREE, TARGET PLUS, TARGET PRO, HNI).
-   **Knowledge Base**: Replaces a traditional blog with educational trading articles.

**Mobile App & PWA Support**:
-   **Mobile REST API (v1)**: Versioned API at `/api/v1/mobile/` with JWT authentication for mobile app integration.
-   **JWT Authentication**: Stateless token-based auth with access tokens (24hr) and refresh tokens (30 days).
-   **Mobile Endpoints**: Authentication (email/password, OTP), portfolio, trading signals, brokers, market data.
-   **Progressive Web App (PWA)**: Full PWA support with service worker, offline caching, install prompts, and push notifications.
-   **Mobile-First Design**: Responsive UI with touch optimization, viewport handling, and slow-connection mode.

**Enterprise Multi-Tenant Security Architecture**:
Implements defense-in-depth tenant isolation through three layers:
1.  **SQLAlchemy ORM Automatic Filtering**: Dynamically discovers models with `tenant_id` and auto-injects tenant filters on SELECT queries, validates `tenant_id` on new records, and syncs session variables for RLS.
2.  **PostgreSQL Row-Level Security (RLS)**: Dynamic RLS policy creation for tenant-scoped tables using `current_setting('app.tenant_id')`.
3.  **Per-Tenant Encryption Service**: Hierarchical key management and Fernet-based field-level encryption for sensitive columns using an `EncryptedColumn Descriptor`.

### External Dependencies
-   **Python Packages**: Flask, Flask-SQLAlchemy, Werkzeug, NSEPython, Pandas, Requests, LangGraph, LangChain, LangChain-OpenAI, LangChain-Community, cryptography.
-   **Frontend Libraries**: Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter).
-   **Infrastructure Dependencies**: PostgreSQL (with pgvector extension), Redis.
-   **AI/ML Stack**: OpenAI API (GPT-4-turbo for LangGraph agents), Perplexity API (Sonar Pro for market data).
-   **Third-Party Services**: n8n, Twilio, WhatsApp Business API, Telegram Bot API, Razorpay API, TradingView (custom implementation).