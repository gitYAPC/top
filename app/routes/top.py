import json

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_user, templates
from app.models import User
from app.services import lists, top

router = APIRouter()


@router.post("/me/top/{mal_id}/toggle")
def toggle_top(request: Request, mal_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    anime = lists.get_anime(db, mal_id)
    if not anime:
        raise HTTPException(status_code=404)
    rating, toast = top.toggle_top(db, user, anime)
    if not rating:
        raise HTTPException(status_code=400)
    context = {"item": rating, "anime": anime, "top_items": top.get_top_items(db, user.id), "own": True, "oob": True}
    return templates.TemplateResponse(request, "_top_toggle_response.html", context,
                                      headers={"HX-Trigger": json.dumps({"toast": toast})})


@router.post("/me/top/reorder")
def reorder_top(anime_ids: list[int] = Body(...), user: User = Depends(require_user), db: Session = Depends(get_db)):
    if not top.reorder_top(db, user, anime_ids):
        raise HTTPException(status_code=400)
    return Response(status_code=204)
