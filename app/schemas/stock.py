from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class StockBase(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)")

class StockCreate(StockBase):
    amount: int = Field(default=0, ge=0, description="Number of stocks to purchase")

class StockUpdate(BaseModel):
    amount: int = Field(..., ge=0, description="Number of stocks to add")

class StockResponse(StockBase):
    after_hours: Optional[float] = Field(None, alias="afterHours")
    close: Optional[float] = None
    from_date: Optional[str] = Field(None, alias="from")
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    pre_market: Optional[float] = Field(None, alias="preMarket")
    status: Optional[str] = None
    volume: Optional[int] = None
    performance: Optional[Dict[str, Any]] = None
    amount: int = 0
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True