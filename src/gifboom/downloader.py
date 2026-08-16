"""Download helper with caching and automatic URL resolution."""

from __future__ import annotations

import hashlib
from pathlib import Path

import diskcache
import httpx

from gifboom.config import settings
from gifboom.resolver import resolve_media_url


def _cache() -> diskcache.Cache:
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    return diskcache.Cache(str(settings.cache_dir), size_limit=int(settings.cache_size_gb * 1024**3))


def _url_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def download_gif(url: str, output_path: Path | None = None, force: bool = False) -> Path:
    """Download a GIF (or video) from URL, resolving web page wrappers and using disk cache.

    Args:
        url: Direct GIF URL or web page URL (GIPHY, Tenor, etc.).
        output_path: Where to save. Defaults to ~/Downloads/gifboom/<filename>
        force: Skip cache.

    Returns:
        Path to the downloaded file.
    """
    resolved_url = resolve_media_url(url)
    cache = _cache()
    key = _url_key(resolved_url)

    if not force and key in cache:
        cached_path = Path(cache[key])
        if cached_path.exists():
            return cached_path

    if output_path is None:
        settings.default_output_dir.mkdir(parents=True, exist_ok=True)
        raw_name = resolved_url.split("/")[-1].split("?")[0]
        ext = Path(raw_name).suffix if Path(raw_name).suffix in (".gif", ".mp4", ".webm", ".mov", ".png") else ".gif"
        stem = Path(raw_name).stem if Path(raw_name).stem else key[:12]
        filename = f"{stem}{ext}"
        output_path = settings.default_output_dir / filename

    async with (
        httpx.AsyncClient(timeout=60, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client,
        client.stream("GET", resolved_url) as resp,
    ):
        resp.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as f:
            async for chunk in resp.aiter_bytes(chunk_size=65536):
                f.write(chunk)

    cache[key] = str(output_path)
    return output_path


def cache_stats() -> dict:
    cache = _cache()
    return {
        "items": len(cache),
        "size_mb": round(cache.volume() / 1024**2, 2),
        "limit_gb": settings.cache_size_gb,
        "dir": str(settings.cache_dir),
    }


def cache_clear() -> None:
    cache = _cache()
    cache.clear()
