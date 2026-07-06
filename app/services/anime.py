import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import anime_source
from app.models import Anime, utcnow

MEMORY_TTL_SECONDS = 30 * 60
DB_TTL_DAYS = 7

_id_cache: dict[str, tuple[float, list[int]]] = {}


def _save(db: Session, items: list[dict]) -> list[Anime]:
    unique = {item["mal_id"]: item for item in items}
    rows = []
    for data in unique.values():
        anime = db.scalar(select(Anime).where(Anime.mal_id == data["mal_id"]))
        if anime:
            for key, value in data.items():
                setattr(anime, key, value)
            anime.cached_at = utcnow()
        else:
            anime = Anime(**data)
            db.add(anime)
        rows.append(anime)
    db.commit()
    return rows


def _by_ids(db: Session, ids: list[int]) -> list[Anime]:
    rows = db.scalars(select(Anime).where(Anime.id.in_(ids))).all()
    order = {id_: pos for pos, id_ in enumerate(ids)}
    return sorted(rows, key=lambda a: order[a.id])


async def _cached_list(db: Session, key: str, fetch) -> list[Anime]:
    entry = _id_cache.get(key)
    if entry and time.time() - entry[0] < MEMORY_TTL_SECONDS:
        return _by_ids(db, entry[1])
    try:
        items = await fetch()
    except Exception:
        return []
    rows = _save(db, items)
    _id_cache[key] = (time.time(), [a.id for a in rows])
    return rows


async def search(db: Session, query: str) -> list[Anime]:
    query = query.strip()
    return await _cached_list(db, f"q:{query.lower()}", lambda: anime_source.search(query))


async def get_top(db: Session, page: int = 1) -> list[Anime]:
    return await _cached_list(db, f"top:{page}", lambda: anime_source.top(page))


def _is_fresh(cached_at: datetime) -> bool:
    if cached_at.tzinfo is None:
        cached_at = cached_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - cached_at < timedelta(days=DB_TTL_DAYS)


async def get_details(db: Session, mal_id: int) -> Anime | None:
    anime = db.scalar(select(Anime).where(Anime.mal_id == mal_id))
    if anime and _is_fresh(anime.cached_at):
        return anime
    try:
        data = await anime_source.get_details(mal_id)
    except Exception:
        return anime
    return _save(db, [data])[0]
