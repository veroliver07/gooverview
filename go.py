import os
from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import urllib.parse
import random
import time

app = Flask(__name__)

# ----------- AI Overview helper ----------
def fetch_ai_overview(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded}&udm=14"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        ai = soup.find('div', {'data-attrid': 'auto'})
        if ai:
            return {"status":"success","ai_overview":ai.get_text(strip=True)}
        return {"status":"success","ai_overview":"No AI Overview found."}
    except Exception as e:
        return {"status":"error","message":str(e)}

# ----------- API ----------
@app.route('/api/overview')
def api_overview():
    query = request.args.get('q')
    if not query:
        return jsonify({"error":"Missing 'q' parameter"}), 400
    time.sleep(random.uniform(1,2))          # gentle rate‑limit
    return jsonify(fetch_ai_overview(query))

# ----------- Documentation ----------
@app.route('/')
def home():
    return render_template('index.html')

# ----------- Run ----------
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
