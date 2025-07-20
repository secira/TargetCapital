#!/usr/bin/env python3
"""
Setup script to create admin user and sample blog posts
"""

from app import app, db
from models import User, BlogPost
from datetime import datetime

def setup_admin_user():
    """Create admin user if it doesn't exist"""
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists")
            # Make sure the existing user is admin
            admin.is_admin = True
            db.session.commit()
            return admin
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@aitradebot.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with username: admin, password: admin123")
        return admin

def create_sample_blog_posts():
    """Create sample blog posts"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found. Creating admin user first.")
            admin = setup_admin_user()
        
        # Check if posts already exist
        if BlogPost.query.count() > 0:
            print("Blog posts already exist")
            return
        
        sample_posts = [
            {
                'title': 'AI-Powered Trading: The Future of Investment',
                'content': '''
                <h2>The Revolution in Trading Technology</h2>
                <p>Artificial Intelligence is transforming the investment landscape in unprecedented ways. Modern AI systems can analyze vast amounts of market data, identify patterns, and execute trades faster than any human trader.</p>
                
                <h3>Key Benefits of AI Trading</h3>
                <ul>
                    <li><strong>Speed and Efficiency:</strong> AI can process thousands of data points in milliseconds</li>
                    <li><strong>Emotion-Free Decisions:</strong> Removes human bias and emotional trading</li>
                    <li><strong>24/7 Market Monitoring:</strong> Never sleeps, constantly monitoring opportunities</li>
                    <li><strong>Risk Management:</strong> Advanced algorithms for portfolio protection</li>
                </ul>
                
                <h3>Real-World Applications</h3>
                <p>Today's AI trading platforms utilize machine learning algorithms to:</p>
                <ol>
                    <li>Predict market movements with high accuracy</li>
                    <li>Optimize portfolio allocation in real-time</li>
                    <li>Identify arbitrage opportunities across markets</li>
                    <li>Execute high-frequency trading strategies</li>
                </ol>
                
                <p>As we move forward, AI will continue to democratize sophisticated trading strategies, making them accessible to retail investors worldwide.</p>
                ''',
                'excerpt': 'Discover how AI is revolutionizing investment strategies and making sophisticated trading accessible to everyone.',
                'category': 'Technology',
                'tags': 'AI, trading, technology, investment, machine learning',
                'featured_image': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800',
                'meta_description': 'Learn how AI-powered trading is transforming investment strategies and making sophisticated trading accessible to all investors.',
                'status': 'published',
                'is_featured': True
            },
            {
                'title': 'Understanding Market Volatility in 2024',
                'content': '''
                <h2>Navigating Today's Complex Markets</h2>
                <p>Market volatility has become a defining characteristic of modern trading. Understanding its causes and implications is crucial for successful investing.</p>
                
                <h3>Factors Driving Volatility</h3>
                <p>Several key factors contribute to increased market volatility:</p>
                <ul>
                    <li>Global economic uncertainty</li>
                    <li>Geopolitical tensions</li>
                    <li>Central bank policy changes</li>
                    <li>Technological disruption</li>
                </ul>
                
                <h3>Strategies for Volatile Markets</h3>
                <p>Smart investors can turn volatility into opportunity:</p>
                <ol>
                    <li><strong>Diversification:</strong> Spread risk across asset classes</li>
                    <li><strong>Dollar-Cost Averaging:</strong> Regular investments reduce timing risk</li>
                    <li><strong>Options Strategies:</strong> Use derivatives for protection</li>
                    <li><strong>Stay Informed:</strong> Monitor news and market indicators</li>
                </ol>
                
                <p>Remember, volatility is a normal part of market cycles. With proper strategy and risk management, investors can navigate these periods successfully.</p>
                ''',
                'excerpt': 'Learn strategies to navigate market volatility and turn uncertainty into investment opportunities.',
                'category': 'Market Analysis',
                'tags': 'volatility, market analysis, investment strategy, risk management',
                'featured_image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800',
                'meta_description': 'Expert strategies for navigating market volatility and turning uncertainty into profitable investment opportunities.',
                'status': 'published',
                'is_featured': True
            },
            {
                'title': 'NSE India: Your Guide to Indian Stock Markets',
                'content': '''
                <h2>Exploring India's Premier Stock Exchange</h2>
                <p>The National Stock Exchange of India (NSE) is one of the world's largest stock exchanges by market capitalization and trading volume. For investors looking to tap into India's growing economy, understanding NSE is essential.</p>
                
                <h3>Key Indices to Watch</h3>
                <ul>
                    <li><strong>Nifty 50:</strong> The benchmark index of top 50 companies</li>
                    <li><strong>Bank Nifty:</strong> Tracks banking sector performance</li>
                    <li><strong>Nifty IT:</strong> Technology sector index</li>
                    <li><strong>Nifty Pharma:</strong> Pharmaceutical sector performance</li>
                </ul>
                
                <h3>Top Performing Sectors</h3>
                <p>Several sectors have shown remarkable growth:</p>
                <ol>
                    <li>Information Technology</li>
                    <li>Banking and Financial Services</li>
                    <li>Pharmaceuticals</li>
                    <li>Consumer Goods</li>
                </ol>
                
                <h3>Getting Started with NSE Trading</h3>
                <p>Our platform provides real-time NSE data, including:</p>
                <ul>
                    <li>Live stock quotes and prices</li>
                    <li>Market indices and performance</li>
                    <li>Top gainers and losers</li>
                    <li>Sector-wise analysis</li>
                </ul>
                
                <p>Start building your Indian portfolio today with comprehensive NSE market data and AI-powered insights.</p>
                ''',
                'excerpt': 'Complete guide to trading on NSE India with real-time market data and expert insights.',
                'category': 'Markets',
                'tags': 'NSE, India, stock market, Nifty, trading',
                'featured_image': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800',
                'meta_description': 'Complete guide to NSE India trading with real-time market data, key indices, and investment strategies.',
                'status': 'published',
                'is_featured': True
            },
            {
                'title': 'Building Your First Stock Portfolio',
                'content': '''
                <h2>Portfolio Construction Fundamentals</h2>
                <p>Creating a well-balanced stock portfolio is the foundation of successful long-term investing. This guide will help beginners understand the key principles of portfolio construction.</p>
                
                <h3>Core Principles</h3>
                <ol>
                    <li><strong>Diversification:</strong> Don't put all eggs in one basket</li>
                    <li><strong>Risk Assessment:</strong> Understand your risk tolerance</li>
                    <li><strong>Time Horizon:</strong> Align investments with your goals</li>
                    <li><strong>Regular Review:</strong> Monitor and rebalance periodically</li>
                </ol>
                
                <h3>Asset Allocation Strategy</h3>
                <p>A typical balanced portfolio might include:</p>
                <ul>
                    <li>60% Stocks (growth potential)</li>
                    <li>30% Bonds (stability)</li>
                    <li>10% Alternative investments (diversification)</li>
                </ul>
                
                <h3>Common Beginner Mistakes</h3>
                <p>Avoid these pitfalls:</p>
                <ul>
                    <li>Chasing hot stocks</li>
                    <li>Timing the market</li>
                    <li>Lack of diversification</li>
                    <li>Emotional decision making</li>
                </ul>
                
                <p>Remember, successful investing is a marathon, not a sprint. Start with a solid foundation and build gradually.</p>
                ''',
                'excerpt': 'Essential guide for beginners on building a well-balanced stock portfolio with proper diversification.',
                'category': 'Education',
                'tags': 'portfolio, diversification, beginner, investing, strategy',
                'featured_image': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800',
                'meta_description': 'Learn how to build your first stock portfolio with expert tips on diversification, risk management, and asset allocation.',
                'status': 'published',
                'is_featured': False
            },
            {
                'title': 'Technical Analysis: Reading Market Charts',
                'content': '''
                <h2>Mastering Chart Analysis</h2>
                <p>Technical analysis is the study of price movements and trading patterns to predict future market behavior. Understanding charts is essential for timing your trades effectively.</p>
                
                <h3>Key Chart Patterns</h3>
                <ul>
                    <li><strong>Support and Resistance:</strong> Price levels where stocks tend to bounce</li>
                    <li><strong>Trend Lines:</strong> Direction of price movement over time</li>
                    <li><strong>Moving Averages:</strong> Smoothed price trends</li>
                    <li><strong>Volume Analysis:</strong> Trading activity confirmation</li>
                </ul>
                
                <h3>Popular Technical Indicators</h3>
                <ol>
                    <li>RSI (Relative Strength Index)</li>
                    <li>MACD (Moving Average Convergence Divergence)</li>
                    <li>Bollinger Bands</li>
                    <li>Stochastic Oscillator</li>
                </ol>
                
                <p>Our platform provides advanced charting tools with all these indicators and more, helping you make informed trading decisions.</p>
                ''',
                'excerpt': 'Learn technical analysis fundamentals and chart reading techniques for better trading decisions.',
                'category': 'Education',
                'tags': 'technical analysis, charts, indicators, trading',
                'featured_image': 'https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=800',
                'meta_description': 'Master technical analysis and chart reading with essential patterns, indicators, and trading strategies.',
                'status': 'draft',
                'is_featured': False
            }
        ]
        
        for post_data in sample_posts:
            post = BlogPost(
                title=post_data['title'],
                content=post_data['content'],
                excerpt=post_data['excerpt'],
                author_id=admin.id,
                author_name=admin.get_full_name(),
                category=post_data['category'],
                tags=post_data['tags'],
                featured_image=post_data['featured_image'],
                meta_description=post_data['meta_description'],
                status=post_data['status'],
                is_featured=post_data['is_featured']
            )
            
            # Generate slug
            post.slug = post.generate_slug()
            
            # Set published date for published posts
            if post.status == 'published':
                post.published_at = datetime.utcnow()
            
            db.session.add(post)
        
        db.session.commit()
        print(f"Created {len(sample_posts)} sample blog posts")

if __name__ == '__main__':
    print("Setting up admin user and sample content...")
    setup_admin_user()
    create_sample_blog_posts()
    print("Setup complete!")
    print("\nAdmin Access:")
    print("- Username: admin")
    print("- Password: admin123")
    print("- Access admin panel from user menu after login")