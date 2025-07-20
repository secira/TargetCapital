#!/usr/bin/env python3
"""
Script to display OAuth configuration URLs for Google and Facebook
"""

import os

def display_oauth_config():
    """Display OAuth configuration instructions"""
    
    # Get the current domain from environment
    domain = os.environ.get('REPLIT_DEV_DOMAIN', 'your-repl-domain.replit.dev')
    
    print("\n" + "="*70)
    print("📋 OAUTH CONFIGURATION SETUP")
    print("="*70)
    
    print("\n🔵 GOOGLE OAUTH SETUP:")
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Create a new OAuth 2.0 Client ID")
    print("3. Add these Authorized redirect URIs:")
    print(f"   • https://{domain}/auth/google/authorized")
    print(f"   • https://{domain}/auth/google/callback")
    
    print("\n📘 FACEBOOK OAUTH SETUP:")
    print("1. Go to: https://developers.facebook.com/apps/")
    print("2. Create a new app and enable Facebook Login")
    print("3. Add these Valid OAuth Redirect URIs:")
    print(f"   • https://{domain}/auth/facebook/authorized")
    print(f"   • https://{domain}/auth/facebook/callback")
    
    print("\n🔑 Environment Variables Needed:")
    google_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'NOT_SET')
    google_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'NOT_SET')
    facebook_id = os.environ.get('FACEBOOK_APP_ID', 'NOT_SET')
    facebook_secret = os.environ.get('FACEBOOK_APP_SECRET', 'NOT_SET')
    
    print(f"GOOGLE_OAUTH_CLIENT_ID: {'✅ SET' if google_id != 'NOT_SET' else '❌ NOT SET'}")
    print(f"GOOGLE_OAUTH_CLIENT_SECRET: {'✅ SET' if google_secret != 'NOT_SET' else '❌ NOT SET'}")
    print(f"FACEBOOK_APP_ID: {'✅ SET' if facebook_id != 'NOT_SET' else '❌ NOT SET'}")
    print(f"FACEBOOK_APP_SECRET: {'✅ SET' if facebook_secret != 'NOT_SET' else '❌ NOT SET'}")
    
    print("\n🌐 Your Current Domain:")
    print(f"https://{domain}")
    
    print("\n🚀 OAuth Login URLs:")
    print(f"Google: https://{domain}/auth/google")
    print(f"Facebook: https://{domain}/auth/facebook")
    
    print("\n" + "="*70)
    print("Ready to test OAuth authentication! 🎉")
    print("="*70)

if __name__ == '__main__':
    display_oauth_config()