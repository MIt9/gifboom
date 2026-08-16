"""Tests for URL resolver."""

from gifboom.resolver import resolve_media_url


def test_resolve_direct_gif_url():
    url = "https://media0.giphy.com/media/v1.Y2lkPTc5/giphy.gif"
    assert resolve_media_url(url) == url


def test_resolve_giphy_web_page_url():
    url = "https://giphy.com/gifs/happy-cat-3oKIPnAiaMCws8nOsE"
    resolved = resolve_media_url(url)
    assert resolved == "https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif"


def test_resolve_giphy_web_page_short_url():
    url = "https://giphy.com/gifs/3oKIPnAiaMCws8nOsE"
    resolved = resolve_media_url(url)
    assert resolved == "https://media.giphy.com/media/3oKIPnAiaMCws8nOsE/giphy.gif"
