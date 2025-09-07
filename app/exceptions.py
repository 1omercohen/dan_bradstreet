class StockAPIException(Exception):
    """Base exception for stock API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ExternalAPIException(StockAPIException):
    """Exception for external API failures"""
    def __init__(self, service: str, message: str):
        super().__init__(f"{service} API error: {message}", 503)
        self.service = service

class StockNotFoundException(StockAPIException):
    """Exception when stock is not found"""
    def __init__(self, symbol: str):
        super().__init__(f"Stock {symbol} not found", 404)
        self.symbol = symbol

class InvalidStockDataException(StockAPIException):
    """Exception for invalid stock data"""
    def __init__(self, message: str):
        super().__init__(f"Invalid stock data: {message}", 400)

class CacheException(StockAPIException):
    """Exception for cache-related errors"""
    def __init__(self, message: str):
        super().__init__(f"Cache error: {message}", 500)