import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow():
    return datetime.now(timezone.utc)


class WatchStatus(enum.Enum):
    watching = "watching"
    completed = "completed"
    planned = "planned"
    dropped = "dropped"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    ratings: Mapped[list["Rating"]] = relationship(back_populates="user")


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(primary_key=True)
    mal_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    title_english: Mapped[str | None] = mapped_column(String(255))
    poster_url: Mapped[str | None] = mapped_column(String(500))
    episodes: Mapped[int | None] = mapped_column(Integer)
    year: Mapped[int | None] = mapped_column(Integer)
    synopsis: Mapped[str | None] = mapped_column(Text)
    score_mal: Mapped[float | None] = mapped_column(Float)
    cached_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    ratings: Mapped[list["Rating"]] = relationship(back_populates="anime")


class Rating(Base):
    __tablename__ = "ratings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.id"), primary_key=True)
    status: Mapped[WatchStatus] = mapped_column(Enum(WatchStatus))
    score: Mapped[int | None] = mapped_column(Integer)
    top_position: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    user: Mapped["User"] = relationship(back_populates="ratings")
    anime: Mapped["Anime"] = relationship(back_populates="ratings")
