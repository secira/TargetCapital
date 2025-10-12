"""
Update Knowledge Base articles with featured images
"""
from app import app, db
from models import BlogPost

def update_images():
    with app.app_context():
        # Map articles to images
        article_images = {
            'day-trading-comprehensive-guide-indian-markets': '/static/images/stock_market_trading_be622557.jpg',
            'swing-trading-capturing-multi-day-price-movements': '/static/images/stock_market_trading_d0cc73ef.jpg',
            'technical-indicators-complete-guide-indian-traders': '/static/images/stock_market_trading_e49ccf23.jpg',
            'options-futures-complete-guide-fo-trading': '/static/images/stock_market_trading_abc3082c.jpg',
            'trading-psychology-mastering-mind-market-success': '/static/images/stock_market_trading_72220cd7.jpg'
        }
        
        for slug, image_path in article_images.items():
            article = BlogPost.query.filter_by(slug=slug).first()
            if article:
                article.featured_image = image_path
                print(f"✅ Updated image for: {article.title}")
        
        db.session.commit()
        print("\n🎉 All article images updated successfully!")

if __name__ == '__main__':
    update_images()
