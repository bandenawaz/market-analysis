"""
Market data fetcher for dpboss-boston.com
Implements web scraping with caching to reduce load on source site
"""
import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MarketFetcher:
    def __init__(self, cache_ttl: int = 300):  # 5 minutes default
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.last_fetch = {}
        
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.last_fetch:
            return False
        return time.time() - self.last_fetch[key] < self.cache_ttl
    
    def _fetch_raw_data(self, url: str) -> Optional[str]:
        """Fetch raw HTML from the source site"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return None
    
    def _parse_market_data(self, html: str) -> Dict[str, Any]:
        """Parse market data from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        # This is a placeholder - actual parsing logic would depend on 
        # the structure of dpboss-boston.com
        market_data = {}
        
        # Example structure - would need to be adapted to actual site
        # Looking for common patterns in Satta Matka sites
        try:
            # Find market containers/tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        # Assuming format: Market Name, Open, Jodi, Close, Final Ank
                        market_name = cells[0].get_text(strip=True)
                        if market_name and len(market_name) > 0:
                            try:
                                open_val = cells[1].get_text(strip=True)
                                jodi_val = cells[2].get_text(strip=True)
                                close_val = cells[3].get_text(strip=True)
                                final_ank = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                                
                                market_data[market_name] = {
                                    'open': open_val,
                                    'jodi': jodi_val,
                                    'close': close_val,
                                    'final_ank': final_ank,
                                    'timestamp': time.time()
                                }
                            except (IndexError, ValueError):
                                continue
        except Exception as e:
            logger.error(f"Error parsing market data: {e}")
            
        return market_data
    
    def get_market_data(self, market_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get market data for all markets or a specific market
        Returns cached data if still valid, otherwise fetches fresh data
        """
        cache_key = market_name if market_name else "all"
        
        # Return cached data if valid
        if self._is_cache_valid(cache_key):
            logger.debug(f"Returning cached data for {cache_key}")
            return self.cache.get(cache_key, {})
        
        # Fetch fresh data
        logger.debug(f"Fetching fresh data for {cache_key}")
        html = self._fetch_raw_data("https://dpboss-boston.com")  # Example URL
        
        if html is None:
            logger.warning("Failed to fetch data, returning cached data if available")
            # Return stale cache if no fresh data available
            if cache_key in self.cache:
                return self.cache[cache_key]
            return {} if market_name else {}
        
        # Parse the data
        all_data = self._parse_market_data(html)
        
        # Update cache
        self.cache[cache_key] = all_data
        self.last_fetch[cache_key] = time.time()
        
        # If specific market requested, return just that market's data
        if market_name and market_name in all_data:
            return {market_name: all_data[market_name]}
        elif market_name:
            return {}  # Market not found
            
        return all_data

# Global instance for use in the application
market_fetcher = MarketFetcher()

def get_market_data(market_name: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to get market data"""
    return market_fetcher.get_market_data(market_name)

def get_specific_market_data(market_name: str) -> Dict[str, Any]:
    """Get data for a specific market"""
    return market_fetcher.get_market_data(market_name)
