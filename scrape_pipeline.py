import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")


def firecrawl_scrape(url: str) -> dict:
    response = requests.post(
        "https://api.firecrawl.dev/v2/scrape",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"url": url, "formats": ["markdown"]},
    )
    response.raise_for_status()
    body = response.json()
    data = body["data"]
    metadata = data.get("metadata", {})
    return {
        "title": metadata.get("title", ""),
        "url": metadata.get("url") or metadata.get("sourceURL") or url,
        "description": metadata.get("description", ""),
        "markdown": data.get("markdown", ""),
    }


# Each pattern is scoped to its own host; cross-domain links in a listing are intentionally ignored.
ARTICLE_URL_PATTERNS = {
    "ir.chipotle.com": re.compile(r"https://ir\.chipotle\.com/\d{4}-\d{2}-\d{2}-[^\s)\"']+"),
    "newsroom.chipotle.com": re.compile(r"https://newsroom\.chipotle\.com/\d{4}-\d{2}-\d{2}-[^\s)\"']+"),
}


def extract_article_urls(listing_md: str, listing_url: str) -> list[str]:
    host = urlparse(listing_url).netloc
    pattern = ARTICLE_URL_PATTERNS.get(host)
    if pattern is None:
        return []
    seen: set[str] = set()
    ordered: list[str] = []
    for match in pattern.findall(listing_md):
        if match not in seen:
            seen.add(match)
            ordered.append(match)
    return ordered


OUTPUT_DIR = Path("knowledge/raw")


def already_scraped(url: str, root: Path = None) -> bool:
    root = root if root is not None else OUTPUT_DIR
    if not root.exists():
        return False
    needle = f"url: {url}\n"
    for md_file in root.rglob("*.md"):
        try:
            text = md_file.read_text()
        except OSError:
            continue
        if needle in text:
            return True
    return False


def save_result(result: dict, ts: str, output_dir: Path = OUTPUT_DIR) -> Path:
    slug = re.sub(r'[^a-z0-9]+', '-', result['title'].lower()).strip('-')
    filename = f"{ts}_{slug}.md"
    path = output_dir / filename
    output_dir.mkdir(parents=True, exist_ok=True)
    frontmatter = f"---\ntitle: {result['title']}\nurl: {result['url']}\n"
    if result.get('description'):
        frontmatter += f"description: {result['description']}\n"
    frontmatter += f"scraped_at: {ts}\n---\n\n"
    path.write_text(frontmatter + (result.get('markdown') or ''))
    return path


if __name__ == "__main__":
    RUN_TS = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    # --- Step 01: Search + scrape with Firecrawl ---

    api_url = "https://api.firecrawl.dev/v2/search"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "query": "Chipotle investor relations press releases",
        "limit": 5,
        "scrapeOptions": {"formats": ["markdown"]}
    }

    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    results = data["data"]["web"]
    print(f"Firecrawl returned {len(results)} results")

    # --- Step 02: Save results to knowledge/raw/ ---

    for r in results:
        saved = save_result(r, RUN_TS)
        print(f"  Saved → {saved}")