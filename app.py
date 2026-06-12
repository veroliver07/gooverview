import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Simple health check - MUST be at root
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "message": "Google AI Overview API",
        "endpoints": {
            "ai_overview": "/ai-overview?q=your+query"
        }
    })

# Health check endpoint
@app.route('/health')
def health():
    return "OK", 200

# Main API endpoint
@app.route('/ai-overview')
def ai_overview():
    query = request.args.get('q')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # Headers to mimic browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        
        # Make request to Google
        url = f"https://www.google.com/search?q={query}&hl=en"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({"error": f"Google returned {response.status_code}"}), 500
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find AI overview or featured snippet
        overview = None
        
        # Method 1: Look for AI overview container
        for div in soup.find_all('div'):
            if div.get('data-attrid') == 'kc:/common/web/ai_answer':
                overview = div.get_text(strip=True)
                break
        
        # Method 2: Look for featured snippet
        if not overview:
            featured = soup.find('div', {'data-attrid': 'wa'})
            if featured:
                overview = featured.get_text(strip=True)
        
        # Method 3: Get first search result
        if not overview:
            first_result = soup.find('div', class_='g')
            if first_result:
                overview = first_result.get_text(strip=True)[:500]
        
        if overview:
            return jsonify({
                "query": query,
                "ai_overview": overview,
                "success": True
            })
        else:
            return jsonify({
                "query": query,
                "ai_overview": None,
                "success": False,
                "message": "No overview found"
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
