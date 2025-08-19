"""
Fresh Perplexity API Service for AI Investment Advisor
Clean implementation with proper model names and error handling
"""
import os
import requests
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class PerplexityAPI:
    """Clean Perplexity API integration for investment advice"""
    
    def __init__(self):
        self.api_key = os.environ.get('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable is required")
        
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Use correct model name (updated for 2025)
        self.model = "sonar-pro"
        
        logger.info("Perplexity API initialized successfully")
    
    def get_investment_advice(self, user_message: str, conversation_history: list = None) -> Tuple[str, Dict]:
        """
        Get investment advice from Perplexity API
        Returns: (response_text, usage_info)
        """
        try:
            # Build conversation messages
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert investment advisor specializing in Indian and global stock markets. 
                    Provide accurate, real-time financial insights, market analysis, and investment recommendations.
                    Focus on practical advice with current market data when possible.
                    Always cite sources when providing specific stock prices or market data."""
                }
            ]
            
            # Add conversation history with proper alternating validation
            if conversation_history:
                valid_history = []
                last_role = "system"  # Start after system message
                
                for msg in conversation_history[-6:]:
                    msg_role = msg.get('role')
                    if msg_role in ['user', 'assistant'] and msg_role != last_role:
                        valid_history.append(msg)
                        last_role = msg_role
                
                messages.extend(valid_history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.9,
                "return_images": False,
                "return_related_questions": False,
                "search_recency_filter": "month",
                "stream": False
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                usage_info = {
                    'prompt_tokens': data.get('usage', {}).get('prompt_tokens', 0),
                    'completion_tokens': data.get('usage', {}).get('completion_tokens', 0),
                    'total_tokens': data.get('usage', {}).get('total_tokens', 0),
                    'processing_time': response.elapsed.total_seconds()
                }
                
                logger.info(f"Perplexity API call successful. Tokens used: {usage_info['total_tokens']}")
                return content, usage_info
                
            else:
                error_data = response.json() if response.content else {"error": "Unknown error"}
                logger.error(f"Perplexity API error: {response.status_code} - {error_data}")
                
                # Return fallback response
                fallback = """I'm experiencing technical difficulties accessing real-time market data. 
                However, I can still provide general investment guidance based on fundamental principles:

                **General Investment Tips:**
                1. **Diversification**: Spread investments across different sectors and asset classes
                2. **Risk Management**: Never invest more than you can afford to lose
                3. **Research**: Always research companies before investing
                4. **Long-term Perspective**: Focus on long-term growth rather than short-term gains
                5. **Regular Monitoring**: Review your portfolio periodically

                For real-time market data and specific stock recommendations, please try again in a moment."""
                
                return fallback, {"error": True, "status_code": response.status_code}
                
        except requests.exceptions.Timeout:
            logger.error("Perplexity API timeout")
            return "Request timed out. Please try again with a shorter question.", {"error": True, "type": "timeout"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API request error: {e}")
            return "Unable to connect to AI service. Please check your internet connection and try again.", {"error": True, "type": "connection"}
            
        except Exception as e:
            logger.error(f"Unexpected error in Perplexity API: {e}")
            return "An unexpected error occurred. Please try again.", {"error": True, "type": "unexpected"}
    
    def validate_connection(self) -> bool:
        """Test if Perplexity API is accessible"""
        try:
            test_response, _ = self.get_investment_advice("Test connection")
            return not test_response.startswith("I'm experiencing technical difficulties")
        except Exception:
            return False