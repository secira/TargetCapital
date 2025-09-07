"""
FastAPI Broker Management Endpoints
Async implementation of broker account management with enhanced security
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, validator

from fastapi_app import get_db_session, cache_response, BrokerAccountRequest, OrderRequest
from models_broker import BrokerAccount, BrokerType, ConnectionStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/broker", tags=["broker"])

# Pydantic models
class BrokerAccountResponse(BaseModel):
    id: int
    broker_type: str
    client_id: str
    connection_status: str
    is_active: bool
    created_at: datetime
    last_sync: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    order_id: str
    symbol: str
    quantity: int
    price: Optional[float]
    status: str
    timestamp: datetime

# Async broker service wrapper
class AsyncBrokerService:
    """Async wrapper for broker operations"""
    
    @staticmethod
    async def validate_credentials(broker_type: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Validate broker credentials asynchronously"""
        try:
            # Import synchronous broker service and run in thread pool
            import asyncio
            from services.broker_service import BrokerService
            
            broker_service = BrokerService()
            # Run in thread pool to avoid blocking
            result = await asyncio.to_thread(
                broker_service.test_connection,
                broker_type,
                credentials
            )
            return result
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def execute_order_async(broker_account: BrokerAccount, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute order asynchronously"""
        try:
            import asyncio
            from services.broker_service import BrokerService
            
            broker_service = BrokerService()
            result = await asyncio.to_thread(
                broker_service.place_order,
                broker_account.id,
                order_data
            )
            return result
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return {"success": False, "error": str(e)}

@router.get("/accounts", response_model=List[BrokerAccountResponse])
@cache_response(expire_seconds=60)
async def get_broker_accounts(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = 1  # TODO: Replace with actual authentication
):
    """Get user's broker accounts with caching"""
    try:
        query = select(BrokerAccount).where(BrokerAccount.user_id == current_user_id)
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        return [BrokerAccountResponse.from_orm(account) for account in accounts]
    
    except Exception as e:
        logger.error(f"Failed to fetch broker accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch broker accounts")

@router.post("/accounts", response_model=BrokerAccountResponse)
async def add_broker_account(
    account_request: BrokerAccountRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = 1  # TODO: Replace with actual authentication
):
    """Add new broker account with async credential validation"""
    try:
        # Check if user already has this broker type
        existing_query = select(BrokerAccount).where(
            and_(
                BrokerAccount.user_id == current_user_id,
                BrokerAccount.broker_type == account_request.broker_type
            )
        )
        result = await db.execute(existing_query)
        existing_account = result.scalar_one_or_none()
        
        if existing_account:
            raise HTTPException(
                status_code=400,
                detail="Account with this broker already exists"
            )
        
        # Validate credentials asynchronously
        credentials = {
            'client_id': account_request.client_id,
            'access_token': account_request.access_token,
            'api_secret': account_request.api_secret,
            'totp_secret': account_request.totp_secret
        }
        
        validation_result = await AsyncBrokerService.validate_credentials(
            account_request.broker_type,
            credentials
        )
        
        if not validation_result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=f"Credential validation failed: {validation_result.get('error')}"
            )
        
        # Create broker account
        broker_account = BrokerAccount(
            user_id=current_user_id,
            broker_type=BrokerType(account_request.broker_type).value,
            client_id=account_request.client_id,
            connection_status=ConnectionStatus.CONNECTED.value,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Encrypt and store credentials
        broker_account.set_credentials({
            'access_token': account_request.access_token,
            'api_secret': account_request.api_secret,
            'totp_secret': account_request.totp_secret
        })
        
        db.add(broker_account)
        await db.commit()
        await db.refresh(broker_account)
        
        # Schedule background sync
        background_tasks.add_task(sync_broker_data_background, broker_account.id)
        
        return BrokerAccountResponse.from_orm(broker_account)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to add broker account: {e}")
        raise HTTPException(status_code=500, detail="Failed to add broker account")

@router.delete("/accounts/{account_id}")
async def remove_broker_account(
    account_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = 1  # TODO: Replace with actual authentication
):
    """Remove broker account"""
    try:
        query = select(BrokerAccount).where(
            and_(
                BrokerAccount.id == account_id,
                BrokerAccount.user_id == current_user_id
            )
        )
        result = await db.execute(query)
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Broker account not found")
        
        await db.delete(account)
        await db.commit()
        
        return JSONResponse({"success": True, "message": "Broker account removed successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to remove broker account: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove broker account")

@router.post("/accounts/{account_id}/orders", response_model=OrderResponse)
async def place_order(
    account_id: int,
    order_request: OrderRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = 1  # TODO: Replace with actual authentication
):
    """Place trading order through broker API"""
    try:
        # Get broker account
        query = select(BrokerAccount).where(
            and_(
                BrokerAccount.id == account_id,
                BrokerAccount.user_id == current_user_id,
                BrokerAccount.is_active == True
            )
        )
        result = await db.execute(query)
        broker_account = result.scalar_one_or_none()
        
        if not broker_account:
            raise HTTPException(status_code=404, detail="Active broker account not found")
        
        # Prepare order data
        order_data = {
            "symbol": order_request.symbol,
            "quantity": order_request.quantity,
            "price": order_request.price,
            "order_type": order_request.order_type,
            "transaction_type": order_request.transaction_type,
            "product_type": order_request.product_type
        }
        
        # Execute order asynchronously
        result = await AsyncBrokerService.execute_order_async(broker_account, order_data)
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Order execution failed: {result.get('error')}"
            )
        
        # Return order response
        return OrderResponse(
            order_id=result.get("order_id", "unknown"),
            symbol=order_request.symbol,
            quantity=order_request.quantity,
            price=order_request.price,
            status=result.get("status", "pending"),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Order placement failed: {e}")
        raise HTTPException(status_code=500, detail="Order placement failed")

@router.get("/accounts/{account_id}/positions")
@cache_response(expire_seconds=30)  # Cache for 30 seconds
async def get_positions(
    account_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user_id: int = 1  # TODO: Replace with actual authentication
):
    """Get current positions from broker"""
    try:
        # Get broker account
        query = select(BrokerAccount).where(
            and_(
                BrokerAccount.id == account_id,
                BrokerAccount.user_id == current_user_id,
                BrokerAccount.is_active == True
            )
        )
        result = await db.execute(query)
        broker_account = result.scalar_one_or_none()
        
        if not broker_account:
            raise HTTPException(status_code=404, detail="Active broker account not found")
        
        # Fetch positions asynchronously
        import asyncio
        from services.broker_service import BrokerService
        
        broker_service = BrokerService()
        positions = await asyncio.to_thread(
            broker_service.get_positions,
            broker_account.id
        )
        
        return JSONResponse({
            "success": True,
            "positions": positions.get("positions", []),
            "total_pnl": positions.get("total_pnl", 0),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch positions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch positions")

# Background task for broker data sync
async def sync_broker_data_background(account_id: int):
    """Background task to sync broker data"""
    try:
        import asyncio
        from services.broker_service import BrokerService
        
        broker_service = BrokerService()
        await asyncio.to_thread(broker_service.sync_account_data, account_id)
        logger.info(f"Background sync completed for account {account_id}")
        
    except Exception as e:
        logger.error(f"Background sync failed for account {account_id}: {e}")