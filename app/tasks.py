from celery import Celery
import asyncio
import logging

from app.database import AsyncSessionLocal
from app.repositories.stock import StockRepository
from app.services.polygon import PolygonService
from app.services.marketwatch import MarketWatchService

from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "stocks_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'sync-popular-stocks': {
            'task': 'app.tasks.sync_popular_stocks',
            'schedule': 300.0,
        },
    },
)

@celery_app.task
def sync_popular_stocks():
    popular_symbols = settings.STOCK_SYMBOLS
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(_sync_stocks_async(popular_symbols))
    finally:
        loop.close()

async def _sync_stocks_async(symbols: list):
    polygon_service = PolygonService()
    marketwatch_service = MarketWatchService()
    
    async with AsyncSessionLocal() as db:
        repository = StockRepository(db)
        
        for symbol in symbols:
            try:
                polygon_task = polygon_service.get_daily_open_close(symbol)
                marketwatch_task = marketwatch_service.get_performance_data(symbol)
                
                polygon_data, performance_data = await asyncio.gather(
                    polygon_task, marketwatch_task, return_exceptions=True
                )
                logger.info(f"Fetched data for {symbol}: polygon_data={polygon_data}, performance_data={performance_data}")
                if not isinstance(polygon_data, Exception) and polygon_data:
                    stock_data = {
                        "symbol": symbol,
                        "performance": performance_data if not isinstance(performance_data, Exception) else {},
                        **polygon_data
                    }
                    
                    existing_stock = await repository.get_by_symbol(symbol)
                    if existing_stock:
                        await repository.update_market_data(symbol, stock_data)
                    else:
                        await repository.create(stock_data)
                        
                logger.info(f"Synced data for {symbol}")
                
            except Exception as e:
                logger.error(f"Error syncing {symbol}: {e}")
    
    await polygon_service.close()
    await marketwatch_service.close()