"""
Research Assistant Service with RAG (Retrieval-Augmented Generation)
Combines vector search, user context, and LLM responses for intelligent stock research
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import openai
import requests
from sqlalchemy import text
from models import (ResearchConversation, ResearchMessage, VectorDocument, 
                   SourceCitation, SignalPerformance, Portfolio, User,
                   BrokerAccount)
from app import db

logger = logging.getLogger(__name__)

class ResearchAssistantService:
    """RAG-powered research assistant for intelligent stock research"""
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY')
        self.perplexity_base_url = "https://api.perplexity.ai/chat/completions"
        
        # Initialize OpenAI for embeddings
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            logger.info("OpenAI API initialized for embeddings")
        else:
            logger.warning("OPENAI_API_KEY not found - embeddings will be limited")
            
        if not self.perplexity_api_key:
            logger.warning("PERPLEXITY_API_KEY not found - web research will be limited")
            
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for Research Assistant"""
        return """You are a Research Assistant for Target Capital, an educational platform focused on the Indian stock market.

Your core capabilities:
1. **Stock Research**: Analyze Indian stocks (NSE/BSE) with real-time data and historical context
2. **Portfolio Context**: Provide personalized advice based on user's current holdings and risk profile
3. **Market Intelligence**: Track sector trends, news, earnings, and regulatory changes
4. **Educational**: Explain complex concepts in simple language for Indian investors
5. **Compliance**: Always include proper disclaimers and cite sources

Research Process:
- Access user's portfolio context for personalized analysis
- Search knowledge base for relevant historical data and research
- Use real-time web data for current market conditions
- Provide evidence-based recommendations with cited sources
- Suggest actionable next steps with pre-filled trade options

Response Format:
- **Analysis**: Data-driven insights with numbers and percentages
- **Sources**: Always cite specific sources for claims
- **Risk Assessment**: Clear risk levels (Low/Medium/High)
- **Next Steps**: Actionable recommendations
- **Disclaimer**: "This information is for educational purposes only. Investors and traders should consult a qualified financial advisor before making any investment decisions."

Indian Market Focus:
- Use ₹ for currency, NSE/BSE for exchanges
- Reference SEBI regulations and Indian tax implications
- Consider Indian market hours and settlement cycles
- Track Indian macroeconomic indicators (GDP, inflation, RBI policy)

Remember: This is educational research - not guaranteed investment advice. Users must consult their financial advisors."""

    def create_or_get_conversation(self, user_id: int, conversation_id: Optional[int] = None) -> ResearchConversation:
        """Create new conversation or retrieve existing one"""
        if conversation_id:
            conversation = ResearchConversation.query.filter_by(
                id=conversation_id,
                user_id=user_id
            ).first()
            if conversation:
                return conversation
        
        # Create new conversation
        conversation = ResearchConversation()
        conversation.user_id = user_id
        conversation.title = "New Research Session"
        db.session.add(conversation)
        db.session.commit()
        logger.info(f"Created new research conversation {conversation.id} for user {user_id}")
        return conversation
    
    def get_user_context(self, user_id: int) -> Dict:
        """Gather comprehensive user context for personalized research"""
        context = {
            'portfolio': {
                'holdings': [],
                'total_value': 0,
                'sectors': {},
                'top_performers': [],
                'underperformers': []
            },
            'brokers': {
                'connected': [],
                'count': 0
            },
            'user_profile': {
                'plan': 'FREE',
                'risk_tolerance': 'MODERATE'
            }
        }
        
        try:
            # Get user info
            user = User.query.get(user_id)
            if user:
                context['user_profile']['plan'] = user.pricing_plan.value if user.pricing_plan else 'FREE'
            
            # Get portfolio holdings
            portfolio_items = Portfolio.query.filter_by(user_id=user_id).all()
            total_value = 0
            
            for item in portfolio_items:
                holding_data = {
                    'symbol': item.ticker_symbol,
                    'name': item.stock_name,
                    'quantity': item.quantity,
                    'current_value': float(item.current_value) if item.current_value else 0,
                    'pnl_percentage': float(item.pnl_percentage) if item.pnl_percentage else 0,
                    'sector': item.sector
                }
                context['portfolio']['holdings'].append(holding_data)
                total_value += holding_data['current_value']
                
                # Track sectors
                sector = item.sector or 'Other'
                if sector not in context['portfolio']['sectors']:
                    context['portfolio']['sectors'][sector] = 0
                context['portfolio']['sectors'][sector] += holding_data['current_value']
            
            context['portfolio']['total_value'] = total_value
            
            # Get connected brokers
            brokers = BrokerAccount.query.filter_by(
                user_id=user_id,
                connection_status='connected'
            ).all()
            context['brokers']['count'] = len(brokers)
            context['brokers']['connected'] = [b.broker_name for b in brokers]
            
        except Exception as e:
            logger.error(f"Error gathering user context: {str(e)}")
        
        return context
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using OpenAI"""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not available for embeddings")
            return []
        
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-small",  # Cost-effective model
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []
    
    def vector_search(self, query_embedding: List[float], limit: int = 5, 
                     symbol: Optional[str] = None) -> List[Dict]:
        """Perform vector similarity search using pgvector"""
        if not query_embedding:
            return []
        
        try:
            from sqlalchemy import text
            
            # Convert embedding to PostgreSQL vector format
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Build query - use proper parameter binding
            if symbol:
                query = text("""
                    SELECT id, title, content, symbol, sector, category, source_url,
                           published_date, document_type,
                           1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                    FROM vector_documents
                    WHERE embedding IS NOT NULL
                    AND symbol = :symbol
                    ORDER BY embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :limit
                """)
                params = {
                    'query_embedding': embedding_str,
                    'symbol': symbol,
                    'limit': limit
                }
            else:
                query = text("""
                    SELECT id, title, content, symbol, sector, category, source_url,
                           published_date, document_type,
                           1 - (embedding <=> CAST(:query_embedding AS vector)) as similarity
                    FROM vector_documents
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> CAST(:query_embedding AS vector)
                    LIMIT :limit
                """)
                params = {
                    'query_embedding': embedding_str,
                    'limit': limit
                }
            
            result = db.session.execute(query, params)
            
            documents = []
            for row in result:
                documents.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'symbol': row[3],
                    'sector': row[4],
                    'category': row[5],
                    'source_url': row[6],
                    'published_date': row[7],
                    'document_type': row[8],
                    'similarity': float(row[9])
                })
            
            logger.info(f"Vector search found {len(documents)} relevant documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error in vector search: {str(e)}")
            return []
    
    def research_with_perplexity(self, query: str, context: Dict) -> Tuple[str, List[Dict]]:
        """Perform research using Perplexity with user context"""
        if not self.perplexity_api_key:
            return ("Perplexity API not available. Please configure PERPLEXITY_API_KEY.", [])
        
        try:
            # Build context-aware prompt
            context_str = self._build_context_string(context)
            full_prompt = f"""{context_str}

User Research Query: {query}

Provide comprehensive research with:
1. Current market data and analysis
2. Key factors and trends
3. Risk assessment
4. Specific recommendations
5. Cited sources"""
            
            headers = {
                'Authorization': f'Bearer {self.perplexity_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'sonar-pro',  # Perplexity Pro model for accurate real-time data
                'messages': [
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': full_prompt}
                ],
                'temperature': 0.2,
                'max_tokens': 2000,  # Increased for comprehensive responses
                'search_recency_filter': 'day'  # Focus on most recent data
            }
            
            # Retry logic with increased timeout
            max_retries = 2
            retry_count = 0
            last_error = None
            
            while retry_count <= max_retries:
                try:
                    response = requests.post(
                        self.perplexity_base_url,
                        headers=headers,
                        json=payload,
                        timeout=120  # Increased from 30 to 120 seconds
                    )
                    break  # Success, exit retry loop
                except requests.exceptions.Timeout:
                    retry_count += 1
                    last_error = "API request timed out"
                    logger.warning(f"Perplexity API timeout (attempt {retry_count}/{max_retries + 1})")
                    if retry_count > max_retries:
                        raise
                    continue
            
            if last_error and retry_count > max_retries:
                return (f"Research temporarily unavailable - API timeout. Please try again.", [])
            
            # Log error details if request fails
            if response.status_code != 200:
                logger.error(f"Perplexity API error {response.status_code}: {response.text}")
                response.raise_for_status()
            
            data = response.json()
            answer = data['choices'][0]['message']['content']
            
            # Extract citations from response
            citations = []
            # Perplexity includes citations inline in the response text
            # We'll parse URLs from the response as citations
            import re
            urls = re.findall(r'https?://[^\s\)]+', answer)
            for url in urls[:5]:  # Limit to top 5 URLs
                citations.append({
                    'source_type': 'web',
                    'source_title': 'Web Source',
                    'source_url': url,
                    'relevance_score': None
                })
            
            logger.info(f"Perplexity research completed with {len(citations)} citations")
            return answer, citations
            
        except Exception as e:
            logger.error(f"Perplexity research error: {str(e)}")
            return (f"Research error: {str(e)}", [])
    
    def _build_context_string(self, context: Dict) -> str:
        """Build context string from user data"""
        parts = ["User Context:"]
        
        # Portfolio context
        if context['portfolio']['holdings']:
            parts.append(f"\nPortfolio Value: ₹{context['portfolio']['total_value']:,.2f}")
            parts.append(f"Holdings: {len(context['portfolio']['holdings'])} stocks")
            if context['portfolio']['sectors']:
                top_sector = max(context['portfolio']['sectors'].items(), key=lambda x: x[1])
                parts.append(f"Top Sector: {top_sector[0]} (₹{top_sector[1]:,.2f})")
        
        # Broker context
        if context['brokers']['connected']:
            parts.append(f"\nConnected Brokers: {', '.join(context['brokers']['connected'])}")
        
        # User profile
        parts.append(f"\nUser Plan: {context['user_profile']['plan']}")
        
        return '\n'.join(parts)
    
    def save_research_interaction(self, conversation_id: int, user_query: str, 
                                  assistant_response: str, context: Dict,
                                  citations: List[Dict]) -> ResearchMessage:
        """Save research interaction to database"""
        try:
            # Save user message
            user_message = ResearchMessage()
            user_message.conversation_id = conversation_id
            user_message.role = 'user'
            user_message.content = user_query
            db.session.add(user_message)
            db.session.flush()
            
            # Save assistant message
            assistant_message = ResearchMessage()
            assistant_message.conversation_id = conversation_id
            assistant_message.role = 'assistant'
            assistant_message.content = assistant_response
            assistant_message.portfolio_context = context.get('portfolio', {})
            assistant_message.market_context = context.get('market', {})
            db.session.add(assistant_message)
            db.session.flush()
            
            # Save citations
            for cite in citations:
                citation = SourceCitation()
                citation.message_id = assistant_message.id
                citation.source_type = cite.get('source_type', 'web')
                citation.source_title = cite.get('source_title', 'Unknown Source')
                citation.source_url = cite.get('source_url')
                citation.relevance_score = cite.get('relevance_score')
                if cite.get('vector_doc_id'):
                    citation.vector_doc_id = cite['vector_doc_id']
                db.session.add(citation)
            
            db.session.commit()
            logger.info(f"Saved research interaction with {len(citations)} citations")
            return assistant_message
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving research interaction: {str(e)}")
            raise
    
    def perform_research(self, user_id: int, query: str, 
                        conversation_id: Optional[int] = None) -> Dict:
        """Main research method combining RAG and Perplexity"""
        try:
            # Get or create conversation
            conversation = self.create_or_get_conversation(user_id, conversation_id)
            
            # Gather user context
            user_context = self.get_user_context(user_id)
            
            # Generate embedding for query
            query_embedding = self.generate_embedding(query)
            
            # Perform vector search for relevant documents
            relevant_docs = self.vector_search(query_embedding, limit=5)
            
            # Add retrieved documents to context
            if relevant_docs:
                user_context['retrieved_documents'] = relevant_docs
            
            # Perform research with Perplexity
            response, citations = self.research_with_perplexity(query, user_context)
            
            # Add citations from vector search
            for doc in relevant_docs[:3]:  # Top 3 relevant docs
                citations.append({
                    'source_type': 'document',
                    'source_title': doc['title'],
                    'source_url': doc.get('source_url'),
                    'relevance_score': doc.get('similarity'),
                    'vector_doc_id': doc['id']
                })
            
            # Save interaction
            message = self.save_research_interaction(
                conversation.id,
                query,
                response,
                user_context,
                citations
            )
            
            # Update conversation title if it's the first message
            if conversation.title == "New Research Session":
                # Use first few words of query as title
                title = ' '.join(query.split()[:6])
                if len(query.split()) > 6:
                    title += '...'
                conversation.title = title
                db.session.commit()
            
            return {
                'success': True,
                'conversation_id': conversation.id,
                'message_id': message.id,
                'response': response,
                'citations': citations,
                'context': {
                    'portfolio_value': user_context['portfolio']['total_value'],
                    'holdings_count': len(user_context['portfolio']['holdings']),
                    'brokers_connected': user_context['brokers']['count']
                }
            }
            
        except Exception as e:
            db.session.rollback()  # Rollback any pending transactions
            logger.error(f"Research error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': "An error occurred during research. Please try again."
            }
    
    def get_conversation_history(self, conversation_id: int, limit: int = 50) -> List[Dict]:
        """Get conversation history"""
        try:
            messages = ResearchMessage.query.filter_by(
                conversation_id=conversation_id
            ).order_by(ResearchMessage.created_at.asc()).limit(limit).all()
            
            history = []
            for msg in messages:
                message_data = {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat(),
                    'citations': []
                }
                
                if msg.role == 'assistant':
                    citations = SourceCitation.query.filter_by(message_id=msg.id).all()
                    message_data['citations'] = [{
                        'title': c.source_title,
                        'url': c.source_url,
                        'type': c.source_type
                    } for c in citations]
                
                history.append(message_data)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def get_user_conversations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's recent conversations"""
        try:
            conversations = ResearchConversation.query.filter_by(
                user_id=user_id,
                is_archived=False
            ).order_by(ResearchConversation.updated_at.desc()).limit(limit).all()
            
            result = []
            for conv in conversations:
                # Count messages
                message_count = ResearchMessage.query.filter_by(
                    conversation_id=conv.id
                ).count()
                
                result.append({
                    'id': conv.id,
                    'title': conv.title,
                    'message_count': message_count,
                    'created_at': conv.created_at.isoformat(),
                    'updated_at': conv.updated_at.isoformat()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            return []
