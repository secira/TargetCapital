"""
Vector Service for RAG operations
Handles embeddings, similarity search, and knowledge retrieval
"""

import os
import logging
import numpy as np
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class VectorService:
    """
    Service for vector operations in RAG system
    - Generate embeddings using OpenAI
    - Store embeddings in database
    - Perform similarity search
    - Cache results for performance
    """
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self._setup_openai()
    
    def _setup_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {str(e)}")
            self.openai_client = None
    
    def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> Optional[List[float]]:
        """
        Generate embedding for a piece of text
        
        Args:
            text: Text to embed
            model: OpenAI embedding model (default: ada-002, 1536 dimensions)
            
        Returns:
            List of floats (embedding vector) or None if error
        """
        if not self.openai_client:
            logger.error("OpenAI not initialized")
            return None
        
        try:
            # Clean text
            text = text.strip()[:8000]  # Limit to 8000 chars for safety
            
            if not text:
                return None
            
            response = self.openai_client.embeddings.create(
                model=model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str], 
                                  model: str = "text-embedding-ada-002") -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of texts to embed
            model: OpenAI embedding model
            
        Returns:
            List of embeddings (same length as input)
        """
        if not self.openai_client:
            return [None] * len(texts)
        
        try:
            # Clean texts
            cleaned_texts = [text.strip()[:8000] for text in texts if text.strip()]
            
            if not cleaned_texts:
                return [None] * len(texts)
            
            # Batch API call
            response = self.openai_client.embeddings.create(
                model=model,
                input=cleaned_texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            return [None] * len(texts)
    
    def cosine_similarity_search(self, query_embedding: List[float],
                                 candidate_embeddings: List[List[float]],
                                 top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Find most similar embeddings using cosine similarity
        
        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors to search
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples sorted by similarity
        """
        try:
            # Convert to numpy arrays
            query_vec = np.array(query_embedding).reshape(1, -1)
            candidate_vecs = np.array(candidate_embeddings)
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vec, candidate_vecs)[0]
            
            # Get top K indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            # Return (index, score) tuples
            results = [(int(idx), float(similarities[idx])) for idx in top_indices]
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def store_document_chunks(self, user_id: int, document_type: str,
                             chunks: List[str], asset_class: Optional[str] = None,
                             source: Optional[str] = None, metadata: Optional[Dict] = None) -> List[int]:
        """
        Store document chunks with embeddings in database
        
        Args:
            user_id: User ID
            document_type: Type of document (broker_statement, research_report, etc.)
            chunks: List of text chunks
            asset_class: Asset class if applicable
            source: Source name (Zerodha, HDFC, etc.)
            metadata: Additional metadata
            
        Returns:
            List of created chunk IDs
        """
        from app import db
        from models_vector import PortfolioDocumentChunk
        
        try:
            # Generate embeddings for all chunks
            embeddings = self.generate_embeddings_batch(chunks)
            
            chunk_ids = []
            
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                if not chunk_text.strip():
                    continue
                
                # Extract tags from chunk (simple keyword extraction)
                tags = self._extract_tags(chunk_text, asset_class)
                
                # Create chunk record
                chunk = PortfolioDocumentChunk(
                    user_id=user_id,
                    document_type=document_type,
                    asset_class=asset_class,
                    source=source,
                    chunk_text=chunk_text,
                    chunk_index=idx,
                    chunk_size=len(chunk_text),
                    embedding=embedding,  # Store as JSON
                    document_metadata=metadata or {},
                    tags=tags,
                    document_date=datetime.now().date()
                )
                
                db.session.add(chunk)
                db.session.flush()  # Get ID
                chunk_ids.append(chunk.id)
            
            db.session.commit()
            logger.info(f"Stored {len(chunk_ids)} chunks for user {user_id}")
            
            return chunk_ids
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing chunks: {str(e)}")
            return []
    
    def search_knowledge_base(self, user_id: int, query: str,
                             asset_class: Optional[str] = None,
                             knowledge_type: Optional[str] = None,
                             top_k: int = 5) -> List[Dict]:
        """
        Search user's knowledge base using vector similarity
        
        Args:
            user_id: User ID
            query: Search query
            asset_class: Filter by asset class
            knowledge_type: Filter by knowledge type
            top_k: Number of results
            
        Returns:
            List of knowledge base items with similarity scores
        """
        from app import db
        from models_vector import PortfolioKnowledgeBase
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Build query
            kb_query = PortfolioKnowledgeBase.query.filter_by(user_id=user_id)
            
            if asset_class:
                kb_query = kb_query.filter_by(asset_class=asset_class)
            if knowledge_type:
                kb_query = kb_query.filter_by(knowledge_type=knowledge_type)
            
            # Get all matching records
            knowledge_items = kb_query.all()
            
            if not knowledge_items:
                return []
            
            # Extract embeddings
            embeddings = [item.embedding for item in knowledge_items if item.embedding]
            
            if not embeddings:
                return []
            
            # Perform similarity search
            similar_indices = self.cosine_similarity_search(
                query_embedding,
                embeddings,
                top_k=min(top_k, len(embeddings))
            )
            
            # Build results
            results = []
            for idx, score in similar_indices:
                item = knowledge_items[idx]
                results.append({
                    'id': item.id,
                    'title': item.title,
                    'content': item.content,
                    'knowledge_type': item.knowledge_type,
                    'asset_class': item.asset_class,
                    'asset_symbol': item.asset_symbol,
                    'structured_data': item.structured_data,
                    'similarity_score': score,
                    'relevant_date': item.relevant_date.isoformat() if item.relevant_date else None,
                    'created_at': item.created_at.isoformat() if item.created_at else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    def search_document_chunks(self, user_id: int, query: str,
                              document_type: Optional[str] = None,
                              asset_class: Optional[str] = None,
                              top_k: int = 5) -> List[Dict]:
        """
        Search document chunks using vector similarity
        
        Args:
            user_id: User ID
            query: Search query
            document_type: Filter by document type
            asset_class: Filter by asset class
            top_k: Number of results
            
        Returns:
            List of matching chunks with similarity scores
        """
        from app import db
        from models_vector import PortfolioDocumentChunk
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Build query
            chunk_query = PortfolioDocumentChunk.query.filter_by(user_id=user_id)
            
            if document_type:
                chunk_query = chunk_query.filter_by(document_type=document_type)
            if asset_class:
                chunk_query = chunk_query.filter_by(asset_class=asset_class)
            
            # Get all matching chunks
            chunks = chunk_query.all()
            
            if not chunks:
                return []
            
            # Extract embeddings
            embeddings = [chunk.embedding for chunk in chunks if chunk.embedding]
            
            if not embeddings:
                return []
            
            # Perform similarity search
            similar_indices = self.cosine_similarity_search(
                query_embedding,
                embeddings,
                top_k=min(top_k, len(embeddings))
            )
            
            # Build results
            results = []
            for idx, score in similar_indices:
                chunk = chunks[idx]
                results.append({
                    'id': chunk.id,
                    'chunk_text': chunk.chunk_text,
                    'document_type': chunk.document_type,
                    'asset_class': chunk.asset_class,
                    'source': chunk.source,
                    'tags': chunk.tags,
                    'document_metadata': chunk.document_metadata,
                    'similarity_score': score,
                    'created_at': chunk.created_at.isoformat() if chunk.created_at else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching chunks: {str(e)}")
            return []
    
    def create_knowledge_item(self, user_id: int, knowledge_type: str,
                             title: str, content: str,
                             asset_class: Optional[str] = None,
                             asset_symbol: Optional[str] = None,
                             structured_data: Optional[Dict] = None,
                             source_chunk_ids: Optional[List[int]] = None) -> Optional[int]:
        """
        Create a knowledge base item with embedding
        
        Returns:
            Knowledge item ID or None if error
        """
        from app import db
        from models_vector import PortfolioKnowledgeBase
        
        try:
            # Generate embedding for title + content
            embedding_text = f"{title} {content}"
            embedding = self.generate_embedding(embedding_text)
            
            # Extract tags
            tags = self._extract_tags(f"{title} {content}", asset_class)
            
            # Create knowledge item
            knowledge = PortfolioKnowledgeBase(
                user_id=user_id,
                knowledge_type=knowledge_type,
                asset_class=asset_class,
                asset_symbol=asset_symbol,
                title=title,
                content=content,
                structured_data=structured_data or {},
                source_chunk_ids=source_chunk_ids or [],
                embedding=embedding,
                tags=tags,
                relevant_date=datetime.now().date()
            )
            
            db.session.add(knowledge)
            db.session.commit()
            
            logger.info(f"Created knowledge item {knowledge.id} for user {user_id}")
            return knowledge.id
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating knowledge item: {str(e)}")
            return None
    
    def _extract_tags(self, text: str, asset_class: Optional[str] = None) -> List[str]:
        """
        Extract relevant tags from text (simple keyword extraction)
        """
        tags = []
        
        # Add asset class
        if asset_class:
            tags.append(asset_class)
        
        # Common stock symbols (simple pattern)
        import re
        stock_patterns = r'\b([A-Z]{2,10})\b'
        stocks = re.findall(stock_patterns, text)
        tags.extend(stocks[:5])  # Limit to 5
        
        # Common financial keywords
        keywords = ['holding', 'equity', 'mutual fund', 'bond', 'FD', 'deposit',
                   'transaction', 'buy', 'sell', 'profit', 'loss', 'dividend']
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                tags.append(keyword)
        
        return list(set(tags))[:10]  # Unique, max 10 tags
    
    def get_query_hash(self, query: str) -> str:
        """Generate hash for query caching"""
        return hashlib.sha256(query.encode()).hexdigest()


# Singleton instance
_vector_service = None

def get_vector_service() -> VectorService:
    """Get or create vector service instance"""
    global _vector_service
    if _vector_service is None:
        _vector_service = VectorService()
    return _vector_service
