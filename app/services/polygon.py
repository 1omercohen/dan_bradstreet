import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from app.config import settings
from app.exceptions import ExternalAPIException

logger = logging.getLogger(__name__)

class PolygonService:
    def __init__(self):
        self.base_url = settings.POLYGON_URL
        self.api_key = settings.POLYGON_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_daily_open_close(self, symbol: str, date: str = None) -> Optional[Dict[str, Any]]:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        url = f"{self.base_url}/{symbol.upper()}/{date}"
        params = {"apikey": self.api_key}
        
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "OK":
                error_msg = data.get("message", "Unknown error")
                logger.warning(f"Polygon API returned non-OK status for {symbol}: {error_msg}")
                raise ExternalAPIException("Polygon", error_msg)
            
            return {
                "symbol": data.get("symbol"),
                "open": data.get("open"),
                "high": data.get("high"),
                "low": data.get("low"),
                "close": data.get("close"),
                "volume": int(data.get("volume", 0)),
                "after_hours": data.get("afterHours"),
                "pre_market": data.get("preMarket"),
                "from_date": data.get("from"),
                "status": data.get("status")
            }
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ExternalAPIException("Polygon", f"Stock {symbol} not found")
            elif e.response.status_code == 429:
                raise ExternalAPIException("Polygon", "Rate limit exceeded")
            else:
                raise ExternalAPIException("Polygon", f"HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            raise ExternalAPIException("Polygon", f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Polygon service: {e}")
            raise ExternalAPIException("Polygon", "Unexpected error occurred")

    async def close(self):
        await self.client.aclose()