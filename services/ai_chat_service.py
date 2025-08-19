"""
Clean AI Chat Service for Investment Advisor
Handles conversation management and message processing
"""
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from app import db
from models import ChatConversation, ChatMessage, User
from services.perplexity_api import PerplexityAPI

logger = logging.getLogger(__name__)

class AIChatService:
    """Clean service for AI investment chat functionality"""
    
    def __init__(self):
        self.perplexity = PerplexityAPI()
        logger.info("AI Chat Service initialized successfully")
    
    def get_or_create_conversation(self, user_id: int, conversation_id: Optional[str] = None) -> ChatConversation:
        """Get existing conversation or create new one"""
        try:
            if conversation_id:
                conversation = ChatConversation.query.filter_by(
                    session_id=conversation_id,
                    user_id=user_id
                ).first()
                
                if conversation:
                    return conversation
            
            # Create new conversation
            new_conversation = ChatConversation(
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                title="Investment Chat",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(new_conversation)
            db.session.commit()
            
            logger.info(f"Created new conversation {new_conversation.session_id} for user {user_id}")
            return new_conversation
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            db.session.rollback()
            raise
    
    def save_message(self, conversation: ChatConversation, message_type: str, content: str, usage_info: Dict = None) -> ChatMessage:
        """Save message to database"""
        try:
            message = ChatMessage(
                conversation_id=conversation.id,
                user_id=conversation.user_id,
                message_type=message_type,
                content=content,
                created_at=datetime.utcnow()
            )
            
            if usage_info and not usage_info.get('error'):
                message.tokens_used = usage_info.get('total_tokens')
                message.processing_time = usage_info.get('processing_time')
            
            db.session.add(message)
            
            # Update conversation
            conversation.updated_at = datetime.utcnow()
            if conversation.title == "Investment Chat" and message_type == 'user' and len(content) > 5:
                conversation.title = content[:40] + "..." if len(content) > 40 else content
            
            db.session.commit()
            logger.info(f"Saved {message_type} message for conversation {conversation.session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            db.session.rollback()
            raise
    
    def get_conversation_history(self, conversation: ChatConversation, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        try:
            messages = ChatMessage.query.filter_by(
                conversation_id=conversation.id
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
            
            history = []
            for msg in reversed(messages):
                history.append({
                    "role": "assistant" if msg.message_type == "assistant" else "user",
                    "content": msg.content
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def process_user_message(self, user_id: int, message: str, conversation_id: Optional[str] = None) -> Tuple[str, str, Dict]:
        """
        Process user message and generate AI response
        Returns: (ai_response, conversation_id, usage_info)
        """
        try:
            # Get or create conversation
            conversation = self.get_or_create_conversation(user_id, conversation_id)
            
            # Save user message
            self.save_message(conversation, 'user', message)
            
            # Get conversation history for context
            history = self.get_conversation_history(conversation)
            
            # Generate AI response
            ai_response, usage_info = self.perplexity.get_investment_advice(message, history)
            
            # Save AI response
            self.save_message(conversation, 'assistant', ai_response, usage_info)
            
            return ai_response, conversation.session_id, usage_info
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            error_response = "I encountered an error while processing your message. Please try again."
            return error_response, conversation_id or str(uuid.uuid4()), {"error": True}
    
    def get_user_conversations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get user's recent conversations"""
        try:
            conversations = ChatConversation.query.filter_by(
                user_id=user_id
            ).order_by(ChatConversation.updated_at.desc()).limit(limit).all()
            
            result = []
            for conv in conversations:
                result.append({
                    'id': conv.session_id,
                    'title': conv.title,
                    'updated_at': conv.updated_at.isoformat(),
                    'message_count': ChatMessage.query.filter_by(conversation_id=conv.id).count()
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
    
    def validate_service(self) -> bool:
        """Validate that the service is working properly"""
        try:
            return self.perplexity.validate_connection()
        except Exception:
            return False