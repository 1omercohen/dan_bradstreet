import httpx
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict, Any
import re

from app.config import settings
from app.exceptions import ExternalAPIException

logger = logging.getLogger(__name__)

class MarketWatchService:
    def __init__(self):
        self.base_url = settings.MARKETWATCH_BASE_URL
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            }
        )

    async def get_performance_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{symbol.lower()}"
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            performance_data = {}
            
            performance_section = soup.find('div', {'class': re.compile(r'.*performance.*', re.I)})
            
            if not performance_section:
                tables = soup.find_all('table')
                for table in tables:
                    if 'performance' in str(table).lower():
                        performance_section = table
                        break
            
            if performance_section:
                rows = performance_section.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        key = re.sub(r'[^\w\s]', '', key).replace(' ', '_').lower()
                        performance_data[key] = value
            
            if not performance_data:
                logger.warning(f"No performance data found for {symbol}")
                return {"status": "no_data_found", "symbol": symbol.upper()}
            
            return performance_data
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ExternalAPIException("MarketWatch", f"Stock {symbol} not found")
            else:
                raise ExternalAPIException("MarketWatch", f"HTTP {e.response.status_code}")
        except httpx.RequestError as e:
            raise ExternalAPIException("MarketWatch", f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in MarketWatch service: {e}")
            raise ExternalAPIException("MarketWatch", "Unexpected error occurred")

    async def close(self):
        await self.client.aclose()