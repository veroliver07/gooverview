#!/usr/bin/env python3
# app.py

import os
import json
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

# -----------------------------
# 1️⃣  Flask app instance
# -----------------------------
app = Flask(__name__)

# -----------------------------
# 2️⃣  Helper: fetch AI overview
# -----------------------------
def fetch_ai_overview(query: str) -> dict:
    """
    Accepts either a plain search string or a full Google URL.
    Returns a dict with 'status' and either 'ai_overview' or an error message.
    """
    # Decide which URL to hit
    if query.lower().startswith("https://www.google.com/search"):
        url = query
    else:
        # Encode the raw query
        encoded_query = requests.utils.quote(query)
        url = (
            f"https://www.google.com/search?q={encoded_query}"
            "&sourceid=chrome&ie=UTF-8&udm=50&aep=48&cud=0"
            "&qsubts=1781281494894&source=chrome.crn.obic"
            "&mstk=AUtExfAUWidfkjLc0ughR9BM5NyqgqvkMKrJvX3Q7I5P0LWIEaMQ1"
            "E-ceJ0y8gFIJi8frcFen8EZlwMiA1-htAYxjHxbTIHE9im9TfQOzaaA4He-GsaNQTFKGvlJDAYPkS9j4amOLg9etoJHZoY4QKereIbUe9Z6U-EsvQ&csuir=1"
        )

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        r.encoding = "utf-8"

        soup = BeautifulSoup(r.text, "html.parser")

        # Google may use different selectors; try a couple of common ones
        ai_div = (
            soup.find("div", {"data-attrid": "auto"})
            or soup.find("div", class_="Z3Vnc")
        )

        if ai_div:
            ai_text = ai_div.get_text(strip=True)
            return {"status": "success", "ai_overview": ai_text}
        else:
            return {
                "status": "success",
                "ai_overview": "No AI Overview found for this query.",
            }

    except requests.exceptions.RequestException as exc:
        return {"status": "error", "message": f"Network error: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": f"Unexpected error: {exc}"}


# -----------------------------
# 3️⃣  API endpoint
# -----------------------------
@app.route("/api/overview", methods=["GET"])
def api_overview():
    query = request.args.get("q", "").strip()
    if not query:
        return (
            jsonify(
                {"status": "error", "message": "Missing required query parameter 'q'."}
            ),
            400,
        )

    result = fetch_ai_overview(query)
    return jsonify(result), 200 if result.get("status") == "success" else 500


# -----------------------------
# 4️⃣  Optional: run locally with Flask dev server
# -----------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
