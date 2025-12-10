import os
import json
import time
import uuid
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import requests
from models import (ChatConversation, ChatMessage, ChatbotKnowledgeBase, 
                   Portfolio, User, AIStockPick)
from app import db
from middleware.tenant_middleware import get_current_tenant_id, TenantQuery, create_for_tenant

logger = logging.getLogger(__name__)

class InvestmentChatbot:
    """AI-Powered Investment Explanation Chatbot using Perplexity Sonar"""
    
    def __init__(self):
        self.perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.system_prompt = self._get_system_prompt()
        self._initialize_perplexity_api()
        
    def _initialize_perplexity_api(self):
        """Initialize Perplexity API"""
        if not self.perplexity_api_key:
            logger.error("PERPLEXITY_API_KEY not found in environment variables")
            return
            
        try:
            # Test connection with a simple call
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            logger.info("Perplexity API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Perplexity API: {e}")
            
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI investment chatbot"""
        return """You are an AI Investment Advisor powered by Perplexity for tCapital, India's leading AI-powered trading platform.

Your expertise includes:
1. Real-time market analysis and current Indian stock market insights
2. Educational investment concepts explained in simple language
3. Portfolio analysis and personalized investment guidance
4. Current news, trends, and market developments affecting Indian stocks
5. Live data from NSE, BSE, and global markets impacting Indian investments

Core capabilities:
- Provide current market data and real-time analysis
- Explain complex financial concepts with practical examples
- Offer personalized advice based on user portfolio context
- Share latest market news, regulatory changes, and sector updates
- Analyze current economic indicators affecting Indian markets

Guidelines:
- Use real-time web data to provide current market insights
- Reference recent news, earnings, and market developments
- Focus on educational content while being aware of current market conditions
- Provide context-aware advice using latest market information
- Include current prices, trends, and market sentiment in responses
- Cite sources when referencing specific market data or news

Response style:
- Concise, informative, and data-driven
- Include current market context and real-time insights
- Use bullet points for clarity
- End with engaging follow-up questions
- Reference Indian market specifics (₹, NSE, BSE, SEBI, etc.)

Remember: You provide educational insights with real-time market context, not guaranteed investment advice."""

    def get_or_create_conversation(self, user_id: int, session_id: str = None) -> ChatConversation:
        """Get existing conversation or create new one"""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        conversation = TenantQuery(ChatConversation).filter_by(
            user_id=user_id, 
            session_id=session_id,
            is_active=True
        ).first()
        
        if not conversation:
            conversation = create_for_tenant(ChatConversation,
                user_id=user_id,
                session_id=session_id,
                title="New Investment Chat",
                is_active=True
            )
            db.session.add(conversation)
            db.session.commit()
            logger.info(f"Created new conversation {session_id} for user {user_id}")
            
        return conversation

    def get_user_context(self, user_id: int) -> Dict:
        """Get user's portfolio and trading context"""
        context = {
            'portfolio_holdings': [],
            'total_portfolio_value': 0,
            'recent_picks': [],
            'user_plan': 'FREE'
        }
        
        try:
            # Get user info (tenant-scoped)
            user = TenantQuery(User).filter_by(id=user_id).first()
            if user:
                context['user_plan'] = user.pricing_plan.value if user.pricing_plan else 'FREE'
                
            # Get portfolio holdings (tenant-scoped)
            portfolio_items = TenantQuery(Portfolio).filter_by(user_id=user_id).all()[:10]
            for item in portfolio_items:
                context['portfolio_holdings'].append({
                    'symbol': item.ticker_symbol,
                    'name': item.stock_name,
                    'quantity': item.quantity,
                    'current_value': item.current_value,
                    'pnl_percentage': item.pnl_percentage,
                    'sector': item.sector
                })
                
            context['total_portfolio_value'] = sum(
                item.current_value or 0 for item in portfolio_items
            )
            
            # Get recent AI picks
            recent_picks = AIStockPick.query.order_by(
                AIStockPick.pick_date.desc()
            ).limit(3).all()
            
            for pick in recent_picks:
                context['recent_picks'].append({
                    'symbol': pick.symbol,
                    'recommendation': pick.recommendation,
                    'current_price': pick.current_price,
                    'target_price': pick.target_price
                })
                
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            
        return context

    def search_knowledge_base(self, query: str, limit: int = 3) -> List[ChatbotKnowledgeBase]:
        """Search knowledge base for relevant information"""
        query_words = query.lower().split()
        
        # Search by keywords and content
        knowledge_items = []
        all_items = ChatbotKnowledgeBase.query.filter_by(is_active=True).all()
        
        for item in all_items:
            score = 0
            keywords = item.get_keywords_list()
            content_lower = item.content.lower()
            topic_lower = item.topic.lower()
            
            # Score based on keyword matches
            for word in query_words:
                if word in keywords:
                    score += 3
                if word in topic_lower:
                    score += 2
                if word in content_lower:
                    score += 1
                    
            if score > 0:
                knowledge_items.append((score, item))
                
        # Sort by score and return top results
        knowledge_items.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in knowledge_items[:limit]]

    def generate_perplexity_response(self, 
                                    user_message: str, 
                                    conversation: ChatConversation,
                                    user_context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """Generate AI response using Perplexity Sonar"""
        return self.generate_response(user_message, conversation, user_context)
    
    def generate_response(self, 
                         user_message: str, 
                         conversation: ChatConversation,
                         user_context: Optional[Dict] = None) -> Tuple[str, Dict]:
        """Generate AI response using Perplexity Sonar"""
        if not self.perplexity_api_key:
            return "I'm sorry, the AI service is temporarily unavailable. Please try again later.", {}
            
        start_time = time.time()
        
        try:
            # Build conversation history
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add user context if available
            if user_context:
                context_message = self._format_context_message(user_context)
                if context_message:
                    messages.append({"role": "system", "content": context_message})
            
            # Add recent conversation history (last 6 messages for better performance)
            try:
                recent_messages = conversation.get_recent_messages(6)
                for msg in recent_messages:
                    messages.append({
                        "role": msg.message_type,
                        "content": msg.content
                    })
            except AttributeError:
                # Fallback if conversation doesn't have get_recent_messages method
                recent_messages = ChatMessage.query.filter_by(
                    conversation_id=conversation.id
                ).order_by(ChatMessage.created_at.desc()).limit(6).all()
                recent_messages.reverse()  # Show oldest first
                for msg in recent_messages:
                    messages.append({
                        "role": msg.message_type,
                        "content": msg.content
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Search knowledge base for relevant context
            relevant_knowledge = self.search_knowledge_base(user_message)
            if relevant_knowledge:
                knowledge_context = "\n\nRelevant information from knowledge base:\n"
                for item in relevant_knowledge:
                    knowledge_context += f"- {item.topic}: {item.content[:200]}...\n"
                messages[-1]["content"] += knowledge_context
            
            # Generate response using Perplexity Sonar
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",  # Using correct Perplexity model
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False,
                "return_related_questions": False,
                "search_recency_filter": "month"
            }
            
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload, 
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                processing_time = time.time() - start_time
                
                # Extract usage information
                usage_info = {
                    'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                    'processing_time': processing_time,
                    'model': 'sonar-pro'
                }
                
                logger.info(f"Generated Perplexity response in {processing_time:.2f}s using {usage_info['tokens_used']} tokens")
                return ai_response, usage_info
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return "I'm sorry, I'm having trouble accessing current market data. Please try again in a moment.", {}
            
        except requests.exceptions.Timeout:
            logger.error("Perplexity API timeout")
            return "I'm sorry, the response took too long. Please try asking a simpler question.", {}
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm sorry, I encountered an error while processing your message. Please try again.", {}

    def _format_context_message(self, context: Dict) -> str:
        """Format user context into a system message"""
        context_parts = []
        
        if context.get('user_plan'):
            context_parts.append(f"User subscription plan: {context['user_plan']}")
            
        if context.get('portfolio_holdings'):
            context_parts.append(f"User has {len(context['portfolio_holdings'])} portfolio holdings")
            context_parts.append(f"Total portfolio value: ₹{context.get('total_portfolio_value', 0):,.2f}")
            
            # Add top 3 holdings
            holdings = context['portfolio_holdings'][:3]
            context_parts.append("Top holdings:")
            for holding in holdings:
                pnl_text = f"{holding['pnl_percentage']:+.1f}%" if holding['pnl_percentage'] else "N/A"
                context_parts.append(
                    f"- {holding['symbol']} ({holding['name']}): {holding['quantity']} units, "
                    f"P&L: {pnl_text}"
                )
        
        if context.get('recent_picks'):
            context_parts.append("Recent AI stock recommendations:")
            for pick in context['recent_picks']:
                context_parts.append(
                    f"- {pick['symbol']}: {pick['recommendation']} at ₹{pick['current_price']}"
                )
        
        return "User context:\n" + "\n".join(context_parts) if context_parts else ""

    def save_message(self, 
                    conversation: ChatConversation, 
                    message_type: str, 
                    content: str, 
                    usage_info: Optional[Dict] = None) -> ChatMessage:
        """Save message to database"""
        message = ChatMessage()
        message.conversation_id = conversation.id
        message.user_id = conversation.user_id
        message.message_type = message_type
        message.content = content
        if usage_info:
            message.tokens_used = usage_info.get('tokens_used')
            message.processing_time = usage_info.get('processing_time')
        
        db.session.add(message)
        
        # Update conversation timestamp and title
        conversation.updated_at = datetime.utcnow()
        if conversation.title == "New Investment Chat" and len(content) > 10:
            # Generate a title from the first message
            conversation.title = content[:50] + "..." if len(content) > 50 else content
            
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving message: {e}")
            raise
        return message

    def get_user_conversations(self, user_id: int, limit: int = 20) -> List[ChatConversation]:
        """Get user's recent conversations"""
        return ChatConversation.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(ChatConversation.updated_at.desc()).limit(limit).all()

    def initialize_knowledge_base(self):
        """Initialize knowledge base with basic investment concepts"""
        if ChatbotKnowledgeBase.query.count() > 0:
            return  # Already initialized
            
        knowledge_items = [
            {
                'category': 'investment_basics',
                'topic': 'What is a Stock?',
                'content': 'A stock represents ownership in a company. When you buy stocks, you become a shareholder and own a small piece of that business. Stocks are traded on exchanges like NSE and BSE in India.',
                'keywords': 'stock, share, equity, ownership, company, NSE, BSE',
                'difficulty_level': 'beginner'
            },
            {
                'category': 'investment_basics',
                'topic': 'Market Capitalization',
                'content': 'Market cap is the total value of a company\'s shares. It\'s calculated by multiplying share price by total number of shares. Large-cap stocks (>₹20,000 cr) are generally more stable than small-cap stocks (<₹5,000 cr).',
                'keywords': 'market cap, large cap, small cap, mid cap, valuation',
                'difficulty_level': 'beginner'
            },
            {
                'category': 'technical_analysis',
                'topic': 'P/E Ratio',
                'content': 'Price-to-Earnings ratio compares a company\'s stock price to its earnings per share. A lower P/E might indicate undervaluation, while higher P/E suggests growth expectations. Average P/E varies by industry.',
                'keywords': 'PE ratio, price earnings, valuation, earnings',
                'difficulty_level': 'intermediate'
            },
            {
                'category': 'trading_strategies',
                'topic': 'Systematic Investment Plan (SIP)',
                'content': 'SIP involves investing fixed amounts regularly regardless of market conditions. This strategy helps average out market volatility and build wealth over time through rupee cost averaging.',
                'keywords': 'SIP, systematic investment, rupee cost averaging, regular investment',
                'difficulty_level': 'beginner'
            },
            {
                'category': 'risk_management',
                'topic': 'Diversification',
                'content': 'Diversification means spreading investments across different assets, sectors, and companies to reduce risk. Don\'t put all eggs in one basket - invest across various sectors like IT, banking, pharma, FMCG.',
                'keywords': 'diversification, risk management, portfolio, sectors, asset allocation',
                'difficulty_level': 'intermediate'
            }
        ]
        
        for item_data in knowledge_items:
            knowledge_item = ChatbotKnowledgeBase(**item_data)
            db.session.add(knowledge_item)
            
        db.session.commit()
        logger.info(f"Initialized knowledge base with {len(knowledge_items)} items")

# Create global chatbot instance
chatbot = InvestmentChatbot()