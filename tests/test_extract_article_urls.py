from scrape_pipeline import extract_article_urls


IR_FIXTURE = """
- Mar 17, 2026

[CHIPOTLE MEXICAN GRILL TO ANNOUNCE FIRST QUARTER 2026 RESULTS ON APRIL 29, 2026](https://ir.chipotle.com/2026-03-17-CHIPOTLE-MEXICAN-GRILL-TO-ANNOUNCE-FIRST-QUARTER-2026-RESULTS-ON-APRIL-29,-2026)

- Feb 3, 2026

[CHIPOTLE ANNOUNCES FOURTH QUARTER AND FULL YEAR 2025 RESULTS](https://ir.chipotle.com/2026-02-03-CHIPOTLE-ANNOUNCES-FOURTH-QUARTER-AND-FULL-YEAR-2025-RESULTS)

- Some unrelated link: [Privacy Policy](https://www.chipotle.com/privacy-policy)
"""

NEWSROOM_FIXTURE = """
- [Apr 13, 2026](https://newsroom.chipotle.com/2026-04-13-CHIPOTLE-RELAUNCHES-REWARDS)
- [Mar 30, 2026](https://newsroom.chipotle.com/2026-03-30-BURRITO-VAULT)
- Footer link: [Privacy](https://www.chipotle.com/privacy-policy)
"""


def test_extract_article_urls_ir_listing():
    urls = extract_article_urls(IR_FIXTURE, "https://ir.chipotle.com/Financial-Releases")
    assert urls == [
        "https://ir.chipotle.com/2026-03-17-CHIPOTLE-MEXICAN-GRILL-TO-ANNOUNCE-FIRST-QUARTER-2026-RESULTS-ON-APRIL-29,-2026",
        "https://ir.chipotle.com/2026-02-03-CHIPOTLE-ANNOUNCES-FOURTH-QUARTER-AND-FULL-YEAR-2025-RESULTS",
    ]


def test_extract_article_urls_newsroom_listing():
    urls = extract_article_urls(NEWSROOM_FIXTURE, "https://newsroom.chipotle.com/press-releases")
    assert urls == [
        "https://newsroom.chipotle.com/2026-04-13-CHIPOTLE-RELAUNCHES-REWARDS",
        "https://newsroom.chipotle.com/2026-03-30-BURRITO-VAULT",
    ]


def test_extract_article_urls_dedupes_within_listing():
    md = """
    [Item](https://ir.chipotle.com/2026-01-12-LEADERSHIP)
    [Item again](https://ir.chipotle.com/2026-01-12-LEADERSHIP)
    """
    urls = extract_article_urls(md, "https://ir.chipotle.com/Financial-Releases")
    assert urls == ["https://ir.chipotle.com/2026-01-12-LEADERSHIP"]


def test_extract_article_urls_unknown_host_returns_empty():
    urls = extract_article_urls("anything", "https://example.com/listing")
    assert urls == []
