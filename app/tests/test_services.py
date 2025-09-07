import pytest
from unittest.mock import patch
from app.services.stock import StockService
from app.repositories.stock import StockRepository
from app.schemas.stock import StockResponse

@pytest.mark.asyncio
async def test_stock_service_get_stock_from_cache(test_db, sample_stock_data):
    """Test getting stock data from cache"""
    repository = StockRepository(test_db)
    service = StockService(repository)
    
    # Mock cache hit
    with patch('app.services.stock_service.cache_service') as mock_cache:
        mock_cache.get.return_value = {
            "symbol": "AAPL",
            "close": 152.0,
            "open": 150.0,
            "high": 155.0,
            "low": 149.0,
            "volume": 1000000
        }
        
        # Create stock in DB for amount
        await repository.create(sample_stock_data)
        
        result = await service.get_stock("AAPL")
        
        assert isinstance(result, StockResponse)
        assert result.symbol == "AAPL"
        assert result.close == 152.0
        assert result.amount == 10

@pytest.mark.asyncio
async def test_stock_service_polygon_service_failure(test_db):
    """Test handling of polygon service failure"""
    repository = StockRepository(test_db)
    service = StockService(repository)
    
    # Mock cache miss and polygon failure
    with patch('app.services.stock_service.cache_service') as mock_cache, \
         patch.object(service.polygon_service, 'get_daily_open_close') as mock_polygon:
        
        mock_cache.get.return_value = None
        mock_polygon.side_effect = Exception("API Error")
        
        # Mock marketwatch success
        with patch.object(service.marketwatch_service, 'get_performance_data') as mock_mw:
            mock_mw.return_value = {"1d": "1.2%"}
            
            result = await service.get_stock("AAPL")
            
            assert isinstance(result, StockResponse)
            assert result.symbol == "AAPL"

@pytest.mark.asyncio
async def test_update_stock_amount_new_stock(test_db):
    """Test updating amount for non-existent stock"""
    repository = StockRepository(test_db)
    service = StockService(repository)
    
    result = await service.update_stock_amount("NEWSTOCK", 5)
    
    assert isinstance(result, StockResponse)
    assert result.symbol == "NEWSTOCK"
    assert result.amount == 5

@pytest.mark.asyncio
async def test_update_stock_amount_existing_stock(test_db, sample_stock_data):
    """Test updating amount for existing stock"""
    repository = StockRepository(test_db)
    service = StockService(repository)
    
    # Create existing stock
    await repository.create(sample_stock_data)
    
    result = await service.update_stock_amount("AAPL", 5)
    
    assert isinstance(result, StockResponse)
    assert result.symbol == "AAPL"
    assert result.amount == 15  # 10 + 5