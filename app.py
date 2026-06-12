def fetch_ai_overview(query: str) -> dict:
    """
    Accepts either:
      • a plain search string (e.g. "uk usa")
      • a full Google search URL (e.g. the long URL you pasted)

    Returns a dictionary with either the AI Overview text or a “not found” message.
    """

    # ------------------------------------------------------------------
    # 1️⃣  Decide which URL to hit
    # ------------------------------------------------------------------
    if query.lower().startswith("https://www.google.com/search"):
        # User supplied the *exact* Google URL – use it as‑is
        url = query
    else:
        # Build the Google URL in the exact format you want
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        # Encode the raw query for a URL‑friendly string
        encoded_query = urllib.parse.quote(query)

        # This is the *exact* template you showed
        url = (
            f"https://www.google.com/search?q={encoded_query}"
            "&sourceid=chrome&ie=UTF-8&udm=50&aep=48&cud=0"
            "&qsubts=1781281494894&source=chrome.crn.obic"
            "&mstk=AUtExfAUWidfkjLc0ughR9BM5NyqgqvkMKrJvX3Q7I5P0LWIEaMQ1"
            "E-ceJ0y8gFIJi8frcFen8EZlwMiA1-htAYxjHxbTIHE9im9TfQOzaaA4He-GsaNQTFKGvlJDAYPkS9j4amOLg9etoJHZoY4QKereIbUe9Z6U-EsvQ&csuir=1"
        )

    # ------------------------------------------------------------------
    # 2️⃣  Make the request
    # ------------------------------------------------------------------
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        r.encoding = "utf-8"

        soup = BeautifulSoup(r.text, "html.parser")

        # Google changed its layout a few times – try a couple of selectors
        ai_div = soup.find("div", {"data-attrid": "auto"}) or soup.find("div", class_="Z3Vnc")

        if ai_div:
            ai_text = ai_div.get_text(strip=True)
            return {"status": "success", "ai_overview": ai_text}
        else:
            return {"status": "success",
                    "ai_overview": "No AI Overview found for this query."}

    except requests.exceptions.RequestException as exc:
        return {"status": "error",
                "message": f"Network error: {exc}"}
    except Exception as exc:
        return {"status": "error",
                "message": f"Unexpected error: {exc}"}
