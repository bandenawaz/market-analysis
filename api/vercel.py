from .market_fetcher import get_market_data, get_specific_market_data
import json
import time

def app(event, context):
    # Extract the path and method from the event
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    # We are only interested in GET requests for now
    if method != 'GET':
        return (
            405,
            {'Content-Type': 'application/json'},
            json.dumps({'error': 'Method not allowed'}).encode('utf-8')
        )

    # Health check
    if path == '/api/health':
        return (
            200,
            {'Content-Type': 'application/json'},
            json.dumps({'status': 'healthy', 'timestamp': time.time()}).encode('utf-8')
        )

    # All market data
    if path == '/api/market-data':
        data = get_market_data()
        if not data:
            return (
                503,
                {'Content-Type': 'application/json'},
                json.dumps({'error': 'Service temporarily unavailable'}).encode('utf-8')
            )
        return (
            200,
            {'Content-Type': 'application/json'},
            json.dumps(data).encode('utf-8')
        )

    # Specific market data
    if path.startswith('/api/market-data/'):
        market_name = path.split('/')[-1]
        data = get_specific_market_data(market_name)
        if not data:
            return (
                404,
                {'Content-Type': 'application/json'},
                json.dumps({'error': f"Market '{market_name}' not found"}).encode('utf-8')
            )
        return (
            200,
            {'Content-Type': 'application/json'},
            json.dumps(data).encode('utf-8')
        )

    # If we reach here, the path is not found
    return (
        404,
        {'Content-Type': 'application/json'},
        json.dumps({'error': 'Not found'}).encode('utf-8')
    )
