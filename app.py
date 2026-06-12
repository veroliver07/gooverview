import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

def extract_ai_overview(html):
    """Extract the AI overview text from Google search results HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Multiple possible selectors for AI overview
    selectors = [
        'div[data-attrid="kc:/common/web/ai_answer"]',
        'div[class*="AIAnswer"]',
        'div[class*="ai-answer"]',
        'div[data-hveid*="AI"]',
        'div[class*="g"] div[style*="border"]',
        'div[role="heading"] + div',
        # Fallback: any large text block before the first result
    ]
    
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            # Clean up the text
            text = element.get_text(separator='\n', strip=True)
            if len(text) > 50:  # AI overviews are usually substantial
                return text
    
    # If no specific AI overview found, try to get the featured snippet
    featured = soup.select_one('div[data-attrid="wa"]')
    if featured:
        return featured.get_text(separator='\n', strip=True)
    
    return None

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "usage": "/ai-overview?q=your+query+here",
        "example": "/ai-overview?q=who+is+ahmed+shara"
    })

@app.route('/ai-overview')
def get_ai_overview():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Build the Google search URL
    search_url = f"https://www.google.com/search?q={query}&udm=50"
    
    try:
        # Send request with browser-like headers
        response = requests.get(
            search_url,
            headers=HEADERS,
            timeout=15,
            allow_redirects=True
        )
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Google returned status {response.status_code}",
                "query": query
            }), 500
        
        # Extract AI overview
        overview = extract_ai_overview(response.text)
        
        if overview:
            return jsonify({
                "query": query,
                "ai_overview": overview,
                "source": "google_ai_overview",
                "success": True
            })
        else:
            return jsonify({
                "query": query,
                "ai_overview": None,
                "message": "No AI overview found for this query",
                "success": False
            })
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "query": query
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
