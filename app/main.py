from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.config import BASE_DIR, SECRET_KEY
from app.deps import templates
from app.routes import auth, lists, pages, top

app = FastAPI(title="AnimeList")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(lists.router)
app.include_router(top.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(request, "404.html", status_code=404)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code, headers=exc.headers)
