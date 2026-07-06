from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import optional_user, templates
from app.models import User
from app.services import anime as anime_service
from app.services import lists, profile

router = APIRouter()


@router.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    anime_list = await anime_service.get_top(db)
    return templates.TemplateResponse(request, "index.html", {"anime_list": anime_list})


@router.get("/search")
async def search(request: Request, q: str = "", db: Session = Depends(get_db)):
    anime_list = await anime_service.search(db, q) if q.strip() else await anime_service.get_top(db)
    template = "_grid.html" if request.headers.get("HX-Request") else "search.html"
    return templates.TemplateResponse(request, template, {"anime_list": anime_list, "q": q})


@router.get("/anime/{mal_id}")
async def anime_detail(request: Request, mal_id: int, user: User | None = Depends(optional_user), db: Session = Depends(get_db)):
    anime = await anime_service.get_details(db, mal_id)
    if not anime:
        raise HTTPException(status_code=404)
    rating = lists.get_rating(db, user.id, anime.id) if user else None
    return templates.TemplateResponse(request, "anime.html", {"anime": anime, "rating": rating, "statuses": lists.STATUS_LABELS})


@router.get("/users")
def users_index(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "users.html", {"users": profile.list_users(db)})


@router.get("/user/{username}")
def user_profile(request: Request, username: str, db: Session = Depends(get_db)):
    data = profile.get_profile(db, username)
    if not data:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "profile.html", data)
