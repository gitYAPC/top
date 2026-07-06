from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Anime, Rating, User, WatchStatus
from app.services.auth import get_by_username
from app.services.lists import STATUS_LABELS


def list_users(db: Session) -> list[tuple[User, int]]:
    rows = db.execute(
        select(User, func.count(Rating.anime_id))
        .outerjoin(Rating, Rating.user_id == User.id)
        .group_by(User.id)
        .order_by(func.count(Rating.anime_id).desc(), User.username)
    ).all()
    return [(user, count) for user, count in rows]


def get_profile(db: Session, username: str) -> dict | None:
    user = get_by_username(db, username)
    if not user:
        return None
    items = db.scalars(
        select(Rating)
        .where(Rating.user_id == user.id)
        .options(joinedload(Rating.anime))
        .order_by(Rating.updated_at.desc())
    ).all()
    top_items = sorted((i for i in items if i.top_position is not None), key=lambda i: i.top_position)
    return {"profile_user": user, "items": items, "top_items": top_items,
            "stats": _stats(db, user.id), "statuses": STATUS_LABELS}


def _stats(db: Session, user_id: int) -> dict:
    counts = dict(
        db.execute(
            select(Rating.status, func.count()).where(Rating.user_id == user_id).group_by(Rating.status)
        ).all()
    )
    avg_score = db.scalar(select(func.avg(Rating.score)).where(Rating.user_id == user_id))
    episodes = db.scalar(
        select(func.coalesce(func.sum(Anime.episodes), 0))
        .join(Rating, Rating.anime_id == Anime.id)
        .where(Rating.user_id == user_id, Rating.status == WatchStatus.completed)
    )
    return {"total": sum(counts.values()), "counts": counts, "avg_score": avg_score, "episodes": episodes}
