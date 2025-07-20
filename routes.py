from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import BlogPost, TeamMember, Testimonial, Newsletter
import logging

@app.route('/')
def index():
    """Home page route"""
    # Get featured testimonials
    testimonials = Testimonial.query.limit(3).all()
    return render_template('index.html', testimonials=testimonials)

@app.route('/about')
def about():
    """About Us page route"""
    # Get team members
    team_members = TeamMember.query.all()
    testimonials = Testimonial.query.limit(2).all()
    return render_template('about.html', team_members=team_members, testimonials=testimonials)

@app.route('/services')
def services():
    """Services page route"""
    testimonials = Testimonial.query.limit(3).all()
    return render_template('services.html', testimonials=testimonials)

@app.route('/algo-trading')
def algo_trading():
    """ALGO Trading page route"""
    testimonials = Testimonial.query.limit(2).all()
    return render_template('algo_trading.html', testimonials=testimonials)

@app.route('/blog')
def blog():
    """Blog listing page route"""
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    featured_posts = BlogPost.query.filter_by(is_featured=True).limit(3).all()
    return render_template('blog.html', posts=posts, featured_posts=featured_posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    """Individual blog post page route"""
    post = BlogPost.query.get_or_404(post_id)
    # Get related posts (same author or recent posts)
    related_posts = BlogPost.query.filter(
        BlogPost.id != post_id
    ).order_by(BlogPost.created_at.desc()).limit(3).all()
    
    testimonials = Testimonial.query.limit(2).all()
    return render_template('blog_post.html', post=post, related_posts=related_posts, testimonials=testimonials)

@app.route('/newsletter', methods=['POST'])
def subscribe_newsletter():
    """Newsletter subscription route"""
    email = request.form.get('email')
    if not email:
        flash('Please enter a valid email address.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # Check if email already exists
    existing = Newsletter.query.filter_by(email=email).first()
    if existing:
        flash('You are already subscribed to our newsletter!', 'info')
        return redirect(request.referrer or url_for('index'))
    
    # Add new subscriber
    subscriber = Newsletter(email=email)
    try:
        db.session.add(subscriber)
        db.session.commit()
        flash('Thank you for subscribing to our newsletter!', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Newsletter subscription error: {e}")
        flash('An error occurred. Please try again.', 'error')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/contact', methods=['POST'])
def contact():
    """Contact form submission route"""
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    if not all([name, email, message]):
        flash('Please fill in all required fields.', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # In a real application, you would send an email or save to database
    logging.info(f"Contact form submission: {name} ({email}) - {message}")
    flash('Thank you for your message. We will get back to you soon!', 'success')
    
    return redirect(request.referrer or url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
