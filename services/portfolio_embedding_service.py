"""
Portfolio Asset Embedding Service
Automatically generates and stores vector embeddings for all portfolio assets
Enables semantic search and intelligent AI analysis over user's holdings
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from app import db
from models_vector import PortfolioAssetEmbedding
from services.vector_service import VectorService

logger = logging.getLogger(__name__)


class PortfolioEmbeddingService:
    """
    Service for generating and managing portfolio asset embeddings
    """
    
    def __init__(self):
        self.vector_service = VectorService()
        self.logger = logging.getLogger(__name__)
    
    def embed_broker_holding(self, user_id: int, holding: Any, broker_account_id: int) -> Optional[int]:
        """
        Create/update embedding for a broker holding
        
        Args:
            user_id: User ID
            holding: BrokerHolding object
            broker_account_id: Broker account ID
            
        Returns:
            PortfolioAssetEmbedding ID or None
        """
        try:
            # Build rich description
            description = self._build_broker_holding_description(holding)
            
            # Generate embedding
            embedding = self.vector_service.generate_embedding(description)
            
            if not embedding:
                logger.error(f"Failed to generate embedding for broker holding {holding.id}")
                return None
            
            # Check if embedding already exists
            existing = PortfolioAssetEmbedding.query.filter_by(
                user_id=user_id,
                source_table='broker_holdings',
                source_record_id=holding.id
            ).first()
            
            if existing:
                # Update existing
                existing.asset_description = description
                existing.embedding = embedding
                existing.quantity = holding.available_quantity
                existing.current_value = holding.total_value
                existing.purchase_value = holding.investment_value
                existing.current_price = holding.current_price
                existing.updated_at = datetime.utcnow()
                existing.last_synced = datetime.utcnow()
                existing.is_active = True
                db.session.commit()
                self.logger.info(f"Updated embedding for broker holding {holding.symbol}")
                return existing.id
            else:
                # Create new
                asset_embedding = PortfolioAssetEmbedding(
                    user_id=user_id,
                    asset_type='equities',
                    asset_symbol=holding.symbol,
                    asset_name=holding.company_name or holding.symbol,
                    asset_category='equity',
                    source_table='broker_holdings',
                    source_record_id=holding.id,
                    broker_account_id=broker_account_id,
                    asset_description=description,
                    quantity=holding.available_quantity,
                    current_value=holding.total_value,
                    purchase_value=holding.investment_value,
                    current_price=holding.current_price,
                    embedding=embedding,
                    asset_metadata={
                        'exchange': holding.exchange,
                        'isin': holding.isin,
                        'trading_symbol': holding.trading_symbol,
                        'avg_cost_price': holding.avg_cost_price,
                        'pnl': holding.pnl,
                        'pnl_percentage': holding.pnl_percentage
                    },
                    tags=self._extract_tags_from_holding(holding),
                    is_active=True
                )
                
                db.session.add(asset_embedding)
                db.session.commit()
                self.logger.info(f"Created embedding for broker holding {holding.symbol}")
                return asset_embedding.id
                
        except Exception as e:
            logger.error(f"Error embedding broker holding: {str(e)}")
            db.session.rollback()
            return None
    
    def embed_manual_equity(self, user_id: int, equity: Any) -> Optional[int]:
        """
        Create/update embedding for manual equity holding
        """
        try:
            description = self._build_manual_equity_description(equity)
            embedding = self.vector_service.generate_embedding(description)
            
            if not embedding:
                return None
            
            existing = PortfolioAssetEmbedding.query.filter_by(
                user_id=user_id,
                source_table='manual_equity_holdings',
                source_record_id=equity.id
            ).first()
            
            if existing:
                existing.asset_description = description
                existing.embedding = embedding
                existing.quantity = equity.quantity
                existing.current_value = equity.current_value
                existing.purchase_value = equity.total_investment
                existing.current_price = equity.current_price
                existing.updated_at = datetime.utcnow()
                existing.is_active = equity.is_active
                db.session.commit()
                return existing.id
            else:
                asset_embedding = PortfolioAssetEmbedding(
                    user_id=user_id,
                    asset_type='equities',
                    asset_symbol=equity.symbol,
                    asset_name=equity.company_name,
                    asset_category='equity',
                    source_table='manual_equity_holdings',
                    source_record_id=equity.id,
                    broker_account_id=equity.broker_account_id,
                    asset_description=description,
                    quantity=equity.quantity,
                    current_value=equity.current_value,
                    purchase_value=equity.total_investment,
                    current_price=equity.current_price,
                    embedding=embedding,
                    asset_metadata={
                        'exchange': equity.exchange,
                        'isin': equity.isin,
                        'purchase_price': equity.purchase_price,
                        'unrealized_pnl': equity.unrealized_pnl,
                        'unrealized_pnl_percentage': equity.unrealized_pnl_percentage,
                        'portfolio_name': equity.portfolio_name,
                        'asset_class': equity.asset_class
                    },
                    tags=['equity', 'manual-entry'],
                    is_active=equity.is_active
                )
                db.session.add(asset_embedding)
                db.session.commit()
                self.logger.info(f"Created embedding for manual equity {equity.symbol}")
                return asset_embedding.id
                
        except Exception as e:
            logger.error(f"Error embedding manual equity: {str(e)}")
            db.session.rollback()
            return None
    
    def embed_mutual_fund(self, user_id: int, mf: Any) -> Optional[int]:
        """
        Create/update embedding for mutual fund holding
        """
        try:
            description = self._build_mutual_fund_description(mf)
            embedding = self.vector_service.generate_embedding(description)
            
            if not embedding:
                return None
            
            existing = PortfolioAssetEmbedding.query.filter_by(
                user_id=user_id,
                source_table='manual_mutual_fund_holdings',
                source_record_id=mf.id
            ).first()
            
            category = self._get_mf_category(mf.fund_category)
            
            if existing:
                existing.asset_description = description
                existing.embedding = embedding
                existing.quantity = mf.units
                existing.current_value = mf.current_value
                existing.purchase_value = mf.total_investment
                existing.updated_at = datetime.utcnow()
                db.session.commit()
                return existing.id
            else:
                asset_embedding = PortfolioAssetEmbedding(
                    user_id=user_id,
                    asset_type='mutual_funds',
                    asset_symbol=mf.scheme_name,
                    asset_name=mf.scheme_name,
                    asset_category=category,
                    source_table='manual_mutual_fund_holdings',
                    source_record_id=mf.id,
                    broker_account_id=mf.broker_account_id,
                    asset_description=description,
                    quantity=mf.units,
                    current_value=mf.current_value,
                    purchase_value=mf.total_investment,
                    embedding=embedding,
                    asset_metadata={
                        'fund_house': mf.fund_house,
                        'isin': mf.isin,
                        'nav': mf.nav,
                        'fund_category': mf.fund_category,
                        'fund_type': mf.fund_type,
                        'sip_active': mf.sip_active
                    },
                    tags=self._extract_tags_from_mf(mf),
                    is_active=True
                )
                db.session.add(asset_embedding)
                db.session.commit()
                return asset_embedding.id
                
        except Exception as e:
            logger.error(f"Error embedding mutual fund: {str(e)}")
            db.session.rollback()
            return None
    
    def embed_fixed_deposit(self, user_id: int, fd: Any) -> Optional[int]:
        """
        Create/update embedding for fixed deposit
        """
        try:
            description = self._build_fd_description(fd)
            embedding = self.vector_service.generate_embedding(description)
            
            if not embedding:
                return None
            
            existing = PortfolioAssetEmbedding.query.filter_by(
                user_id=user_id,
                source_table='manual_fixed_deposit_holdings',
                source_record_id=fd.id
            ).first()
            
            if existing:
                existing.asset_description = description
                existing.embedding = embedding
                existing.current_value = fd.current_value
                existing.purchase_value = fd.principal_amount
                existing.updated_at = datetime.utcnow()
                db.session.commit()
                return existing.id
            else:
                asset_embedding = PortfolioAssetEmbedding(
                    user_id=user_id,
                    asset_type='fixed_deposits',
                    asset_symbol=fd.bank_name,
                    asset_name=f"{fd.bank_name} Fixed Deposit",
                    asset_category='debt',
                    source_table='manual_fixed_deposit_holdings',
                    source_record_id=fd.id,
                    asset_description=description,
                    current_value=fd.current_value,
                    purchase_value=fd.principal_amount,
                    embedding=embedding,
                    asset_metadata={
                        'bank_name': fd.bank_name,
                        'interest_rate': fd.interest_rate,
                        'tenure_months': fd.tenure_months,
                        'start_date': fd.start_date.isoformat() if fd.start_date else None,
                        'maturity_date': fd.maturity_date.isoformat() if fd.maturity_date else None,
                        'maturity_amount': fd.maturity_amount,
                        'interest_frequency': fd.interest_frequency
                    },
                    tags=['fixed-deposit', 'debt', 'low-risk'],
                    is_active=True
                )
                db.session.add(asset_embedding)
                db.session.commit()
                return asset_embedding.id
                
        except Exception as e:
            logger.error(f"Error embedding fixed deposit: {str(e)}")
            db.session.rollback()
            return None
    
    def embed_futures_options(self, user_id: int, fo: Any) -> Optional[int]:
        """
        Create/update embedding for F&O holding
        """
        try:
            description = self._build_fo_description(fo)
            embedding = self.vector_service.generate_embedding(description)
            
            if not embedding:
                return None
            
            existing = PortfolioAssetEmbedding.query.filter_by(
                user_id=user_id,
                source_table='manual_futures_options_holdings',
                source_record_id=fo.id
            ).first()
            
            if existing:
                existing.asset_description = description
                existing.embedding = embedding
                existing.quantity = fo.quantity
                existing.current_value = fo.current_value
                existing.purchase_value = fo.total_investment
                existing.updated_at = datetime.utcnow()
                db.session.commit()
                return existing.id
            else:
                asset_embedding = PortfolioAssetEmbedding(
                    user_id=user_id,
                    asset_type='futures_options',
                    asset_symbol=fo.symbol,
                    asset_name=f"{fo.symbol} {fo.contract_type}",
                    asset_category='derivative',
                    source_table='manual_futures_options_holdings',
                    source_record_id=fo.id,
                    broker_account_id=fo.broker_account_id,
                    asset_description=description,
                    quantity=fo.quantity,
                    current_value=fo.current_value,
                    purchase_value=fo.total_investment,
                    embedding=embedding,
                    asset_metadata={
                        'contract_type': fo.contract_type,
                        'strike_price': fo.strike_price,
                        'expiry_date': fo.expiry_date.isoformat() if fo.expiry_date else None,
                        'lot_size': fo.lot_size,
                        'exchange': fo.exchange
                    },
                    tags=['derivatives', 'f&o', 'high-risk'],
                    is_active=fo.is_active
                )
                db.session.add(asset_embedding)
                db.session.commit()
                return asset_embedding.id
                
        except Exception as e:
            logger.error(f"Error embedding F&O: {str(e)}")
            db.session.rollback()
            return None
    
    def search_portfolio_assets(self, user_id: int, query: str, asset_type: Optional[str] = None, 
                               limit: int = 10) -> List[Dict]:
        """
        Semantic search over user's portfolio assets
        
        Args:
            user_id: User ID
            query: Natural language query (e.g., "my technology stocks", "high-risk investments")
            asset_type: Optional filter by asset type
            limit: Max results to return
            
        Returns:
            List of matching assets with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.vector_service.generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Get all active embeddings for user
            query_filter = PortfolioAssetEmbedding.query.filter_by(
                user_id=user_id,
                is_active=True
            )
            
            if asset_type:
                query_filter = query_filter.filter_by(asset_type=asset_type)
            
            embeddings = query_filter.all()
            
            if not embeddings:
                return []
            
            # Extract embeddings
            embedding_vectors = [emb.embedding for emb in embeddings if emb.embedding]
            
            if not embedding_vectors:
                return []
            
            # Perform similarity search
            similar_indices = self.vector_service.cosine_similarity_search(
                query_embedding,
                embedding_vectors,
                top_k=min(limit, len(embedding_vectors))
            )
            
            # Build results
            results = []
            for idx, score in similar_indices:
                asset = embeddings[idx]
                results.append({
                    'id': asset.id,
                    'asset_name': asset.asset_name,
                    'asset_symbol': asset.asset_symbol,
                    'asset_type': asset.asset_type,
                    'asset_category': asset.asset_category,
                    'description': asset.asset_description,
                    'quantity': asset.quantity,
                    'current_value': asset.current_value,
                    'purchase_value': asset.purchase_value,
                    'current_price': asset.current_price,
                    'metadata': asset.asset_metadata,
                    'tags': asset.tags,
                    'similarity_score': score,
                    'source_table': asset.source_table,
                    'source_record_id': asset.source_record_id
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching portfolio assets: {str(e)}")
            return []
    
    def sync_all_user_assets(self, user_id: int) -> Dict[str, int]:
        """
        Sync all portfolio assets for a user to vector database
        Called after bulk import or broker sync
        
        Returns:
            Dictionary with counts of synced assets by type
        """
        from models import (
            ManualEquityHolding, ManualMutualFundHolding, ManualFixedDepositHolding,
            ManualFuturesOptionsHolding
        )
        from models_broker import BrokerHolding, BrokerAccount
        
        stats = {
            'broker_holdings': 0,
            'manual_equities': 0,
            'mutual_funds': 0,
            'fixed_deposits': 0,
            'futures_options': 0
        }
        
        try:
            # Sync broker holdings
            broker_accounts = BrokerAccount.query.filter_by(user_id=user_id).all()
            for account in broker_accounts:
                holdings = BrokerHolding.query.filter_by(broker_account_id=account.id).all()
                for holding in holdings:
                    if self.embed_broker_holding(user_id, holding, account.id):
                        stats['broker_holdings'] += 1
            
            # Sync manual equities
            equities = ManualEquityHolding.query.filter_by(user_id=user_id).all()
            for equity in equities:
                if self.embed_manual_equity(user_id, equity):
                    stats['manual_equities'] += 1
            
            # Sync mutual funds
            mfs = ManualMutualFundHolding.query.filter_by(user_id=user_id).all()
            for mf in mfs:
                if self.embed_mutual_fund(user_id, mf):
                    stats['mutual_funds'] += 1
            
            # Sync fixed deposits
            fds = ManualFixedDepositHolding.query.filter_by(user_id=user_id).all()
            for fd in fds:
                if self.embed_fixed_deposit(user_id, fd):
                    stats['fixed_deposits'] += 1
            
            # Sync F&O
            fos = ManualFuturesOptionsHolding.query.filter_by(user_id=user_id).all()
            for fo in fos:
                if self.embed_futures_options(user_id, fo):
                    stats['futures_options'] += 1
            
            self.logger.info(f"Synced all assets for user {user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error syncing all user assets: {str(e)}")
            return stats
    
    def _build_broker_holding_description(self, holding: Any) -> str:
        """Build rich description for broker holding"""
        desc = f"{holding.company_name or holding.symbol} ({holding.symbol}) - "
        desc += f"Indian equity stock traded on {holding.exchange}. "
        desc += f"Holding {holding.available_quantity} shares at average cost of ₹{holding.avg_cost_price:.2f}. "
        desc += f"Current price: ₹{holding.current_price:.2f}. "
        desc += f"Total investment: ₹{holding.investment_value:.2f}, "
        desc += f"current value: ₹{holding.total_value:.2f}. "
        
        if holding.pnl != 0:
            desc += f"P&L: ₹{holding.pnl:.2f} ({holding.pnl_percentage:.2f}%). "
        
        if holding.isin:
            desc += f"ISIN: {holding.isin}. "
        
        return desc.strip()
    
    def _build_manual_equity_description(self, equity: Any) -> str:
        """Build rich description for manual equity"""
        desc = f"{equity.company_name} ({equity.symbol}) - "
        desc += f"Equity holding of {equity.quantity} shares purchased at ₹{equity.purchase_price:.2f} per share. "
        
        if equity.current_price:
            desc += f"Current price: ₹{equity.current_price:.2f}. "
            desc += f"Unrealized P&L: ₹{equity.unrealized_pnl or 0:.2f} ({equity.unrealized_pnl_percentage or 0:.2f}%). "
        
        desc += f"Traded on {equity.exchange}. "
        desc += f"Portfolio: {equity.portfolio_name}. "
        
        return desc.strip()
    
    def _build_mutual_fund_description(self, mf: Any) -> str:
        """Build rich description for mutual fund"""
        desc = f"{mf.scheme_name} - "
        desc += f"Mutual fund managed by {mf.fund_house or 'fund house'}. "
        desc += f"Category: {mf.fund_category or 'not specified'}, Type: {mf.fund_type or 'not specified'}. "
        desc += f"Holding {mf.units:.2f} units at NAV ₹{mf.nav:.2f}. "
        desc += f"Total investment: ₹{mf.total_investment:.2f}, current value: ₹{mf.current_value or 0:.2f}. "
        
        if mf.sip_active:
            desc += f"Active SIP of ₹{mf.sip_amount or 0} {mf.sip_frequency or 'monthly'}. "
        
        return desc.strip()
    
    def _build_fd_description(self, fd: Any) -> str:
        """Build rich description for fixed deposit"""
        desc = f"Fixed deposit with {fd.bank_name} for ₹{fd.principal_amount:,.2f}. "
        desc += f"Interest rate: {fd.interest_rate}% per annum, "
        desc += f"tenure: {fd.tenure_months} months. "
        
        if fd.maturity_date:
            desc += f"Matures on {fd.maturity_date.strftime('%d %b %Y')} "
            desc += f"with expected amount: ₹{fd.maturity_amount or 0:,.2f}. "
        
        desc += f"Interest paid {fd.interest_frequency or 'quarterly'}. "
        desc += f"Current value: ₹{fd.current_value or 0:,.2f}. "
        desc += "Low-risk debt instrument."
        
        return desc.strip()
    
    def _build_fo_description(self, fo: Any) -> str:
        """Build rich description for F&O"""
        desc = f"{fo.symbol} {fo.contract_type} derivative contract. "
        
        if fo.strike_price:
            desc += f"Strike price: ₹{fo.strike_price}. "
        
        if fo.expiry_date:
            desc += f"Expires on {fo.expiry_date.strftime('%d %b %Y')}. "
        
        desc += f"Holding {fo.quantity} lots (lot size: {fo.lot_size}). "
        desc += f"Total investment: ₹{fo.total_investment:.2f}, "
        desc += f"current value: ₹{fo.current_value or 0:.2f}. "
        desc += f"Traded on {fo.exchange}. "
        desc += "High-risk derivatives instrument."
        
        return desc.strip()
    
    def _extract_tags_from_holding(self, holding: Any) -> List[str]:
        """Extract semantic tags from holding"""
        tags = ['equity', 'stock', 'broker-holding']
        
        # Add exchange
        if holding.exchange:
            tags.append(holding.exchange.lower())
        
        return tags
    
    def _extract_tags_from_mf(self, mf: Any) -> List[str]:
        """Extract tags from mutual fund"""
        tags = ['mutual-fund', 'managed-fund']
        
        if mf.fund_category:
            tags.append(mf.fund_category.lower().replace(' ', '-'))
        
        if mf.fund_type:
            tags.append(mf.fund_type.lower().replace(' ', '-'))
        
        if mf.sip_active:
            tags.append('sip-active')
        
        return tags
    
    def _get_mf_category(self, fund_category: Optional[str]) -> str:
        """Map fund category to asset category"""
        if not fund_category:
            return 'hybrid'
        
        category_lower = fund_category.lower()
        
        if 'equity' in category_lower or 'growth' in category_lower:
            return 'equity'
        elif 'debt' in category_lower or 'income' in category_lower or 'bond' in category_lower:
            return 'debt'
        else:
            return 'hybrid'
