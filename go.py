import requests
from bs4 import BeautifulSoup
import json
import urllib.parse

def get_google_ai_overview(query):
    """
    Fetches the AI Overview text from Google Search for a given query.
    """
    # 1. Set up headers to mimic a real browser (Chrome on Windows)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Connection': 'keep-alive',
    }

    # 2. Encode the query parameter
    encoded_query = urllib.parse.quote(query)
    
    # 3. Construct the URL (You can add '&udm=14' to force AI Mode if available)
    url = f"https://www.google.com/search?q={encoded_query}&udm=14"

    try:
        # 4. Send GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for errors
        
        # 5. Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 6. Extract AI Overview Text
        # Note: Google changes class names frequently. 
        # Common selector for AI Overview is div[data-attrid="auto"] or similar.
        # We will try multiple selectors for robustness.
        
        ai_text = ""
        
        # Selector 1: Data attribute method (Most reliable)
        ai_div = soup.find('div', {'data-attrid': 'auto'})
        if ai_div:
            ai_text = ai_div.get_text(strip=True)
        else:
            # Fallback: Try to find elements with specific AI-related classes
            # This may vary based on Google's current UI update
            ai_elements = soup.select('div[role="article"] span[class*="AIOverview"]')
            if ai_elements:
                ai_text = " ".join([el.get_text() for el in ai_elements])

        # 7. Return structured JSON (API Format)
        return {
            "status": "success",
            "query": query,
            "ai_overview": ai_text if ai_text else "No AI Overview found for this query.",
            "source_url": url
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# --- Example Usage ---
if __name__ == "__main__":
    # Change the query as per your logic
    query = "who is ahmed shara"
    result = get_google_ai_overview(query)
    
    print(json.dumps(result, indent=2))
