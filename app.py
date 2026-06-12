import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "Google AI Overview API is running!"

@app.route('/health')
def health():
    return "OK"

@app.route('/ai-overview')
def ai_overview():
    query = request.args.get('q')
    if not query:
        return {"error": "No query provided"}, 400
    
    try:
        # Better headers to mimic real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        }
        
        # First get Google homepage to set cookies
        session = requests.Session()
        session.get("https://www.google.com", headers=headers, timeout=10)
        
        # Set consent cookie
        session.cookies.set('CONSENT', 'YES+cb.20231020-17-p0.en+FX+', domain='.google.com')
        
        # Make search request
        url = f"https://www.google.com/search?q={query}&hl=en&gl=us&num=10"
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return {"error": f"Google returned status {response.status_code}"}, 500
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: AI Overview specific div
        overview = None
        
        # Try multiple selectors for AI overview
        ai_selectors = [
            {'data-attrid': 'kc:/common/web/ai_answer'},
            {'data-attrid': 'wa'},
            {'class': 'V3FYCf'},
            {'class': 'wDYxhc'},
            {'class': 'c2xzTb'},
        ]
        
        for selector in ai_selectors:
            div = soup.find('div', selector)
            if div:
                overview = div.get_text(strip=True)
                if len(overview) > 50:  # Make sure it's substantial text
                    break
        
        # Method 2: Look for "AI Overview" heading
        if not overview:
            for heading in soup.find_all(['h2', 'h3', 'div']):
                if heading.get_text(strip=True).lower() in ['ai overview', 'overview', 'ai']:
                    parent = heading.find_parent('div')
                    if parent:
                        overview = parent.get_text(strip=True)
                        break
        
        # Method 3: Get featured snippet
        if not overview:
            featured = soup.find('div', {'data-content-feature': '1'})
            if featured:
                overview = featured.get_text(strip=True)
        
        # Method 4: First result text
        if not overview:
            first_result = soup.find('div', class_='g')
            if first_result:
                text = first_result.get_text(strip=True)
                # Clean up the text
                text = re.sub(r'\s+', ' ', text)
                if len(text) > 100:
                    overview = text[:1000]
        
        if overview:
            # Clean up the text
            overview = re.sub(r'\s+', ' ', overview)
            overview = overview.strip()
            
            return {
                "query": query,
                "ai_overview": overview,
                "success": True,
                "length": len(overview),
                "source": "google_search"
            }
        else:
            return {
                "query": query,
                "ai_overview": None,
                "success": False,
                "message": "Google did not show AI Overview for this query. Try a different query.",
                "note": "AI Overview is only shown for certain queries by Google"
            }
    
    except Exception as e:
        return {"error": str(e), "query": query}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
