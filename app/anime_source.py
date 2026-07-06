import asyncio
import time

import httpx

BASE_URL = "https://api.jikan.moe/v4"
MIN_INTERVAL_SECONDS = 0.5
MAX_RETRIES = 4
TIMEOUT_SECONDS = 15
PAGE_LIMIT = 25

_lock = asyncio.Lock()
_last_request_at = 0.0


def _normalize(item: dict) -> dict:
    images = item.get("images") or {}
    picture = images.get("webp") or images.get("jpg") or {}
    return {
        "mal_id": item["mal_id"],
        "title": item.get("title") or "",
        "title_english": item.get("title_english"),
        "poster_url": picture.get("large_image_url") or picture.get("image_url"),
        "episodes": item.get("episodes"),
        "year": item.get("year"),
        "synopsis": item.get("synopsis"),
        "score_mal": item.get("score"),
    }


async def _get(path: str, params: dict | None = None) -> dict | list:
    global _last_request_at
    async with _lock:
        for attempt in range(MAX_RETRIES):
            delay = _last_request_at + MIN_INTERVAL_SECONDS - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.get(f"{BASE_URL}{path}", params=params)
            _last_request_at = time.monotonic()
            if response.status_code == 429 or response.status_code >= 500:
                await asyncio.sleep(2**attempt)
                continue
            response.raise_for_status()
            return response.json()["data"]
    raise RuntimeError(f"Jikan: retries exhausted, last status {response.status_code}")


async def search(query: str) -> list[dict]:
    data = await _get("/anime", {"q": query, "limit": PAGE_LIMIT, "sfw": "true"})
    return [_normalize(item) for item in data]


async def get_details(mal_id: int) -> dict:
    data = await _get(f"/anime/{mal_id}")
    return _normalize(data)


async def top() -> list[dict]:
    data = await _get("/top/anime", {"limit": PAGE_LIMIT})
    return [_normalize(item) for item in data]
