import requests
from bs4 import BeautifulSoup
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

def get_google_ai_overview(query):
    """Main function to extract AI overview from Google"""
    
    # Build the search URL
    search_url = f"https://www.google.com/search?q={query}&hl=en&gl=us"
    
    session = requests.Session()
    
    # Get initial cookies
    session.get("https://www.google.com", headers=get_headers(), timeout=10)
    
    # Set consent cookie
    session.cookies.set('CONSENT', 'YES+cb.20231020-17-p0.en+FX+', domain='.google.com')
    
    # Make the search request
    response = session.get(
        search_url,
        headers=get_headers(),
        timeout=30,
        allow_redirects=True
    )
    
    if response.status_code != 200:
        return {
            "error": f"Google returned status {response.status_code}",
            "query": query,
            "success": False
        }
    
    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try multiple selectors for AI overview
    overview = None
    
    # Method 1: Direct AI overview div
    ai_div = soup.find('div', {'data-attrid': 'kc:/common/web/ai_answer'})
    if ai_div:
        overview = ai_div.get_text(strip=True)
    
    # Method 2: Any div with AI in the class
    if not overview:
        for div in soup.find_all('div'):
            if div.get('class'):
                classes = ' '.join(div.get('class'))
                if 'AI' in classes or 'ai' in classes.lower():
                    text = div.get_text(strip=True)
                    if len(text) > 100:
                        overview = text
                        break
    
    # Method 3: Featured snippet
    if not overview:
        featured = soup.find('div', {'data-attrid': 'wa'})
        if featured:
            overview = featured.get_text(strip=True)
    
    # Method 4: First result with substantial text
    if not overview:
        first_result = soup.find('div', class_='g')
        if first_result:
            text = first_result.get_text(strip=True)
            if len(text) > 200:
                overview = text[:500]  # Limit to 500 chars
    
    if overview:
        return {
            "query": query,
            "ai_overview": overview,
            "success": True,
            "length": len(overview)
        }
    else:
        return {
            "query": query,
            "ai_overview": None,
            "success": False,
            "message": "No AI overview found for this query"
        }
