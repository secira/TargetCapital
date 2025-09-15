# SMS OTP Service using Twilio integration
# From blueprint:twilio_send_message integration

import os
import random
import string
from datetime import datetime, timedelta

# Simplified Twilio client import to avoid gevent recursion issues
from twilio.rest import Client

# Use standard client to avoid recursion problems
http_client = None

# Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN") 
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

class SMSService:
    def __init__(self):
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            try:
                # Initialize standard Twilio client
                self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                print("✅ Twilio client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Twilio client: {e}")
                self.client = None
        else:
            self.client = None
            print("⚠️ Twilio credentials not configured - OTP will be logged instead of sent")
    
    def generate_otp(self, length=6):
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp(self, mobile_number: str, otp: str) -> bool:
        """Send OTP via SMS"""
        message_body = f"Your Target Capital OTP is: {otp}. Valid for 10 minutes. Do not share this code."
        
        try:
            if self.client and TWILIO_PHONE_NUMBER:
                # Ensure mobile number is in E.164 format
                if not mobile_number.startswith('+'):
                    # Assume Indian number if no country code
                    mobile_number = f"+91{mobile_number}"
                
                message = self.client.messages.create(
                    body=message_body,
                    from_=TWILIO_PHONE_NUMBER,
                    to=mobile_number
                )
                print(f"✅ OTP sent via SMS. Message SID: {message.sid}")
                return True
            else:
                # Development mode - log OTP instead of sending
                print(f"📱 DEV MODE - OTP for {mobile_number}: {otp}")
                return True
                
        except Exception as e:
            print(f"❌ Failed to send OTP: {str(e)}")
            # In development, still return True and log the OTP
            if not self.client:
                print(f"📱 DEV MODE - OTP for {mobile_number}: {otp}")
                return True
            return False
    
    def format_mobile_number(self, mobile_number: str) -> str:
        """Format mobile number to standard format"""
        # Remove all non-digit characters
        mobile_number = ''.join(filter(str.isdigit, mobile_number))
        
        # Add country code for Indian numbers
        if len(mobile_number) == 10:
            mobile_number = f"+91{mobile_number}"
        elif len(mobile_number) == 12 and mobile_number.startswith('91'):
            mobile_number = f"+{mobile_number}"
        elif not mobile_number.startswith('+'):
            mobile_number = f"+{mobile_number}"
            
        return mobile_number
    
    def validate_mobile_number(self, mobile_number: str) -> bool:
        """Validate Indian mobile number format"""
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, mobile_number))
        
        # Check for valid Indian mobile number
        if len(digits_only) == 10:
            # Indian mobile numbers start with 6, 7, 8, or 9
            return digits_only[0] in ['6', '7', '8', '9']
        elif len(digits_only) == 12:
            # With country code +91
            return digits_only.startswith('91') and digits_only[2] in ['6', '7', '8', '9']
        
        return False

# Global SMS service instance
sms_service = SMSService()