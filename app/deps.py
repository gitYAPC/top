from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import BASE_DIR
from app.db import SessionLocal, get_db
from app.models import User


def current_user_context(request: Request) -> dict:
    user_id = request.session.get("user_id")
    if not user_id:
        return {"current_user": None}
    with SessionLocal() as db:
        return {"current_user": db.get(User, user_id)}


templates = Jinja2Templates(
    directory=BASE_DIR / "app" / "templates",
    context_processors=[current_user_context],
)


def optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    return db.get(User, user_id) if user_id else None


def require_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    user = db.get(User, user_id) if user_id else None
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user
