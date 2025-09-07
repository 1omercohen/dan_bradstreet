from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.database import Base

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    
    # Polygon.io data
    after_hours = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    from_date = Column(String, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    open = Column(Float, nullable=True)
    pre_market = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    volume = Column(Integer, nullable=True)
    
    # MarketWatch data (JSON string)
    performance = Column(String, nullable=True)
    
    # User data
    amount = Column(Integer, default=0)
    
    # Metadata
    updated_at = Column(DateTime, default=datetime.utcnow)