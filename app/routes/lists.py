import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_user, templates
from app.models import User, WatchStatus
from app.services import lists

router = APIRouter()


def _controls(request: Request, anime, rating, toast: str):
    return templates.TemplateResponse(
        request,
        "_status_controls.html",
        {"anime": anime, "rating": rating, "statuses": lists.STATUS_LABELS},
        headers={"HX-Trigger": json.dumps({"toast": toast})},
    )


def _get_anime(db: Session, mal_id: int):
    anime = lists.get_anime(db, mal_id)
    if not anime:
        raise HTTPException(status_code=404)
    return anime


@router.post("/anime/{mal_id}/status")
def set_status(request: Request, mal_id: int, status: str = Form(...), user: User = Depends(require_user), db: Session = Depends(get_db)):
    try:
        parsed = WatchStatus(status)
    except ValueError:
        raise HTTPException(status_code=400)
    anime = _get_anime(db, mal_id)
    rating, toast = lists.set_status(db, user, anime, parsed)
    return _controls(request, anime, rating, toast)


@router.post("/anime/{mal_id}/score")
def set_score(request: Request, mal_id: int, score: int = Form(...), user: User = Depends(require_user), db: Session = Depends(get_db)):
    if not 1 <= score <= 10:
        raise HTTPException(status_code=400)
    anime = _get_anime(db, mal_id)
    rating, toast = lists.set_score(db, user, anime, score)
    return _controls(request, anime, rating, toast)
