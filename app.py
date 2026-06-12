import re
import requests
from bs4 import BeautifulSoup

def fetch_ai_overview(query: str) -> dict:
    """
    Accepts either a plain search string or a full Google URL.
    Returns a dict with 'status' and either 'ai_overview' or an error message.
    """
    # 1️⃣ Decide which URL to hit
    if query.lower().startswith("https://www.google.com/search"):
        url = query
    else:
        encoded = requests.utils.quote(query)
        url = (
            f"https://www.google.com/search?q={encoded}"
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

        # ------------------------------------------------------------------
        # 2️⃣  Try the “AI Overview” container
        # ------------------------------------------------------------------
        ai_div = (
            soup.find("div", {"data-attrid": "auto"})
            or soup.find("div", class_="Z3Vnc")
        )
        if ai_div:
            return {
                "status": "success",
                "ai_overview": ai_div.get_text(strip=True),
            }

        # ------------------------------------------------------------------
        # 3️⃣  Try the snippet of the first search result
        # ------------------------------------------------------------------
        snippet = soup.find("span", class_="aCOpRe")
        if snippet:
            return {
                "status": "success",
                "ai_overview": snippet.get_text(strip=True),
            }

        # ------------------------------------------------------------------
        # 4️⃣  Fallback: regex search for “AI Overview …”
        # ------------------------------------------------------------------
        m = re.search(
            r"(?i)AI Overview.*?[.\n]{0,200}", r.text, re.S
        )
        if m:
            return {
                "status": "success",
                "ai_overview": m.group(0).strip(),
            }

        # ------------------------------------------------------------------
        # 5️⃣  No result – return the default message
        # ------------------------------------------------------------------
        return {
            "status": "success",
            "ai_overview": "No AI Overview found for this query.",
        }

    except requests.exceptions.RequestException as exc:
        return {"status": "error", "message": f"Network error: {exc}"}
    except Exception as exc:
        return {"status": "error", "message": f"Unexpected error: {exc}"}
