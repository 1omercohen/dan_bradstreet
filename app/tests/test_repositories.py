import pytest
from app.repositories.stock import StockRepository

@pytest.mark.asyncio
async def test_create_stock(test_db, sample_stock_data):
    """Test creating a new stock"""
    repository = StockRepository(test_db)
    
    stock = await repository.create(sample_stock_data)
    
    assert stock.symbol == "AAPL"
    assert stock.close == 152.0
    assert stock.amount == 10

@pytest.mark.asyncio
async def test_get_stock_by_symbol(test_db, sample_stock_data):
    """Test getting stock by symbol"""
    repository = StockRepository(test_db)
    
    # Create stock
    await repository.create(sample_stock_data)
    
    # Get stock
    stock = await repository.get_by_symbol("AAPL")
    
    assert stock is not None
    assert stock.symbol == "AAPL"
    assert stock.close == 152.0

@pytest.mark.asyncio
async def test_get_nonexistent_stock(test_db):
    """Test getting non-existent stock"""
    repository = StockRepository(test_db)
    
    stock = await repository.get_by_symbol("NONEXISTENT")
    
    assert stock is None

@pytest.mark.asyncio
async def test_update_amount(test_db, sample_stock_data):
    """Test updating stock amount"""
    repository = StockRepository(test_db)
    
    # Create stock
    await repository.create(sample_stock_data)
    
    # Update amount
    updated_stock = await repository.update_amount("AAPL", 5)
    
    assert updated_stock is not None
    assert updated_stock.amount == 15  # 10 + 5

@pytest.mark.asyncio
async def test_update_market_data(test_db, sample_stock_data):
    """Test updating market data"""
    repository = StockRepository(test_db)
    
    # Create stock
    await repository.create(sample_stock_data)
    
    # Update market data
    new_data = {"close": 160.0, "high": 165.0}
    updated_stock = await repository.update_market_data("AAPL", new_data)
    
    assert updated_stock is not None
    assert updated_stock.close == 160.0
    assert updated_stock.high == 165.0