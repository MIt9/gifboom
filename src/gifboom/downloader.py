"""Download helper with caching."""

from __future__ import annotations

import hashlib
from pathlib import Path

import diskcache
import httpx

from gifboom.config import settings


def _cache() -> diskcache.Cache:
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    return diskcache.Cache(
        str(settings.cache_dir), size_limit=int(settings.cache_size_gb * 1024**3)
    )


def _url_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def download_gif(url: str, output_path: Path | None = None, force: bool = False) -> Path:
    """Download a GIF from URL, using cache.

    Args:
        url: Direct GIF URL.
        output_path: Where to save. Defaults to ~/Downloads/gifboom/<hash>.gif
        force: Skip cache.

    Returns:
        Path to the downloaded file.
    """
    cache = _cache()
    key = _url_key(url)

    if not force and key in cache:
        cached_path = Path(cache[key])
        if cached_path.exists():
            return cached_path

    if output_path is None:
        settings.default_output_dir.mkdir(parents=True, exist_ok=True)
        filename = url.split("/")[-1].split("?")[0] or f"{key[:12]}.gif"
        output_path = settings.default_output_dir / filename

    async with (
        httpx.AsyncClient(timeout=60, follow_redirects=True) as client,
        client.stream("GET", url) as resp,
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
