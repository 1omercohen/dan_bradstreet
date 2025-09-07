import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./stocks.db")
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")
    POLYGON_URL: str = "https://api.polygon.io/v1/open-close"
    MARKETWATCH_BASE_URL: str = "https://www.marketwatch.com/investing/stock"
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    CACHE_TTL: int = 60
    # STOCK_SYMBOLS: list = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    STOCK_SYMBOLS: list = ["AAPL"]

settings = Settings()