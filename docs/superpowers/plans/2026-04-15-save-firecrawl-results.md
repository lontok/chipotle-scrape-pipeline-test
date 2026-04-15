# Save Firecrawl Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `scrape_pipeline.py` to save each Firecrawl search result as a timestamped markdown file with YAML frontmatter in `knowledge/raw/`.

**Architecture:** A `save_result(result, ts)` helper function is added inline to `scrape_pipeline.py`. It builds YAML frontmatter from the result dict, appends the raw markdown body, and writes the file to `knowledge/raw/`. One shared ISO timestamp is captured at run start so all files from a single run sort together.

**Tech Stack:** Python 3.11, pathlib, re, datetime (all stdlib)

---

### Task 1: Write and verify the save_result helper with tests

**Files:**
- Modify: `scrape_pipeline.py`
- Create: `tests/test_save_result.py`

- [ ] **Step 1: Create the tests directory and write the failing test**

```bash
mkdir -p tests
touch tests/__init__.py
```

Create `tests/test_save_result.py`:

```python
import pytest
from pathlib import Path
from scrape_pipeline import save_result


def test_save_result_creates_file(tmp_path):
    result = {
        "title": "News Releases - Chipotle Mexican Grill",
        "url": "https://ir.chipotle.com/news-releases",
        "description": "Investor news releases.",
        "markdown": "# News Releases\n\nSome content here.",
    }
    ts = "2026-04-15T08-25-00"
    saved = save_result(result, ts, output_dir=tmp_path)

    assert saved == tmp_path / "2026-04-15T08-25-00_news-releases-chipotle-mexican-grill.md"
    assert saved.exists()


def test_save_result_frontmatter(tmp_path):
    result = {
        "title": "News Releases - Chipotle Mexican Grill",
        "url": "https://ir.chipotle.com/news-releases",
        "description": "Investor news releases.",
        "markdown": "# News Releases\n\nSome content here.",
    }
    ts = "2026-04-15T08-25-00"
    saved = save_result(result, ts, output_dir=tmp_path)
    content = saved.read_text()

    assert content.startswith("---\n")
    assert "title: News Releases - Chipotle Mexican Grill\n" in content
    assert "url: https://ir.chipotle.com/news-releases\n" in content
    assert "description: Investor news releases.\n" in content
    assert "scraped_at: 2026-04-15T08-25-00\n" in content
    assert "---\n\n# News Releases" in content


def test_save_result_omits_missing_description(tmp_path):
    result = {
        "title": "SEC Filings",
        "url": "https://ir.chipotle.com/sec-filings",
        "description": "",
        "markdown": "# SEC Filings",
    }
    ts = "2026-04-15T08-25-00"
    saved = save_result(result, ts, output_dir=tmp_path)
    content = saved.read_text()

    assert "description:" not in content


def test_save_result_slug_special_chars(tmp_path):
    result = {
        "title": "Q1 2026: Earnings & Results!",
        "url": "https://ir.chipotle.com/q1",
        "description": None,
        "markdown": "",
    }
    ts = "2026-04-15T08-25-00"
    saved = save_result(result, ts, output_dir=tmp_path)

    assert saved.name == "2026-04-15T08-25-00_q1-2026-earnings-results.md"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
venv/bin/python -m pytest tests/test_save_result.py -v
```

Expected: 4 failures with `ImportError: cannot import name 'save_result' from 'scrape_pipeline'`

- [ ] **Step 3: Add save_result to scrape_pipeline.py**

Replace the top of `scrape_pipeline.py` (imports + setup) with:

```python
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
RUN_TS = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def save_result(result: dict, ts: str, output_dir: Path = OUTPUT_DIR) -> Path:
    slug = re.sub(r'[^a-z0-9]+', '-', result['title'].lower()).strip('-')
    filename = f"{ts}_{slug}.md"
    path = output_dir / filename
    frontmatter = f"---\ntitle: {result['title']}\nurl: {result['url']}\n"
    if result.get('description'):
        frontmatter += f"description: {result['description']}\n"
    frontmatter += f"scraped_at: {ts}\n---\n\n"
    path.write_text(frontmatter + (result.get('markdown') or ''))
    return path
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
venv/bin/python -m pytest tests/test_save_result.py -v
```

Expected output:
```
tests/test_save_result.py::test_save_result_creates_file PASSED
tests/test_save_result.py::test_save_result_frontmatter PASSED
tests/test_save_result.py::test_save_result_omits_missing_description PASSED
tests/test_save_result.py::test_save_result_slug_special_chars PASSED

4 passed
```

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/test_save_result.py tests/__init__.py
git commit -m "feat: add save_result helper with YAML frontmatter"
```

---

### Task 2: Wire save_result into the results loop

**Files:**
- Modify: `scrape_pipeline.py`

- [ ] **Step 1: Replace the results section**

Replace everything after the `save_result` function definition with:

```python
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
data = response.json()
results = data["data"]["web"]
print(f"Firecrawl returned {len(results)} results")

# --- Step 02: Save results to knowledge/raw/ ---

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
for r in results:
    saved = save_result(r, RUN_TS)
    print(f"  Saved → {saved}")
```

- [ ] **Step 2: Run the full pipeline**

```bash
venv/bin/python scrape_pipeline.py
```

Expected output (exact filenames vary by result titles; note that two results with identical titles produce the same slug and the second silently overwrites the first — deduplication is out of scope per spec):
```
Firecrawl returned 5 results
  Saved → knowledge/raw/2026-04-15T08-25-00_news-releases-chipotle-mexican-grill.md
  Saved → knowledge/raw/2026-04-15T08-25-00_chipotle-news-releases.md
  Saved → knowledge/raw/2026-04-15T08-25-00_chipotle-investorroom-home.md
  Saved → knowledge/raw/2026-04-15T08-25-00_news-releases-chipotle-mexican-grill.md
  Saved → knowledge/raw/2026-04-15T08-25-00_sec-filings-chipotle-mexican-grill.md
```

- [ ] **Step 3: Verify files exist and spot-check one**

```bash
ls knowledge/raw/
head -10 knowledge/raw/*.md | head -20
```

Expected: 5 `.md` files with `---` frontmatter visible at top.

- [ ] **Step 4: Run tests one final time**

```bash
venv/bin/python -m pytest tests/test_save_result.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py
git commit -m "feat: wire save_result into pipeline, write results to knowledge/raw/"
```
