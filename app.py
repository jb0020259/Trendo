from flask import Flask, render_template, jsonify
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

app = Flask(__name__)

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=330)  # 330 is the timezone offset for India (UTC+5:30)

def get_trend_data(keyword, timeframe='2004-01-01 2024-03-28'):
    try:
        # Build payload
        pytrends.build_payload([keyword], timeframe=timeframe, geo='IN')
        
        # Get interest over time
        interest_over_time_df = pytrends.interest_over_time()
        
        if interest_over_time_df.empty:
            return None
            
        # Convert to list for JSON serialization
        dates = interest_over_time_df.index.strftime('%Y-%m-%d').tolist()
        values = interest_over_time_df[keyword].tolist()
        
        return {
            'dates': dates,
            'values': values,
            'keyword': keyword
        }
    except Exception as e:
        print(f"Error fetching data for {keyword}: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/trends')
def get_trends():
    keywords = [
        'buy gold',
        'bitcoin investment',
        'stock market investment',
        'real estate investment'
    ]
    
    results = {}
    for keyword in keywords:
        data = get_trend_data(keyword)
        if data:
            results[keyword] = data
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True) 