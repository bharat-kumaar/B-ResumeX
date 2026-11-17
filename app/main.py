from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.core.db import create_db_and_tables
from app.api import auth, analyze, dashboard, tools

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="RESUMATE AI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(tools.router, prefix="/api/tools", tags=["Tools"])

from fastapi import Depends
from app.core.deps import get_current_user_optional
from app.models.domain import User

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, user: User | None = Depends(get_current_user_optional)):
    return templates.TemplateResponse(request, "index.html", {"user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")

@app.get("/logout")
async def logout_redirect():
    from fastapi.responses import RedirectResponse
    res = RedirectResponse(url="/login")
    res.delete_cookie(key="resumate_token", path="/")
    return res

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user: User | None = Depends(get_current_user_optional)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "dashboard.html", {"user": user})

@app.get("/dashboard/{analysis_id}", response_class=HTMLResponse)
async def report_page(request: Request, analysis_id: str, user: User | None = Depends(get_current_user_optional)):
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "report.html", {"user": user, "analysis_id": analysis_id})
