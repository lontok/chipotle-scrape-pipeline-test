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


def test_save_result_omits_absent_description(tmp_path):
    result = {
        "title": "SEC Filings",
        "url": "https://ir.chipotle.com/sec-filings",
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
