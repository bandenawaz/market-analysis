from .market_fetcher import get_market_data, get_specific_market_data
import json
import time

def app(event, context):
    # Extract the path and method from the event
    path = event.get('path', '')
    method = event.get('httpMethod', '')

    # We are only interested in GET requests for now
    if method != 'GET':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }

    # Health check
    if path == '/api/health':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'healthy', 'timestamp': time.time()})
        }

    # All market data
    if path == '/api/market-data':
        data = get_market_data()
        if not data:
            return {
                'statusCode': 503,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Service temporarily unavailable'})
            }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data)
        }

    # Specific market data
    if path.startswith('/api/market-data/'):
        market_name = path.split('/')[-1]
        data = get_specific_market_data(market_name)
        if not data:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': f"Market '{market_name}' not found"})
            }
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(data)
        }

    # If we reach here, the path is not found
    return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'error': 'Not found'})
    }
