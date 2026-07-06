from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Anime, Rating, User


def get_top_items(db: Session, user_id: int) -> list[Rating]:
    return db.scalars(
        select(Rating)
        .where(Rating.user_id == user_id, Rating.top_position.is_not(None))
        .options(joinedload(Rating.anime))
        .order_by(Rating.top_position)
    ).all()


def add_to_top(db: Session, user: User, anime: Anime) -> Rating | None:
    rating = db.get(Rating, (user.id, anime.id))
    if not rating:
        return None
    if rating.top_position is None:
        max_position = db.scalar(select(func.max(Rating.top_position)).where(Rating.user_id == user.id))
        rating.top_position = (max_position or 0) + 1
        db.commit()
    return rating


def remove_from_top(db: Session, user: User, anime: Anime) -> Rating | None:
    rating = db.get(Rating, (user.id, anime.id))
    if not rating:
        return None
    rating.top_position = None
    db.flush()
    for position, item in enumerate(get_top_items(db, user.id), start=1):
        item.top_position = position
    db.commit()
    return rating


def toggle_top(db: Session, user: User, anime: Anime) -> tuple[Rating | None, str]:
    rating = db.get(Rating, (user.id, anime.id))
    if not rating:
        return None, ""
    if rating.top_position is None:
        return add_to_top(db, user, anime), "Добавлено в топ"
    return remove_from_top(db, user, anime), "Убрано из топа"


def reorder_top(db: Session, user: User, anime_ids: list[int]) -> bool:
    ratings = {r.anime_id: r for r in get_top_items(db, user.id)}
    if len(anime_ids) != len(ratings) or set(anime_ids) != set(ratings):
        return False
    for position, anime_id in enumerate(anime_ids, start=1):
        ratings[anime_id].top_position = position
    db.commit()
    return True
