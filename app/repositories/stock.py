from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
import json
import logging

from app.models.stock import Stock
from app.exceptions import StockAPIException

logger = logging.getLogger(__name__)

class StockRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_symbol(self, symbol: str) -> Optional[Stock]:
        try:
            result = await self.db.execute(
                select(Stock).where(Stock.symbol == symbol.upper())
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching stock {symbol}: {e}")
            raise StockAPIException(f"Failed to fetch stock {symbol}: {str(e)}")

    async def create(self, stock_data: dict) -> Stock:
        try:
            if 'performance' in stock_data and isinstance(stock_data['performance'], dict):
                stock_data['performance'] = json.dumps(stock_data['performance'])
            
            stock = Stock(**stock_data)
            self.db.add(stock)
            await self.db.commit()
            await self.db.refresh(stock)
            return stock
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error creating stock: {e}")
            raise StockAPIException(f"Failed to create stock: {str(e)}")

    async def update_market_data(self, symbol: str, market_data: dict) -> Optional[Stock]:
        try:
            logger.info(f"Updating market data for {symbol} with {market_data}")
            if 'performance' in market_data and isinstance(market_data['performance'], dict):
                market_data['performance'] = json.dumps(market_data['performance'])
            
            await self.db.execute(
                update(Stock)
                .where(Stock.symbol == symbol.upper())
                .values(**market_data)
            )
            await self.db.commit()
            return await self.get_by_symbol(symbol)
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating market data for {symbol}: {e}")
            raise StockAPIException(f"Failed to update market data for {symbol}: {str(e)}")

    async def update_amount(self, symbol: str, additional_amount: int) -> Optional[Stock]:
        try:
            stock = await self.get_by_symbol(symbol)
            if not stock:
                return None
            
            new_amount = stock.amount + additional_amount
            await self.db.execute(
                update(Stock)
                .where(Stock.symbol == symbol.upper())
                .values(amount=new_amount)
            )
            await self.db.commit()
            return await self.get_by_symbol(symbol)
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error updating amount for {symbol}: {e}")
            raise StockAPIException(f"Failed to update amount for {symbol}: {str(e)}")