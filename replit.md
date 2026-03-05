# Target Capital - Flask Web Application

### Overview
Target Capital is an AI-powered trading support platform for the Indian market. It aims to reduce losses for individual F&O traders by offering a Portfolio Hub for multi-broker dashboards and risk analytics, an AI Research Assistant for RAG-powered insights, and Trading Support with transparent, experience-gated signals. The platform targets over 15 million Indian investors with a vision for multi-regional expansion.

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
The platform features a multi-service backend with Flask for the web interface and FastAPI for high-performance trading operations. It uses WebSockets for real-time data, Celery with Redis for background tasks, and PostgreSQL with Redis caching for data storage. A multi-tenant architecture ensures tenant isolation via `tenant_id` and middleware for resolution. The frontend uses Jinja2, Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter), and vanilla JavaScript, focusing on a mobile-first, responsive design with clean white backgrounds and modern typography.

**AI Architecture**:
Target Capital employs a dual AI engine approach:
-   **Anthropic Workflow Engine**: Utilizes Claude Sonnet/Haiku for enterprise-grade solutions. This includes a robust `Anthropic Service`, a `Workflow Engine Framework` for multi-step pipeline execution with state management, `Data Connector Layer` for B2B/B2C data integration, and specialized workflows like `I-Score Workflow`, `Research Workflow`, and `Portfolio Analysis Workflow`. API routes and UI components (`Workflow Hub UI`) are provided for interaction and visualization.
-   **LangGraph Engine**: The original OpenAI-based system, featuring a `LangGraph Research Assistant`, a `Multi-Agent Portfolio Optimizer`, a `Smart Trading Signal Pipeline`, and a `Trade Plus Pipeline`. Visualizations are provided through a `Visual Agent Workflow System`, with state persistence via PostgreSQL models.

**B2B/B2C Multi-Tenant Data Architecture**: Supports B2C user-connected brokers (Dhan, Zerodha, Angel) via `BrokerService` and B2B partner broker APIs with configurable `B2BConnector`. A database fallback reads from the local `Portfolio` model. Each B2B partner operates as a distinct tenant.

**Key Features & Design Patterns**:
-   **Agentic AI Tools**: Leverages OpenAI, Perplexity, and LangGraph for advanced analytics.
-   **Multi-Broker Integration**: Unified API support for 12 major Indian brokers.
-   **Authentication**: Google OAuth, Mobile OTP, and Email/Password.
-   **RAG-Powered Research Assistant**: Semantic search with pgvector, LLM responses with citations.
-   **Multi-Asset Portfolio System**: Supports 11 asset classes across multiple brokers with real-time data and asset-specific filtering.
-   **Portfolio Asset Vector Embeddings**: Automatic generation for semantic search and AI analysis.
-   **Unified Portfolio Analyzer System**: AI-powered analysis with multi-agent LangGraph optimization and risk profiling.
-   **Comprehensive Trading Signal System**: LangGraph-powered signal pipeline with validation and execution planning.
-   **Subscription Model**: Tiered access (FREE, TARGET PLUS, TARGET PRO, HNI).
-   **Knowledge Base**: Educational trading articles.

**Mobile App & PWA Support**:
-   **Mobile REST API (v1)**: Versioned API `/api/v1/mobile/` with JWT authentication.
-   **JWT Authentication**: Stateless token-based authentication.
-   **Mobile Endpoints**: Covers authentication, portfolio, trading signals, brokers, and market data.
-   **Progressive Web App (PWA)**: Full PWA support including service worker, offline caching, and push notifications.
-   **Mobile-First Design**: Responsive UI with touch optimization.

**Enterprise Multi-Tenant Security Architecture**: Implements defense-in-depth through:
1.  **SQLAlchemy ORM Automatic Filtering**: Auto-injects tenant filters and validates `tenant_id` for data isolation.
2.  **PostgreSQL Row-Level Security (RLS)**: Dynamic RLS policy creation using `current_setting('app.tenant_id')`.
3.  **Per-Tenant Encryption Service**: Hierarchical key management and Fernet-based field-level encryption for sensitive data.

**Application Security Controls**:
-   **User Data Isolation**: Queries filtered by `user_id` and `tenant_id`, URL manipulation protection via `verify_resource_ownership()`.
-   **API Keys & Secrets Protection**: Environment variables for keys, encrypted broker credentials, Replit/Railway secrets management, rate limiting.
-   **Privilege Escalation Prevention**: `is_admin` and `pricing_plan` fields cannot be user-modified, `@admin_required` decorator, subscription changes via verified webhooks.

**I-Score Engine Implementation**: A fully functional 7-node LangGraph workflow using GPT-4 Turbo, Perplexity Sonar Pro, and NSE Service for weighted scoring based on Qualitative, Quantitative/Technical, Search/Sentiment, and Trend Analysis. Includes cache checks, real-time market data, detailed reasoning, and result storage.

### External Dependencies
-   **Python Packages**: Flask, Flask-SQLAlchemy, Werkzeug, NSEPython, Pandas, Requests, LangGraph, LangChain, LangChain-OpenAI, LangChain-Community, cryptography.
-   **Frontend Libraries**: Bootstrap 5.3.0, Font Awesome 6.4.0, Google Fonts (Inter).
-   **Infrastructure Dependencies**: PostgreSQL (with pgvector extension), Redis.
-   **AI/ML Stack**: OpenAI API (GPT-4-turbo), Perplexity API (Sonar Pro).
-   **Third-Party Services**: n8n, Twilio, WhatsApp Business API, Telegram Bot API, Razorpay API, TradingView (custom implementation).
-   **Mutual Fund Data Sources**: MFapi.in, mftool Python Library, AMFI Data for NAV and scheme information.