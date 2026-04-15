---
date: 2026-04-15
topic: Save Firecrawl search results as markdown files
status: approved
---

# Design: Save Firecrawl Results to knowledge/raw/

## Goal

Extend `scrape_pipeline.py` so each Firecrawl search result is persisted as a
markdown file in `knowledge/raw/` for downstream processing.

## File Naming

- Output directory: `knowledge/raw/` (created if absent)
- Filename pattern: `{YYYY-MM-DDTHH-MM-SS}_{slugified-title}.md`
- One shared timestamp per script run so a batch of 5 results sorts together
- Slug: lowercase title, non-alphanumeric chars collapsed to `-`, leading/trailing `-` stripped
- Example: `2026-04-15T08-25-00_news-releases-chipotle-mexican-grill.md`

## File Contents

```
---
title: <result title>
url: <result url>
description: <result description>   # omitted if empty/missing
scraped_at: <run timestamp>
---

<raw markdown body from Firecrawl, written as-is>
```

## Code Structure

- Strategy: inline helper function `save_result(result, ts)` added to `scrape_pipeline.py`
- `datetime` added to imports; `re` and `Path` already present
- No new dependencies
- `OUTPUT_DIR.mkdir(parents=True, exist_ok=True)` called once before the results loop
- Each saved path printed to stdout as `Saved → knowledge/raw/<filename>`

## Re-run Behavior

Always writes new files. The run timestamp in the filename means re-runs never
overwrite existing files.

## Out of Scope

- Deduplication or diffing against existing files
- Cleaning or trimming the markdown body
- Separate storage module (revisit if pipeline grows)
