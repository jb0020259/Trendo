# Trend Analysis Dashboard

A Python-based dashboard that displays Google Trends data for various investment keywords using the pytrends API.

## Features

- Real-time Google Trends data visualization
- Four investment trend charts (Gold, Bitcoin, Stock Market, Real Estate)
- Responsive 2x2 grid layout
- Interactive charts with Plotly
- Data from 2004 to present
- India-specific trends

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to:
```
http://localhost:5000
```

## Technical Details

- Built with Flask and Python
- Uses pytrends API for Google Trends data
- Plotly.js for interactive charts
- Responsive design with CSS Grid
- Error handling and retry mechanisms

## Notes

- The application uses the pytrends API which may have rate limits
- Data is fetched from Google Trends for India (IN) region
- Time range is set from 2004 to present
- Charts are interactive and can be zoomed, panned, and downloaded 