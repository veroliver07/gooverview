import os
import random
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ------------------------------------------------------------------
# Helper – fetch the AI Overview from Google
# ------------------------------------------------------------------
def fetch_ai_overview(query: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&udm=14"

    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        r.encoding = "utf-8"

        soup = BeautifulSoup(r.text, "html.parser")
        ai_div = soup.find("div", {"data-attrid": "auto"})

        if ai_div:
            return {"status": "success", "ai_overview": ai_div.get_text(strip=True)}

        return {"status": "success", "ai_overview": "No AI Overview found for this query."}

    except requests.exceptions.RequestException as exc:
        # Network / HTTP errors
        return {"status": "error", "message": f"Network error: {exc}"}
    except Exception as exc:
        # Any other unexpected error
        return {"status": "error", "message": f"Unexpected error: {exc}"}


# ------------------------------------------------------------------
# API endpoint
# ------------------------------------------------------------------
@app.route("/api/overview")
def api_overview():
    query = request.args.get("q")
    if not query:
        return (
            jsonify({"error": "Missing required query parameter 'q'"}),
            400,
        )

    # Small delay to avoid hammering Google
    time.sleep(random.uniform(1, 2))

    result = fetch_ai_overview(query)
    return jsonify(result)


# ------------------------------------------------------------------
# Documentation page – just renders the static template
# ------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ------------------------------------------------------------------
# Run the app – Railway will use gunicorn, but this works locally
# ------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
