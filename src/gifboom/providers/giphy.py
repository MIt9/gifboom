"""GIPHY provider."""

from __future__ import annotations

import httpx

from gifboom.config import settings
from gifboom.models import GifResult, SearchResult
from gifboom.providers import BaseProvider

GIPHY_BASE = "https://api.giphy.com/v1/gifs"


class GiphyProvider(BaseProvider):
    name = "giphy"
    api_key_url = "https://developers.giphy.com/dashboard/"

    def is_configured(self) -> bool:
        return bool(settings.giphy_api_key)

    def _build_gif(self, item: dict) -> GifResult:
        images = item.get("images", {})
        original = images.get("original", {})
        preview = images.get("fixed_width_small", images.get("preview_gif", {}))
        return GifResult(
            id=item["id"],
            title=item.get("title", ""),
            url=original.get("url", ""),
            preview_url=preview.get("url", original.get("url", "")),
            width=int(original.get("width", 0)),
            height=int(original.get("height", 0)),
            size_bytes=int(original.get("size", 0)),
            duration_s=None,
            frame_count=int(original.get("frames", 0)) or None,
            provider="giphy",
            rating=item.get("rating", "g"),
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
                f"{GIPHY_BASE}/search",
                params={
                    "api_key": settings.giphy_api_key,
                    "q": query,
                    "limit": limit,
                    "offset": offset,
                    "rating": rating,
                    "lang": "en",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        items = [self._build_gif(item) for item in data.get("data", [])]
        total = data.get("pagination", {}).get("total_count", len(items))
        return SearchResult(
            items=items, total=total, query=query, provider=self.name, offset=offset
        )

    async def get_by_id(self, gif_id: str) -> SearchResult:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{GIPHY_BASE}/{gif_id}",
                params={"api_key": settings.giphy_api_key},
            )
            resp.raise_for_status()
            data = resp.json()

        item = self._build_gif(data["data"])
        return SearchResult(items=[item], total=1, query=gif_id, provider=self.name)
