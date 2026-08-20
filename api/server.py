"""
Flask API server for serving market data
"""
import time
from flask import Flask, jsonify, abort
from werkzeug.exceptions import HTTPException
import logging
from market_fetcher import get_market_data, get_specific_market_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/api/market-data', methods=['GET'])
def get_all_market_data():
    """GET endpoint to return all markets data"""
    try:
        logger.info("Fetching all market data")
        data = get_market_data()
        if not data:
            logger.warning("No market data available")
            abort(503, description="Service temporarily unavailable - no market data")
        return jsonify(data), 200
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        abort(503, description="Service temporarily unavailable")

@app.route('/api/market-data/<string:market_name>', methods=['GET'])
def get_market_data_endpoint(market_name):
    """GET endpoint to return data for a specific market"""
    try:
        logger.info(f"Fetching market data for {market_name}")
        data = get_specific_market_data(market_name)
        if not data:
            logger.warning(f"No data found for market: {market_name}")
            abort(404, description=f"Market '{market_name}' not found")
        return jsonify(data), 200
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market data for {market_name}: {e}")
        abort(503, description="Service temporarily unavailable")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
