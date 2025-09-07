import asyncio
import logging
import json
from typing import Optional

from app.repositories.stock import StockRepository
from app.services.polygon import PolygonService
from app.services.marketwatch import MarketWatchService
from app.schemas.stock import StockResponse
from app.cache import cache_service
from app.exceptions import StockNotFoundException, ExternalAPIException, CacheException

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self, repository: StockRepository):
        self.repository = repository
        self.polygon_service = PolygonService()
        self.marketwatch_service = MarketWatchService()

    async def get_stock(self, symbol: str) -> Optional[StockResponse]:
        cache_key = f"stock:{symbol.upper()}"
        
        try:
            cached_data = await cache_service.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for {symbol}")
                stock = await self.repository.get_by_symbol(symbol)
                cached_data['amount'] = stock.amount if stock else 0
                cached_data['performance'] = json.loads(cached_data['performance']) if 'performance' in cached_data and isinstance(cached_data['performance'], str) else cached_data.get('performance', {})
                return StockResponse(**cached_data)
        except CacheException as e:
            logger.warning(f"Cache read failed for {symbol}: {e.message}")

        stock = await self.repository.get_by_symbol(symbol)
        
        polygon_data = None
        performance_data = {}
        
        try:
            polygon_task = self.polygon_service.get_daily_open_close(symbol)
            marketwatch_task = self.marketwatch_service.get_performance_data(symbol)
            
            polygon_data, performance_data = await asyncio.gather(
                polygon_task, marketwatch_task, return_exceptions=True
            )

            if isinstance(polygon_data, ExternalAPIException):
                logger.error(f"Polygon service failed for {symbol}: {polygon_data.message}")
                polygon_data = None
            elif isinstance(polygon_data, Exception):
                logger.error(f"Unexpected Polygon error for {symbol}: {polygon_data}")
                polygon_data = None
            
            if isinstance(performance_data, ExternalAPIException):
                logger.error(f"MarketWatch service failed for {symbol}: {performance_data.message}")
                performance_data = {}
            elif isinstance(performance_data, Exception):
                logger.error(f"Unexpected MarketWatch error for {symbol}: {performance_data}")
                performance_data = {}
                
        except Exception as e:
            logger.error(f"Unexpected error fetching external data for {symbol}: {e}")
        
        if not polygon_data and not stock:
            raise StockNotFoundException(symbol)
        
        stock_data = {
            "symbol": symbol.upper(),
            "performance": performance_data or {},
            "amount": stock.amount if stock else 0
        }
        
        if polygon_data:
            stock_data.update(polygon_data)
        
        try:
            if stock:
                stock = await self.repository.update_market_data(symbol, stock_data)
            else:
                stock = await self.repository.create(stock_data)
        except Exception as e:
            logger.error(f"Database operation failed for {symbol}: {e}")
            if polygon_data:
                return StockResponse(**stock_data)
            raise
        
        try:
            market_data = stock_data.copy()
            market_data.pop('amount', None)
            await cache_service.set(cache_key, market_data)
        except CacheException as e:
            logger.warning(f"Cache write failed for {symbol}: {e.message}")
        
        return self._to_response(stock)

    async def update_stock_amount(self, symbol: str, amount: int) -> Optional[StockResponse]:
        try:
            stock = await self.repository.update_amount(symbol, amount)
            if not stock:
                stock_data = {"symbol": symbol.upper(), "amount": amount, "performance": "{}"}
                stock = await self.repository.create(stock_data)
            
            return self._to_response(stock)
        except Exception as e:
            logger.error(f"Failed to update stock amount for {symbol}: {e}")
            raise

    def _to_response(self, stock) -> StockResponse:
        performance = {}
        if stock.performance:
            try:
                performance = json.loads(stock.performance)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in performance data for {stock.symbol}: {e}")
                performance = {}
        
        return StockResponse(
            symbol=stock.symbol,
            afterHours=stock.after_hours,
            close=stock.close,
            **{"from": stock.from_date},
            high=stock.high,
            low=stock.low,
            open=stock.open,
            preMarket=stock.pre_market,
            status=stock.status,
            volume=stock.volume,
            performance=performance,
            amount=stock.amount,
            updated_at=stock.updated_at
        )

    async def cleanup(self):
        try:
            await self.polygon_service.close()
            await self.marketwatch_service.close()
        except Exception as e:
            logger.error(f"Error during service cleanup: {e}")