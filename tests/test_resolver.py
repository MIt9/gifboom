"""Tests for URL resolver."""

from gifboom.resolver import resolve_media_url


def test_resolve_direct_gif_url():
    url = "https://i.giphy.com/OK27wINdQS5YQ.gif"
    assert resolve_media_url(url) == url


def test_resolve_giphy_web_page_url():
    url = "https://giphy.com/gifs/happy-cat-3oKIPnAiaMCws8nOsE"
    resolved = resolve_media_url(url)
    assert resolved == "https://i.giphy.com/3oKIPnAiaMCws8nOsE.gif"


def test_resolve_giphy_web_page_short_url():
    url = "https://giphy.com/gifs/3oKIPnAiaMCws8nOsE"
    resolved = resolve_media_url(url)
    assert resolved == "https://i.giphy.com/3oKIPnAiaMCws8nOsE.gif"


def test_resolve_giphy_long_tracking_url():
    url = "https://media0.giphy.com/media/v1.Y2lkPTlkMThiY2ZlbW92b2lvNGRkd20ydzRraHJsdTA3cHl5dmFybXRjNWNwYjBzYXVqciZlcD12MV9naWZzX3NlYXJjaCZjdD1n/OK27wINdQS5YQ/giphy.gif"
    resolved = resolve_media_url(url)
    assert resolved == "https://i.giphy.com/OK27wINdQS5YQ.gif"
