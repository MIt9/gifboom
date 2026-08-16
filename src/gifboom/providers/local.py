"""Local directory provider — search GIF files on disk."""

from __future__ import annotations

import hashlib
from pathlib import Path

from gifboom.models import GifResult, SearchResult
from gifboom.providers import BaseProvider


class LocalProvider(BaseProvider):
    name = "local"

    def __init__(self, search_dirs: list[Path] | None = None):
        self.search_dirs = search_dirs or [Path.home() / "Downloads", Path.home() / "Pictures"]

    def _build_gif(self, path: Path) -> GifResult:
        stat = path.stat()
        uid = hashlib.md5(str(path).encode()).hexdigest()[:12]
        return GifResult(
            id=uid,
            title=path.stem,
            url=path.as_uri(),
            preview_url=path.as_uri(),
            width=0,
            height=0,
            size_bytes=stat.st_size,
            duration_s=None,
            frame_count=None,
            provider="local",
            tags=[],
        )

    def _all_gifs(self) -> list[Path]:
        gifs: list[Path] = []
        for d in self.search_dirs:
            if d.is_dir():
                gifs.extend(d.rglob("*.gif"))
        return sorted(gifs, key=lambda p: p.stat().st_mtime, reverse=True)

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        rating: str = "g",
    ) -> SearchResult:
        q = query.lower()
        matches = [p for p in self._all_gifs() if q in p.name.lower()]
        page = matches[offset : offset + limit]
        items = [self._build_gif(p) for p in page]
        return SearchResult(
            items=items, total=len(matches), query=query, provider=self.name, offset=offset
        )

    async def get_by_id(self, gif_id: str) -> SearchResult:
        for p in self._all_gifs():
            uid = __import__("hashlib").md5(str(p).encode()).hexdigest()[:12]
            if uid == gif_id:
                return SearchResult(
                    items=[self._build_gif(p)], total=1, query=gif_id, provider=self.name
                )
        return SearchResult(items=[], total=0, query=gif_id, provider=self.name)
