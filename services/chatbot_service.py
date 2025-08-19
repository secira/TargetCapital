import os
import json
import time
import uuid
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from openai import OpenAI
from models import (ChatConversation, ChatMessage, ChatbotKnowledgeBase, 
                   Portfolio, User, AIStockPick)
from app import db

logger = logging.getLogger(__name__)

class InvestmentChatbot:
    """AI-Powered Investment Explanation Chatbot using OpenAI GPT-4"""
    
    def __init__(self):
        self.openai_client = None
        self._initialize_openai()
        self.system_prompt = self._get_system_prompt()
        
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            return
            
        try:
            self.openai_client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI investment chatbot"""
        return """You are an AI Investment Advisor and Educational Chatbot for tCapital, a leading AI-powered trading platform in India.

Your role is to:
1. Explain investment concepts in simple, understandable language
2. Help users understand their portfolios and market data
3. Provide educational insights about stocks, trading, and financial markets
4. Answer questions about Indian stock markets, NSE, BSE, and investment strategies
5. Use context from user's portfolio when available to give personalized advice

Guidelines:
- Always maintain a professional, helpful, and educational tone
- Explain complex financial terms in simple language
- Use examples and analogies when helpful
- Focus on education rather than specific buy/sell recommendations
- Be transparent about risks and market volatility
- Reference Indian market context (NSE, BSE, rupees, etc.)
- Never guarantee returns or make promises about market performance
- Encourage users to do their own research and consult financial advisors for major decisions

Response format:
- Keep responses concise but informative
- Use bullet points for lists when appropriate
- Include relevant examples when explaining concepts
- End with a related question to keep the conversation engaging

Remember: You're an educational tool to help users make informed decisions, not a replacement for professional financial advice."""

    def get_or_create_conversation(self, user_id: int, session_id: str = None) -> ChatConversation:
        """Get existing conversation or create new one"""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        conversation = ChatConversation.query.filter_by(
            user_id=user_id, 
            session_id=session_id,
            is_active=True
        ).first()
        
        if not conversation:
            conversation = ChatConversation(
                user_id=user_id,
                session_id=session_id,
                title="New Investment Chat"
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
            # Get user info
            user = User.query.get(user_id)
            if user:
                context['user_plan'] = user.pricing_plan.value if user.pricing_plan else 'FREE'
                
            # Get portfolio holdings
            portfolio_items = Portfolio.query.filter_by(user_id=user_id).limit(10).all()
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

    def generate_response(self, 
                         user_message: str, 
                         conversation: ChatConversation,
                         user_context: Dict = None) -> Tuple[str, Dict]:
        """Generate AI response using OpenAI GPT-4"""
        if not self.openai_client:
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
            
            # Add recent conversation history (last 10 messages)
            recent_messages = conversation.get_recent_messages(10)
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
            
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using latest GPT-4o model
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )
            
            ai_response = response.choices[0].message.content
            processing_time = time.time() - start_time
            
            # Extract usage information
            usage_info = {
                'tokens_used': response.usage.total_tokens,
                'processing_time': processing_time,
                'model': 'gpt-4o'
            }
            
            logger.info(f"Generated response in {processing_time:.2f}s using {usage_info['tokens_used']} tokens")
            
            return ai_response, usage_info
            
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
                    usage_info: Dict = None) -> ChatMessage:
        """Save message to database"""
        message = ChatMessage(
            conversation_id=conversation.id,
            user_id=conversation.user_id,
            message_type=message_type,
            content=content,
            tokens_used=usage_info.get('tokens_used') if usage_info else None,
            processing_time=usage_info.get('processing_time') if usage_info else None
        )
        
        db.session.add(message)
        
        # Update conversation timestamp and title
        conversation.updated_at = datetime.utcnow()
        if conversation.title == "New Investment Chat" and len(content) > 10:
            # Generate a title from the first message
            conversation.title = content[:50] + "..." if len(content) > 50 else content
            
        db.session.commit()
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