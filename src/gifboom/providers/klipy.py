"""KLIPY provider."""

from __future__ import annotations

import httpx

from gifboom.config import settings
from gifboom.models import GifResult, SearchResult
from gifboom.providers import BaseProvider

KLIPY_BASE = "https://api.klipy.co/api/v1"


class KlipyProvider(BaseProvider):
    name = "klipy"
    api_key_url = "https://klipy.co/developer"

    def is_configured(self) -> bool:
        return bool(settings.klipy_api_key)

    def _build_gif(self, item: dict) -> GifResult:
        return GifResult(
            id=str(item.get("id", "")),
            title=item.get("title", ""),
            url=item.get("gif", {}).get("url", item.get("url", "")),
            preview_url=item.get("preview", {}).get("url", item.get("url", "")),
            width=item.get("width", 0),
            height=item.get("height", 0),
            size_bytes=item.get("size", 0),
            duration_s=item.get("duration"),
            frame_count=None,
            provider="klipy",
            tags=item.get("tags", []),
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
                f"{KLIPY_BASE}/gifs/search",
                headers={"Authorization": f"Bearer {settings.klipy_api_key}"},
                params={"q": query, "limit": limit, "offset": offset},
            )
            resp.raise_for_status()
            data = resp.json()

        results = data.get("data", data.get("results", []))
        items = [self._build_gif(r) for r in results]
        return SearchResult(items=items, total=data.get("total", len(items)), query=query, provider=self.name, offset=offset)

    async def get_by_id(self, gif_id: str) -> SearchResult:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{KLIPY_BASE}/gifs/{gif_id}",
                headers={"Authorization": f"Bearer {settings.klipy_api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()

        item = self._build_gif(data.get("data", data))
        return SearchResult(items=[item], total=1, query=gif_id, provider=self.name)
