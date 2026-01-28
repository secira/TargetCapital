"""
Messaging Service for WhatsApp and Telegram Integration
Sends trading signals to group chats
"""
import os
import requests
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# WhatsApp Business API Configuration
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_PHONE_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_GROUP_ID = os.environ.get('WHATSAPP_GROUP_ID')

# Telegram Bot Configuration  
_raw_telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
# Extract clean token (format: numeric_id:alphanumeric_string)
import re
_token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', _raw_telegram_token)
TELEGRAM_BOT_TOKEN = _token_match.group(1) if _token_match else _raw_telegram_token
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')  # Group chat ID

def send_whatsapp_message(message_text):
    """Send message to WhatsApp group"""
    try:
        if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
            logger.warning("WhatsApp credentials not configured")
            return False
            
        url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Format message for WhatsApp
        formatted_message = format_message_for_whatsapp(message_text)
        
        payload = {
            'messaging_product': 'whatsapp',
            'to': WHATSAPP_GROUP_ID,  # Group ID or individual number
            'type': 'text',
            'text': {
                'body': formatted_message
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            logger.info("WhatsApp message sent successfully")
            return True
        else:
            logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False

def send_telegram_message(message_text):
    """Send message to Telegram group"""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.warning("Telegram credentials not configured")
            return False
            
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        # Format message for Telegram with Markdown
        formatted_message = format_message_for_telegram(message_text)
        
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': formatted_message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            logger.info("Telegram message sent successfully")
            return True
        else:
            logger.error(f"Telegram API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False

def format_message_for_whatsapp(message):
    """Format trading signal message for WhatsApp"""
    # WhatsApp supports basic formatting
    formatted = message.replace('🚨', '*')
    formatted = formatted.replace('💰', '₹')
    formatted = formatted.replace('🎯', 'Target:')
    formatted = formatted.replace('🛑', 'SL:')
    
    return formatted

def format_message_for_telegram(message):
    """Format trading signal message for Telegram with Markdown"""
    # Convert to Telegram Markdown format
    formatted = message.replace('🚨 NEW TRADING SIGNAL 🚨', '*🚨 NEW TRADING SIGNAL 🚨*')
    
    # Make important fields bold
    formatted = formatted.replace('Symbol:', '*Symbol:*')
    formatted = formatted.replace('Action:', '*Action:*')
    formatted = formatted.replace('Type:', '*Type:*')
    formatted = formatted.replace('Strategy:', '*Strategy:*')
    formatted = formatted.replace('Risk Level:', '*Risk Level:*')
    
    return formatted

def send_signal_notification(signal):
    """Send trading signal to both WhatsApp and Telegram"""
    try:
        # Format comprehensive signal message
        message = f"""🚨 NEW TRADING SIGNAL 🚨

Symbol: {signal.symbol}
{f"Company: {signal.company_name}" if signal.company_name else ""}
Action: {signal.action}
Type: {signal.signal_type.replace('_', ' ').title()}

💰 Entry: ₹{signal.entry_price or 'Market Price'}
🎯 Target: ₹{signal.target_price or 'TBD'}
🛑 Stop Loss: ₹{signal.stop_loss or 'TBD'}

{f"Quantity: {signal.quantity}" if signal.quantity else ""}
{f"Time Frame: {signal.time_frame}" if signal.time_frame else ""}
{f"Strategy: {signal.strategy_name}" if signal.strategy_name else ""}
Risk Level: {signal.risk_level or 'Medium'}

{f"Notes: {signal.notes[:100]}..." if signal.notes else ""}

⚠️ Trade at your own risk. This is for educational purposes only.

- Target Capital Team
Generated: {datetime.now(timezone.utc).strftime('%d/%m/%Y %I:%M %p')}"""

        # Send to both platforms
        whatsapp_sent = send_whatsapp_message(message)
        telegram_sent = send_telegram_message(message)
        
        # Update signal record
        if whatsapp_sent:
            signal.sent_to_whatsapp = True
        if telegram_sent:
            signal.sent_to_telegram = True
            
        # Commit changes
        from app import db
        db.session.commit()
        
        logger.info(f"Signal notification sent - WhatsApp: {whatsapp_sent}, Telegram: {telegram_sent}")
        return whatsapp_sent or telegram_sent
        
    except Exception as e:
        logger.error(f"Error sending signal notification: {e}")
        return False

def send_signup_notification(user):
    """Send notification email for new user signup"""
    try:
        from app import app
        from flask_mail import Message, Mail
        
        # Check if mail is configured
        if not app.config.get('MAIL_SERVER'):
            logger.warning("Mail server not configured for signup notifications")
            return False
            
        mail = Mail(app)
        msg = Message(
            subject="New User Signup: Target Capital",
            recipients=["uday@targetcapital.ai"],
            body=f"Hello Uday,\n\nA new user has just signed up on Target Capital!\n\nUser Details:\nName: {user.first_name} {user.last_name}\nUsername: {user.username}\nEmail: {user.email}\nSignup Time: {datetime.now(timezone.utc).strftime('%d/%m/%Y %I:%M %p')}\n\nBest regards,\nTarget Capital System"
        )
        mail.send(msg)
        logger.info(f"Signup notification sent for user {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error sending signup notification: {e}")
        return False

def test_messaging_setup():
    """Test messaging configuration"""
    test_message = "🧪 Test message from Target Capital Admin\n\nThis is a test to verify messaging setup is working correctly."
    
    print("Testing messaging setup...")
    
    # Test WhatsApp
    whatsapp_result = send_whatsapp_message(test_message)
    print(f"WhatsApp test: {'✅ Success' if whatsapp_result else '❌ Failed'}")
    
    # Test Telegram
    telegram_result = send_telegram_message(test_message)
    print(f"Telegram test: {'✅ Success' if telegram_result else '❌ Failed'}")
    
    return whatsapp_result, telegram_result

if __name__ == "__main__":
    # Test the messaging setup
    test_messaging_setup()