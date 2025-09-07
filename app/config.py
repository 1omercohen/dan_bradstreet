import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./stocks.db")
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")
    
    POLYGON_BASE_URL: str = "https://api.polygon.io"
    MARKETWATCH_BASE_URL: str = "https://www.marketwatch.com/investing/stock"
    
    CACHE_TTL: int = 60
    # STOCK_SYMBOLS: list = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    STOCK_SYMBOLS: list = ["AAPL"]

settings = Settings()