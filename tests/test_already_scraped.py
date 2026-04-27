from scrape_pipeline import already_scraped


def _write(path, url):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\ntitle: T\nurl: {url}\nscraped_at: 2026-04-26T00-00-00\n---\n\nbody")


def test_already_scraped_finds_url_in_top_level(tmp_path):
    _write(tmp_path / "a.md", "https://example.com/foo")
    assert already_scraped("https://example.com/foo", root=tmp_path) is True


def test_already_scraped_finds_url_in_subdir(tmp_path):
    _write(tmp_path / "sub" / "b.md", "https://example.com/bar")
    assert already_scraped("https://example.com/bar", root=tmp_path) is True


def test_already_scraped_returns_false_for_unknown_url(tmp_path):
    _write(tmp_path / "a.md", "https://example.com/foo")
    assert already_scraped("https://example.com/other", root=tmp_path) is False


def test_already_scraped_empty_dir(tmp_path):
    assert already_scraped("https://example.com/foo", root=tmp_path) is False


def test_already_scraped_does_not_match_substring(tmp_path):
    _write(tmp_path / "a.md", "https://example.com/foo")
    assert already_scraped("https://example.com/foo-extra", root=tmp_path) is False
