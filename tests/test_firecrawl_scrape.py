from unittest.mock import patch, MagicMock
from scrape_pipeline import firecrawl_scrape


def test_firecrawl_scrape_returns_flat_dict():
    fake_response = MagicMock()
    fake_response.json.return_value = {
        "data": {
            "markdown": "# Hello\n\nBody.",
            "metadata": {
                "title": "Hello Title",
                "url": "https://example.com/article",
                "sourceURL": "https://example.com/article",
                "description": "A short description.",
            },
        }
    }
    fake_response.raise_for_status = MagicMock()

    with patch("scrape_pipeline.requests.post", return_value=fake_response) as mock_post:
        result = firecrawl_scrape("https://example.com/article")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.firecrawl.dev/v2/scrape"
    assert kwargs["headers"]["Authorization"].startswith("Bearer ")
    assert kwargs["json"]["url"] == "https://example.com/article"
    assert kwargs["json"]["formats"] == ["markdown"]

    assert result == {
        "title": "Hello Title",
        "url": "https://example.com/article",
        "description": "A short description.",
        "markdown": "# Hello\n\nBody.",
    }
    fake_response.raise_for_status.assert_called_once()


def test_firecrawl_scrape_falls_back_to_sourceurl_when_url_missing():
    fake_response = MagicMock()
    fake_response.json.return_value = {
        "data": {
            "markdown": "body",
            "metadata": {
                "title": "T",
                "sourceURL": "https://example.com/fallback",
                "description": "",
            },
        }
    }
    fake_response.raise_for_status = MagicMock()

    with patch("scrape_pipeline.requests.post", return_value=fake_response):
        result = firecrawl_scrape("https://example.com/fallback")

    assert result["url"] == "https://example.com/fallback"
