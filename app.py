import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "AI Overview API is running!"

@app.route('/health')
def health():
    return "OK"

@app.route('/ai-overview')
def ai_overview():
    query = request.args.get('q')
    if not query:
        return {"error": "No query provided"}, 400
    
    try:
        # Method 1: DuckDuckGo Instant Answer API (Always works)
        url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # Extract answer from DuckDuckGo
        answer = None
        
        if data.get('AbstractText'):
            answer = data['AbstractText']
        elif data.get('Answer'):
            answer = data['Answer']
        elif data.get('Definition'):
            answer = data['Definition']
        elif data.get('Results') and len(data['Results']) > 0:
            answer = data['Results'][0].get('Text')
        
        if answer:
            return {
                "query": query,
                "ai_overview": answer,
                "success": True,
                "source": "duckduckgo"
            }
        
        # Method 2: Wikipedia API (Always works)
        wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        wiki_response = requests.get(wiki_url, headers=headers, timeout=10)
        
        if wiki_response.status_code == 200:
            wiki_data = wiki_response.json()
            if wiki_data.get('extract'):
                return {
                    "query": query,
                    "ai_overview": wiki_data['extract'][:1000],
                    "success": True,
                    "source": "wikipedia"
                }
        
        # Method 3: Scrape DuckDuckGo HTML
        ddg_url = f"https://html.duckduckgo.com/html/?q={query}"
        ddg_response = requests.get(ddg_url, headers=headers, timeout=10)
        
        if ddg_response.status_code == 200:
            soup = BeautifulSoup(ddg_response.text, 'html.parser')
            
            # Find instant answer
            result = soup.find('div', class_='result__body')
            if result:
                snippet = result.find('a', class_='result__snippet')
                if snippet:
                    return {
                        "query": query,
                        "ai_overview": snippet.get_text(strip=True),
                        "success": True,
                        "source": "duckduckgo_html"
                    }
        
        # Method 4: Google Custom Search (If you have API key)
        # You can add this later
        
        return {
            "query": query,
            "ai_overview": None,
            "success": False,
            "message": "Could not find answer"
        }
    
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
