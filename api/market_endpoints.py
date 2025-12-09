"""
FastAPI Market Data Endpoints
High-performance async market data API with caching
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, validator
import asyncio

from fastapi_app import get_read_db_session, cache_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/market", tags=["market"])

# Pydantic models
class StockQuoteResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open_price: float
    close_price: Optional[float] = None
    timestamp: datetime

class MarketOverviewResponse(BaseModel):
    indices: Dict[str, Any]
    top_gainers: List[Dict[str, Any]]
    top_losers: List[Dict[str, Any]]
    most_active: List[Dict[str, Any]]
    market_status: str
    timestamp: datetime

class WatchlistRequest(BaseModel):
    symbols: List[str]
    
    @validator('symbols')
    def validate_symbols(cls, v):
        if not v or len(v) > 50:  # Limit to 50 symbols
            raise ValueError('Watchlist must contain 1-50 symbols')
        return [symbol.upper().strip() for symbol in v]

# Async market data service
class AsyncMarketService:
    """Async wrapper for market data operations"""
    
    @staticmethod
    async def get_stock_quote_async(symbol: str) -> Dict[str, Any]:
        """Get stock quote asynchronously"""
        try:
            from services.nse_service import NSEService
            
            nse_service = NSEService()
            quote = await asyncio.to_thread(nse_service.get_stock_data, symbol)
            return quote
        except Exception as e:
            logger.error(f"Failed to fetch quote for {symbol}: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def get_market_overview_async() -> Dict[str, Any]:
        """Get market overview asynchronously"""
        try:
            from services.nse_service import NSEService
            
            nse_service = NSEService()
            overview = await asyncio.to_thread(nse_service.get_market_overview)
            return overview
        except Exception as e:
            logger.error(f"Failed to fetch market overview: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def get_multiple_quotes_async(symbols: List[str]) -> Dict[str, Any]:
        """Get multiple stock quotes concurrently"""
        try:
            tasks = [
                AsyncMarketService.get_stock_quote_async(symbol) 
                for symbol in symbols
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            quotes = {}
            for symbol, result in zip(symbols, results):
                if isinstance(result, Exception):
                    quotes[symbol] = {"error": str(result)}
                else:
                    quotes[symbol] = result
            
            return {"quotes": quotes, "timestamp": datetime.utcnow()}
        except Exception as e:
            logger.error(f"Failed to fetch multiple quotes: {e}")
            return {"error": str(e)}

@router.get("/quote/{symbol}", response_model=StockQuoteResponse)
@cache_response(expire_seconds=30)  # Cache for 30 seconds
async def get_stock_quote(
    symbol: str,
    request: Request
):
    """Get real-time stock quote with caching"""
    try:
        symbol = symbol.upper().strip()
        quote_data = await AsyncMarketService.get_stock_quote_async(symbol)
        
        if quote_data.get("error"):
            raise HTTPException(status_code=400, detail=quote_data["error"])
        
        # Transform data to match response model
        return StockQuoteResponse(
            symbol=symbol,
            price=quote_data.get("price", 0.0),
            change=quote_data.get("change", 0.0),
            change_percent=quote_data.get("change_percent", 0.0),
            volume=quote_data.get("volume", 0),
            high=quote_data.get("high", 0.0),
            low=quote_data.get("low", 0.0),
            open_price=quote_data.get("open", 0.0),
            close_price=quote_data.get("prev_close"),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock quote")

@router.get("/overview", response_model=MarketOverviewResponse)
@cache_response(expire_seconds=60)  # Cache for 1 minute
async def get_market_overview(request: Request):
    """Get market overview with indices and top movers"""
    try:
        overview_data = await AsyncMarketService.get_market_overview_async()
        
        if overview_data.get("error"):
            raise HTTPException(status_code=500, detail=overview_data["error"])
        
        return MarketOverviewResponse(
            indices=overview_data.get("indices", {}),
            top_gainers=overview_data.get("top_gainers", []),
            top_losers=overview_data.get("top_losers", []),
            most_active=overview_data.get("most_active", []),
            market_status=overview_data.get("market_status", "unknown"),
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get market overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market overview")

@router.post("/watchlist")
@cache_response(expire_seconds=15)  # Cache for 15 seconds
async def get_watchlist_quotes(
    watchlist: WatchlistRequest,
    request: Request
):
    """Get quotes for multiple symbols concurrently"""
    try:
        quotes_data = await AsyncMarketService.get_multiple_quotes_async(watchlist.symbols)
        
        if quotes_data.get("error"):
            raise HTTPException(status_code=500, detail=quotes_data["error"])
        
        return JSONResponse({
            "success": True,
            "quotes": quotes_data["quotes"],
            "symbols_count": len(watchlist.symbols),
            "timestamp": quotes_data["timestamp"].isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get watchlist quotes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch watchlist quotes")

@router.get("/search")
@cache_response(expire_seconds=300)  # Cache for 5 minutes
async def search_stocks(
    query: str = Query(..., min_length=2, max_length=50),
    limit: int = Query(10, ge=1, le=50),
    request: Request = None
):
    """Search stocks by symbol or company name"""
    try:
        from services.nse_service import NSEService
        
        nse_service = NSEService()
        search_results = await asyncio.to_thread(
            nse_service.search_stocks,
            query,
            limit
        )
        
        return JSONResponse({
            "success": True,
            "query": query,
            "results": search_results,
            "count": len(search_results),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Stock search failed for query '{query}': {e}")
        raise HTTPException(status_code=500, detail="Stock search failed")

@router.get("/historical/{symbol}")
@cache_response(expire_seconds=1800)  # Cache for 30 minutes
async def get_historical_data(
    symbol: str,
    period: str = Query("1Y", regex="^(1D|1W|1M|3M|6M|1Y|2Y|5Y)$"),
    request: Request = None
):
    """Get historical price data"""
    try:
        symbol = symbol.upper().strip()
        
        # Map period to days
        period_days = {
            "1D": 1,
            "1W": 7,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365,
            "2Y": 730,
            "5Y": 1825
        }
        
        days = period_days.get(period, 365)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        from services.nse_service import NSEService
        nse_service = NSEService()
        
        historical_data = await asyncio.to_thread(
            nse_service.get_historical_data,
            symbol,
            start_date.strftime("%d-%m-%Y"),
            end_date.strftime("%d-%m-%Y")
        )
        
        return JSONResponse({
            "success": True,
            "symbol": symbol,
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": historical_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical data")

@router.get("/sectors")
@cache_response(expire_seconds=3600)  # Cache for 1 hour
async def get_sector_performance(request: Request):
    """Get sector-wise performance"""
    try:
        from services.nse_service import NSEService
        
        nse_service = NSEService()
        sector_data = await asyncio.to_thread(nse_service.get_sector_performance)
        
        return JSONResponse({
            "success": True,
            "sectors": sector_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get sector performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sector performance")