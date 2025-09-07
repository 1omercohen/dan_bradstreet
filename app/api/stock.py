from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database import get_db
from app.repositories.stock import StockRepository
from app.services.stock import StockService
from app.schemas.stock import StockResponse, StockUpdate
from app.exceptions import StockNotFoundException, StockAPIException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stock", tags=["stocks"])

async def get_stock_service(db: AsyncSession = Depends(get_db)) -> StockService:
    repository = StockRepository(db)
    return StockService(repository)

@router.get("/{stock_symbol}", response_model=StockResponse)
async def get_stock(
    stock_symbol: str,
    stock_service: StockService = Depends(get_stock_service)
):
    try:
        stock = await stock_service.get_stock(stock_symbol)
        if not stock:
            raise StockNotFoundException(stock_symbol)
        return stock
    except StockNotFoundException:
        raise  
    except StockAPIException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_stock for {stock_symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching stock data"
        )
    finally:
        try:
            await stock_service.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

@router.post("/{stock_symbol}", status_code=status.HTTP_201_CREATED)
async def update_stock_amount(
    stock_symbol: str,
    stock_update: StockUpdate,
    stock_service: StockService = Depends(get_stock_service)
):
    try:
        await stock_service.update_stock_amount(stock_symbol, stock_update.amount)
        return {
            "message": f"{stock_update.amount} units of stock {stock_symbol.upper()} were added to your stock record"
        }
    except StockAPIException:
        raise 
    except Exception as e:
        logger.error(f"Unexpected error in update_stock_amount for {stock_symbol}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating stock amount"
        )
    finally:
        try:
            await stock_service.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")