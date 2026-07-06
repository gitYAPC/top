import re

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"])
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,30}$")


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def register(db: Session, username: str, password: str) -> tuple[User | None, str | None]:
    if not USERNAME_RE.match(username):
        return None, "Имя: 3–30 символов, только латиница, цифры и _"
    if len(password) < 6:
        return None, "Пароль: минимум 6 символов"
    if get_by_username(db, username):
        return None, "Это имя уже занято"
    user = User(username=username, password_hash=pwd_context.hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, None


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = get_by_username(db, username)
    if user and pwd_context.verify(password, user.password_hash):
        return user
    return None


def update_profile(db: Session, user: User, bio: str, avatar_url: str) -> User:
    user.bio = bio.strip() or None
    user.avatar_url = avatar_url.strip() or None
    db.commit()
    db.refresh(user)
    return user
