"""URL resolver — extracts direct media (.gif, .mp4) links from web page wrappers."""

from __future__ import annotations

import re

import httpx


def resolve_media_url(url: str) -> str:
    """Resolve a web page URL (e.g. GIPHY/Tenor page or shortlink) to a direct media URL.

    Args:
        url: Web URL or direct media URL.

    Returns:
        Direct URL pointing to .gif, .mp4, or other binary media.
    """
    # 1. GIPHY web page URL: https://giphy.com/gifs/funny-cat-3oKIPnAiaMCws8nOsE
    giphy_match = re.search(r"giphy\.com/gifs/(?:[a-zA-Z0-9-]+-)?([a-zA-Z0-9]{10,25})(?:/|\?|$)", url)
    if giphy_match:
        gif_id = giphy_match.group(1)
        return f"https://media.giphy.com/media/{gif_id}/giphy.gif"

    # 2. If it's already a direct media file extension, return as-is
    clean_url = url.split("?")[0].lower()
    if clean_url.endswith((".gif", ".mp4", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".webp")):
        return url

    # 3. Otherwise, fetch the page HTML and extract OpenGraph / Twitter meta tags
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
            resp = client.get(url)
            content_type = resp.headers.get("content-type", "")

            if "text/html" in content_type or resp.text.lstrip().startswith(("<!", "<html", "<HTML")):
                html = resp.text

                # Check og:image (preferred for GIFs)
                og_image = re.search(
                    r"<meta[^>]+property=[\"\']og:image(?::secure_url)?[\"\'][^>]+content=[\"\']([^\"\'\>]+)[\"\']",
                    html,
                    re.IGNORECASE,
                ) or re.search(
                    r"<meta[^>]+content=[\"\']([^\"\'\>]+)[\"\'][^>]+property=[\"\']og:image(?::secure_url)?[\"\']",
                    html,
                    re.IGNORECASE,
                )
                if og_image:
                    return og_image.group(1)

                # Check twitter:image
                tw_image = re.search(
                    r"<meta[^>]+name=[\"\']twitter:image[\"\'][^>]+content=[\"\']([^\"\'\>]+)[\"\']",
                    html,
                    re.IGNORECASE,
                )
                if tw_image:
                    return tw_image.group(1)

                # Check og:video
                og_video = re.search(
                    r"<meta[^>]+property=[\"\']og:video(?::secure_url)?[\"\'][^>]+content=[\"\']([^\"\'\>]+)[\"\']",
                    html,
                    re.IGNORECASE,
                )
                if og_video:
                    return og_video.group(1)

                # Search for any .gif URL in page body
                gif_urls = re.findall(r"https://[^\s\"\'\>]+\.gif[^\s\"\'\>]*", html)
                if gif_urls:
                    return gif_urls[0]

            return str(resp.url)
    except Exception:
        return url
