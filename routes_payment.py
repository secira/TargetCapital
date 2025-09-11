"""
Payment Routes for tCapital
Handles Razorpay integration, subscription payments, and billing
"""

import os
import logging
from datetime import datetime, timedelta
from flask import request, render_template, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
import hmac
import hashlib

from app import app, db, csrf
from models import User, PricingPlan
from services.razorpay_service import razorpay_service

# Import payment models
try:
    from models.payment_models import Payment, Subscription, PaymentAttempt, PaymentStatus, SubscriptionStatus
    payment_models_available = True
except ImportError:
    payment_models_available = False

logger = logging.getLogger(__name__)

# Pricing route handled in main routes.py

@app.route('/subscribe/<plan_type>')
@login_required
def subscribe(plan_type):
    """Start subscription process for a plan"""
    if not payment_models_available:
        flash('Payment system is currently unavailable. Please try again later.', 'error')
        return redirect(url_for('pricing'))
    
    # Validate plan type
    try:
        plan_enum = PricingPlan(plan_type.upper())
    except ValueError:
        flash('Invalid subscription plan selected.', 'error')
        return redirect(url_for('pricing'))
    
    # Check if user is already on this plan
    if current_user.pricing_plan == plan_enum:
        flash('You are already subscribed to this plan.', 'info')
        return redirect(url_for('dashboard'))
    
    # Get plan details
    plans = razorpay_service.get_subscription_plans()
    plan_details = plans.get(plan_type.upper())
    
    if not plan_details:
        flash('Plan not found.', 'error')
        return redirect(url_for('pricing'))
    
    # Handle free plan
    if plan_type.upper() == 'FREE':
        current_user.pricing_plan = PricingPlan.FREE
        db.session.commit()
        flash('Successfully switched to Free plan.', 'success')
        return redirect(url_for('dashboard'))
    
    # Create payment attempt record
    payment_attempt = PaymentAttempt(
        user_id=current_user.id,
        plan_type=plan_enum,
        amount=plan_details['price'],
        status='initiated',
        user_agent=request.headers.get('User-Agent'),
        ip_address=request.remote_addr
    )
    db.session.add(payment_attempt)
    db.session.commit()
    
    # Create Razorpay order
    order_result = razorpay_service.create_subscription_order(
        user_id=current_user.id,
        plan_type=plan_type.upper(),
        amount=plan_details['price']
    )
    
    if not order_result['success']:
        payment_attempt.status = 'failed'
        db.session.commit()
        flash(f'Payment initialization failed: {order_result["error"]}', 'error')
        return redirect(url_for('pricing'))
    
    # Update payment attempt with order ID
    payment_attempt.razorpay_order_id = order_result['order_id']
    payment_attempt.session_data = {
        'plan_details': plan_details,
        'order_details': order_result
    }
    db.session.commit()
    
    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        razorpay_order_id=order_result['order_id'],
        amount=plan_details['price'],
        plan_type=plan_enum,
        plan_duration_days=plan_details['duration_days'],
        description=f"Subscription to {plan_details['name']}"
    )
    db.session.add(payment)
    db.session.commit()
    
    return render_template('payment/checkout.html',
                         plan=plan_details,
                         order=order_result,
                         user=current_user)

@app.route('/payment/verify', methods=['POST'])
@login_required
def verify_payment():
    """Verify payment completion from Razorpay"""
    if not payment_models_available:
        return jsonify({'success': False, 'error': 'Payment system unavailable'})
    
    try:
        # Get payment details from request
        razorpay_order_id = request.form.get('razorpay_order_id')
        razorpay_payment_id = request.form.get('razorpay_payment_id')
        razorpay_signature = request.form.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({'success': False, 'error': 'Missing payment parameters'})
        
        # Find payment record
        payment = Payment.query.filter_by(
            user_id=current_user.id,
            razorpay_order_id=razorpay_order_id
        ).first()
        
        if not payment:
            return jsonify({'success': False, 'error': 'Payment record not found'})
        
        # Verify payment signature
        signature_valid = razorpay_service.verify_payment_signature(
            razorpay_order_id, razorpay_payment_id, razorpay_signature
        )
        
        if not signature_valid:
            payment.mark_as_failed('Invalid signature')
            return jsonify({'success': False, 'error': 'Payment verification failed'})
        
        # Get payment details from Razorpay
        payment_details = razorpay_service.get_payment_details(razorpay_payment_id)
        
        if not payment_details['success']:
            payment.mark_as_failed('Could not verify payment details')
            return jsonify({'success': False, 'error': 'Payment verification failed'})
        
        # Mark payment as completed
        payment.mark_as_paid(
            razorpay_payment_id=razorpay_payment_id,
            payment_method=payment_details['payment'].get('method')
        )
        payment.razorpay_signature = razorpay_signature
        
        # Create subscription
        subscription = Subscription.create_from_payment(payment)
        db.session.add(subscription)
        
        # Update user's plan
        current_user.pricing_plan = payment.plan_type
        current_user.subscription_expires_at = subscription.end_date
        
        # Update payment attempt
        payment_attempt = PaymentAttempt.query.filter_by(
            user_id=current_user.id,
            razorpay_order_id=razorpay_order_id
        ).first()
        
        if payment_attempt:
            payment_attempt.status = 'completed'
            payment_attempt.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Payment successful for user {current_user.id}: {payment.plan_type.value}")
        
        return jsonify({
            'success': True,
            'message': 'Payment successful! Your subscription has been activated.',
            'redirect_url': url_for('payment_success', payment_id=payment.id)
        })
        
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        return jsonify({'success': False, 'error': 'Payment processing failed'})

@app.route('/payment/success/<int:payment_id>')
@login_required
def payment_success(payment_id):
    """Payment success page"""
    if not payment_models_available:
        flash('Payment system unavailable.', 'error')
        return redirect(url_for('dashboard'))
    
    payment = Payment.query.filter_by(
        id=payment_id,
        user_id=current_user.id,
        status=PaymentStatus.COMPLETED
    ).first()
    
    if not payment:
        flash('Payment not found or not completed.', 'error')
        return redirect(url_for('dashboard'))
    
    subscription = Subscription.query.filter_by(payment_id=payment.id).first()
    
    return render_template('payment/success.html',
                         payment=payment,
                         subscription=subscription)

@app.route('/payment/failed')
@login_required
def payment_failed():
    """Payment failure page"""
    return render_template('payment/failed.html')

@app.route('/account/billing')
@login_required
def billing_history():
    """User billing history and subscription management"""
    if not payment_models_available:
        flash('Billing system unavailable.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get user's payments and subscriptions
    payments = Payment.query.filter_by(user_id=current_user.id).order_by(Payment.created_at.desc()).all()
    subscriptions = Subscription.query.filter_by(user_id=current_user.id).order_by(Subscription.created_at.desc()).all()
    
    # Get current active subscription
    active_subscription = Subscription.query.filter_by(
        user_id=current_user.id,
        status=SubscriptionStatus.ACTIVE
    ).filter(Subscription.end_date > datetime.utcnow()).first()
    
    return render_template('account/billing.html',
                         payments=payments,
                         subscriptions=subscriptions,
                         active_subscription=active_subscription)

@app.route('/account/upgrade')
@login_required
def upgrade_plan():
    """Plan upgrade page"""
    plans = razorpay_service.get_subscription_plans()
    current_plan = current_user.pricing_plan.value if current_user.pricing_plan else 'FREE'
    
    # Calculate upgrade costs
    upgrade_options = {}
    for plan_key, plan_details in plans.items():
        if plan_key != current_plan:
            upgrade_cost = razorpay_service.calculate_plan_upgrade_cost(
                current_plan, plan_key
            )
            if upgrade_cost['success']:
                upgrade_options[plan_key] = {
                    'plan': plan_details,
                    'cost': upgrade_cost['upgrade_cost']
                }
    
    return render_template('account/upgrade.html',
                         current_plan=current_plan,
                         upgrade_options=upgrade_options)

@app.route('/webhook/razorpay', methods=['POST'])
@csrf.exempt  # Exempt from CSRF protection for external webhook
def razorpay_webhook():
    """Handle Razorpay webhooks"""
    if not payment_models_available:
        return jsonify({'status': 'error', 'message': 'Payment system unavailable'}), 500
    
    try:
        # Verify webhook signature for security
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_body = request.get_data()
        webhook_secret = os.environ.get('RAZORPAY_WEBHOOK_SECRET')
        
        if not webhook_signature or not webhook_secret:
            logger.warning("Missing webhook signature or secret")
            return jsonify({'status': 'error', 'message': 'Invalid webhook'}), 400
        
        # Verify HMAC signature
        expected_signature = hmac.new(
            webhook_secret.encode(),
            webhook_body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(webhook_signature, expected_signature):
            logger.warning("Invalid webhook signature")
            return jsonify({'status': 'error', 'message': 'Invalid signature'}), 403
        
        # Process webhook event  
        event_data = request.get_json()
        event_type = event_data.get('event')
        
        logger.info(f"Received Razorpay webhook: {event_type}")
        
        if event_type == 'payment.captured':
            # Handle successful payment
            payment_data = event_data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            
            if order_id:
                payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
                if payment and payment.status == PaymentStatus.PENDING:
                    # Payment was successful, activate subscription
                    payment.mark_as_paid(payment_data.get('id'))
                    
                    # Create subscription if not exists
                    if not payment.subscription:
                        subscription = Subscription.create_from_payment(payment)
                        db.session.add(subscription)
                        db.session.commit()
        
        elif event_type == 'payment.failed':
            # Handle failed payment
            payment_data = event_data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_data.get('order_id')
            
            if order_id:
                payment = Payment.query.filter_by(razorpay_order_id=order_id).first()
                if payment:
                    payment.mark_as_failed('Payment failed via webhook')
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Admin routes for payment management
@app.route('/admin/payments')
@login_required
def admin_payments():
    """Admin panel for payment management"""
    # Add admin check here
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    if not payment_models_available:
        flash('Payment system unavailable.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    # Get recent payments
    payments = Payment.query.order_by(Payment.created_at.desc()).limit(100).all()
    
    # Payment statistics
    stats = {
        'total_revenue': db.session.query(db.func.sum(Payment.amount)).filter_by(status=PaymentStatus.COMPLETED).scalar() or 0,
        'pending_payments': Payment.query.filter_by(status=PaymentStatus.PENDING).count(),
        'failed_payments': Payment.query.filter_by(status=PaymentStatus.FAILED).count(),
        'active_subscriptions': Subscription.query.filter_by(status=SubscriptionStatus.ACTIVE).count()
    }
    
    return render_template('admin/payments.html',
                         payments=payments,
                         stats=stats)