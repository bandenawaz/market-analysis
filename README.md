# Satta Matka Market Analysis Platform

This platform combines WhatsApp-based bet tracking with live market result display for Satta Matka games, sourcing live data from dpboss-boston.com.

## Features

### Live Market Data Display
- Fetches real-time market data from dpboss-boston.com
- Shows Open, Jodi, Close, and Final Ank values for major markets:
  - Kalyan
  - Main Bazar
  - Milan Day/Night
  - Rajdhani Day/Night
- Implements 5-minute caching to reduce load on source site
- Updates display every 30 seconds via AJAX polling
- Color-coded display for easy reading:
  - Open: Green (#28a745)
  - Jodi: Teal (#20c997)
  - Close: Red (#dc3545)
  - Final Ank: Purple (#6f42c1)

### API Endpoints
- `GET /api/market-data` - Returns all markets data as JSON
- `GET /api/market-data/<market_name>` - Returns data for specific market
- `GET /health` - Health check endpoint

### Bet Tracking
- Existing WhatsApp-based bet tracking functionality (preserved)
- Bet statistics and analytics

### Excel Export
- Export bet data alongside live market data
- Includes timestamp of when market data was fetched
- Separate worksheets for bet tracking and market data

## Implementation Details

### Backend (Python/Flask)
- `api/market_fetcher.py`: Web scraper with caching mechanism
- `api/server.py`: Flask API server with market data endpoints
- `api/utils/excel_export.py`: Excel export functionality enhanced with market data

### Frontend (HTML/CSS/JS)
- `dashboard/index.html`: Main dashboard interface
- `dashboard/static/js/dashboard.js`: Dynamic updates and UI logic
- `dashboard/static/css/dashboard.css`: Styling including color-coded market data

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python api/server.py
   ```

3. Access the dashboard at `http://localhost:5000`

## Architecture

```
Frontend (Dashboard)  <-- AJAX (30s interval) -->  Backend API (Flask)
                                                               |
                                                               V
                                                Market Fetcher (with 5-min cache)
                                                               |
                                                               V
                                                dpboss-boston.com (source)
```

## Caching Strategy
- Market data is cached for 5 minutes to prevent overloading dpboss-boston.com
- Frontend updates every 30 seconds for near-real-time display
- Graceful degradation when source site is unavailable (returns 503 with cached data if available)

## Security Considerations
- Input validation on all API endpoints
- Error handling prevents information leakage
- No direct user input passed to web scraper (uses predefined market list)
- Rate limiting consideration through caching
