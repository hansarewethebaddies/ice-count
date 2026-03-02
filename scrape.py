# scrape.py
import re
import json
import sys
import urllib.request
import urllib.error

# ------------------------------------------------------------
# URL of the Guardian interactive article that contains the tally
# ------------------------------------------------------------
ARTICLE_URL = (
    "https://www.theguardian.com/us-news/ng-interactive/2026/jan/04/ice-2025-deaths-timeline"
)

def fetch_article():
    """Download the article HTML. Raises on non‑200 response."""
    req = urllib.request.Request(
        ARTICLE_URL,
        headers={"User-Agent": "Mozilla/5.0 (compatible; NeocitiesBot/1.0)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Guardian responded {resp.status}")
            return resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error while fetching article: {e}") from e

def extract_count(html):
    """
    Try a few regex patterns to find the number of deaths.
    Returns an int or raises ValueError if nothing matches.
    """
    patterns = [
        r"(\d+)\s+people\s+died",          # e.g., "23 people died"
        r"(\d+)\s+people\s+have\s+died",  # e.g., "23 people have died"
        r"(\d+)\s+deaths?\b",             # e.g., "23 deaths"
        r"(\d+)\s+ICE\s+deaths?\b",       # e.g., "23 ICE deaths"
    ]
    for pat in patterns:
        m = re.search(pat, html, re.I)
        if m:
            return int(m.group(1))
    raise ValueError("Could not locate a death count in the article")

def main():
    try:
        html = fetch_article()
        count = extract_count(html)

        # Write the JSON file that the Neocities page will read
        data = {"count": count}
        with open("count.json", "w", encoding="utf-8") as f:
            json.dump(data, f)

        print(f"✅ Count extracted: {count}")
    except Exception as exc:
        # Print a clear error message for the Actions log
        print(f"❌ Error while processing: {exc}", file=sys.stderr)

        # OPTIONAL: keep the previous count.json unchanged rather than failing
        # If you want the workflow to *fail* (exit code != 0), uncomment the line below:
        # sys.exit(1)

if __name__ == "__main__":
    main()
