# AI TradeBot - Flask Web Application

## Overview

AI TradeBot is a Flask-based web application that provides an AI-powered stock trading platform with portfolio analysis and algorithmic trading services. The application features a modern, responsive frontend with multiple service pages and a blog system for sharing trading insights.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Database**: SQLite (default) with PostgreSQL support via DATABASE_URL environment variable
- **Session Management**: Flask sessions with configurable secret key
- **Logging**: Python's built-in logging module configured at DEBUG level
- **Deployment**: WSGI-compatible with ProxyFix middleware for reverse proxy support

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Inter)
- **JavaScript**: Vanilla JavaScript with modern ES6+ features
- **Responsive Design**: Mobile-first approach using Bootstrap's grid system

### Application Structure
- **Entry Point**: `main.py` - Development server runner
- **Application Factory**: `app.py` - Flask app initialization and configuration
- **Models**: `models.py` - SQLAlchemy database models
- **Routes**: `routes.py` - URL routing and view functions
- **Templates**: `/templates/` - Jinja2 HTML templates
- **Static Assets**: `/static/` - CSS, JavaScript, and media files

## Key Components

### Database Models
1. **BlogPost**: Blog articles with title, content, author, featured images, and publishing metadata
2. **TeamMember**: Team profiles with roles, bio, images, and social links
3. **Testimonial**: Client testimonials with ratings and company information
4. **Newsletter**: Email subscription management

### Page Structure
1. **Home Page** (`/`): Hero section, features, services overview, stats, testimonials
2. **About Page** (`/about`): Company mission, team profiles, testimonials
3. **Services Page** (`/services`): Service descriptions, benefits, testimonials
4. **ALGO Trading Page** (`/algo-trading`): Specialized algorithmic trading features
5. **Blog** (`/blog`): Article listings with pagination and featured posts
6. **Blog Posts** (`/blog/<id>`): Individual article pages with related content

### Frontend Features
- Responsive navigation with dropdown menus
- Gradient backgrounds and modern UI components
- Interactive elements with smooth scrolling
- Form validation and user feedback
- Animation and counter effects
- Modal dialogs and tooltips
- Newsletter subscription functionality

## Data Flow

### Request Processing
1. User requests are routed through Flask's URL routing system
2. Route handlers in `routes.py` process requests and query database via SQLAlchemy models
3. Data is passed to Jinja2 templates for rendering
4. Rendered HTML is returned to the client with static assets served by Flask

### Database Operations
- Database models are defined using SQLAlchemy's declarative base
- Database initialization occurs on application startup with automatic table creation
- Database connections are managed by SQLAlchemy with connection pooling and health checks

### Client-Side Interactions
- JavaScript handles form submissions, animations, and user interface enhancements
- AJAX requests (where implemented) communicate with Flask endpoints
- Client-side validation complements server-side form processing

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM integration
- Werkzeug: WSGI utilities and middleware

### Frontend Libraries
- Bootstrap 5.3.0: CSS framework and components
- Font Awesome 6.4.0: Icon library
- Google Fonts (Inter): Typography

### Infrastructure Dependencies
- Database: SQLite (development) / PostgreSQL (production)
- Web server: Any WSGI-compatible server (development uses Flask's built-in server)

## Deployment Strategy

### Environment Configuration
- Database URL configurable via `DATABASE_URL` environment variable
- Session secret configurable via `SESSION_SECRET` environment variable
- Application supports both SQLite (development) and PostgreSQL (production)

### Production Considerations
- ProxyFix middleware configured for reverse proxy deployment
- SQLAlchemy connection pooling with health checks enabled
- Debug mode controlled by environment
- Static file serving handled by web server in production

### Development Setup
- Application runs on `0.0.0.0:5000` with debug mode enabled
- Database tables automatically created on first run
- Hot reloading enabled for development

### Scalability Features
- Database connection pooling with automatic reconnection
- Stateless application design suitable for horizontal scaling
- Separation of concerns between models, routes, and templates
- Environment-based configuration for different deployment stages