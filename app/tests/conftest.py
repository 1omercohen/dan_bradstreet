import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.stock import Stock

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_stocks.db"
TEST_SYNC_DATABASE_URL = "sqlite:///./test_stocks.db"

# Test async engine
test_async_engine = create_async_engine(TEST_DATABASE_URL)
TestAsyncSessionLocal = async_sessionmaker(
    test_async_engine, class_=AsyncSession, expire_on_commit=False
)

# Test sync engine for setup
test_sync_engine = create_engine(TEST_SYNC_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session scope"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Create test database for each test"""
    # Create tables
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestAsyncSessionLocal() as session:
        yield session
    
    # Drop tables
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(test_db):
    """Create test client with test database"""
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_stock_data():
    """Sample stock data for testing"""
    return {
        "symbol": "AAPL",
        "open": 150.0,
        "high": 155.0,
        "low": 149.0,
        "close": 152.0,
        "volume": 1000000,
        "after_hours": 151.5,
        "pre_market": 150.5,
        "status": "OK",
        "from_date": "2024-01-10",
        "performance": '{"1d": "1.2%", "1w": "3.4%"}',
        "amount": 10
    }