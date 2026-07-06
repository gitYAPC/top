from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import optional_user, templates
from app.models import User
from app.services import anime as anime_service
from app.services import lists, profile

router = APIRouter()


def _feed_context(anime_list: list, page: int) -> dict:
    return {"anime_list": anime_list, "feed": True, "page": page, "has_more": len(anime_list) == 25}


@router.get("/")
async def index(request: Request, db: Session = Depends(get_db)):
    anime_list = await anime_service.get_top(db)
    return templates.TemplateResponse(request, "index.html", _feed_context(anime_list, 1))


@router.get("/feed")
async def feed(request: Request, page: int = 1, db: Session = Depends(get_db)):
    anime_list = await anime_service.get_top(db, page)
    return templates.TemplateResponse(request, "_feed_page.html", _feed_context(anime_list, page))


@router.get("/search")
async def search(request: Request, q: str = "", db: Session = Depends(get_db)):
    template = "_grid.html" if request.headers.get("HX-Request") else "search.html"
    if q.strip():
        return templates.TemplateResponse(request, template, {"anime_list": await anime_service.search(db, q), "q": q})
    return templates.TemplateResponse(request, template, {**_feed_context(await anime_service.get_top(db), 1), "q": q})


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
