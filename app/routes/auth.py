from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_user, templates
from app.models import User
from app.services import auth, profile

router = APIRouter()


@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.post("/register")
def register(request: Request, username: str = Form(""), password: str = Form(""), db: Session = Depends(get_db)):
    user, error = auth.register(db, username.strip(), password)
    if error:
        return templates.TemplateResponse(request, "register.html", {"error": error, "username": username})
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
def login(request: Request, username: str = Form(""), password: str = Form(""), db: Session = Depends(get_db)):
    user = auth.authenticate(db, username.strip(), password)
    if not user:
        return templates.TemplateResponse(request, "login.html", {"error": "Неверное имя или пароль", "username": username})
    request.session["user_id"] = user.id
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/me")
def me(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "me.html", {**profile.get_profile(db, user.username), "own": True})


@router.post("/me")
def me_update(request: Request, bio: str = Form(""), avatar_url: str = Form(""), user: User = Depends(require_user), db: Session = Depends(get_db)):
    auth.update_profile(db, user, bio, avatar_url)
    return templates.TemplateResponse(request, "me.html", {**profile.get_profile(db, user.username), "own": True, "saved": True})
