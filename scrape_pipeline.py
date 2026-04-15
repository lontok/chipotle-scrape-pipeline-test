import os
import re
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

OUTPUT_DIR = Path("knowledge/raw")


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