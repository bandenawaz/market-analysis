"""
Market data fetcher for dpboss-boston.com
Implements web scraping with caching to reduce load on source site
Vercel handler for API endpoints
"""
import requests
from bs4 import BeautifulSoup
import time
import logging
import json
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
        market_data = {}
        
        try:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
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
        
        if self._is_cache_valid(cache_key):
            logger.debug(f"Returning cached data for {cache_key}")
            return self.cache.get(cache_key, {})
        
        logger.debug(f"Fetching fresh data for {cache_key}")
        html = self._fetch_raw_data("https://dpboss-boston.com")
        
        if html is None:
            logger.warning("Failed to fetch data, returning cached data if available")
            if cache_key in self.cache:
                return self.cache[cache_key]
            return {} if market_name else {}
        
        all_data = self._parse_market_data(html)
        
        self.cache[cache_key] = all_data
        self.last_fetch[cache_key] = time.time()
        
        if market_name and market_name in all_data:
            return {market_name: all_data[market_name]}
        elif market_name:
            return {}
            
        return all_data

market_fetcher = MarketFetcher()

def get_market_data(market_name: Optional[str] = None) -> Dict[str, Any]:
    return market_fetcher.get_market_data(market_name)

def get_specific_market_data(market_name: str) -> Dict[str, Any]:
    return market_fetcher.get_market_data(market_name)


def handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    if method != 'GET':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }

    if path == '/api/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': b'OK'
        }

    if path == '/api/market-data':
        data = get_market_data()
        if not data:
            return {
                'statusCode': 503,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Service temporarily unavailable'}).encode('utf-8')
            }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data).encode('utf-8')
        }

    if path.startswith('/api/market-data/'):
        market_name = path.split('/')[-1]
        data = get_specific_market_data(market_name)
        if not data:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f"Market '{market_name}' not found"}).encode('utf-8')
            }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data).encode('utf-8')
        }

    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found'}).encode('utf-8')
    }
