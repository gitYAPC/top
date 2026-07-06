from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Anime, Rating, User, WatchStatus

STATUS_LABELS = {
    WatchStatus.watching: "Смотрю",
    WatchStatus.completed: "Просмотрено",
    WatchStatus.planned: "В планах",
    WatchStatus.dropped: "Брошено",
}


def get_anime(db: Session, mal_id: int) -> Anime | None:
    return db.scalar(select(Anime).where(Anime.mal_id == mal_id))


def get_rating(db: Session, user_id: int, anime_id: int) -> Rating | None:
    return db.get(Rating, (user_id, anime_id))


def set_status(db: Session, user: User, anime: Anime, status: WatchStatus) -> tuple[Rating | None, str]:
    rating = get_rating(db, user.id, anime.id)
    if rating and rating.status == status:
        db.delete(rating)
        db.commit()
        return None, "Убрано из списка"
    if rating:
        rating.status = status
    else:
        rating = Rating(user_id=user.id, anime_id=anime.id, status=status)
        db.add(rating)
    db.commit()
    return rating, STATUS_LABELS[status]


def set_score(db: Session, user: User, anime: Anime, score: int) -> tuple[Rating | None, str]:
    rating = get_rating(db, user.id, anime.id)
    if not rating:
        return None, "Сначала добавьте в список"
    if rating.score == score:
        rating.score = None
        db.commit()
        return rating, "Оценка убрана"
    rating.score = score
    db.commit()
    return rating, f"Оценка: {score}/10"
