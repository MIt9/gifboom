"""Tenor (Google) provider."""

from __future__ import annotations

import httpx

from gifboom.config import settings
from gifboom.models import GifResult, SearchResult
from gifboom.providers import BaseProvider

TENOR_BASE = "https://tenor.googleapis.com/v2"


class TenorProvider(BaseProvider):
    name = "tenor"
    api_key_url = "https://developers.google.com/tenor/guides/quickstart"

    def is_configured(self) -> bool:
        return bool(settings.tenor_api_key)

    def _build_gif(self, item: dict) -> GifResult:
        media = item.get("media_formats", {})
        gif = media.get("gif", {})
        tinygif = media.get("tinygif", gif)
        dims = gif.get("dims", [0, 0])
        return GifResult(
            id=item["id"],
            title=item.get("title", item.get("content_description", "")),
            url=gif.get("url", ""),
            preview_url=tinygif.get("url", gif.get("url", "")),
            width=dims[0] if dims else 0,
            height=dims[1] if len(dims) > 1 else 0,
            size_bytes=gif.get("size", 0),
            duration_s=item.get("hasaudio") and None or None,
            frame_count=None,
            provider="tenor",
            tags=item.get("tags", []),
            rating="g",
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        rating: str = "g",
    ) -> SearchResult:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{TENOR_BASE}/search",
                params={
                    "key": settings.tenor_api_key,
                    "q": query,
                    "limit": limit,
                    "pos": str(offset),
                    "contentfilter": rating
                    if rating in ("off", "low", "medium", "high")
                    else "low",
                    "media_filter": "gif,tinygif",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        items = [self._build_gif(r) for r in data.get("results", [])]
        return SearchResult(
            items=items, total=len(items), query=query, provider=self.name, offset=offset
        )

    async def get_by_id(self, gif_id: str) -> SearchResult:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{TENOR_BASE}/posts",
                params={"key": settings.tenor_api_key, "ids": gif_id},
            )
            resp.raise_for_status()
            data = resp.json()

        items = [self._build_gif(r) for r in data.get("results", [])]
        return SearchResult(items=items, total=len(items), query=gif_id, provider=self.name)
