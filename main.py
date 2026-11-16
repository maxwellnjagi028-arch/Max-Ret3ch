from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import init_db
from app.routes import (
    auth_routes,
    ted_routes,
    proposals_routes,
    leads_routes,
    services_routes,
    tickets_routes,
    ewaste_routes,
    education_routes,
    admin_routes
)

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & seed on startup
    init_db()
    yield

app = FastAPI(
    title="MaxReT3ch AI",
    description="Next-Generation AI Solutions, High-Performance Computing & Sustainable Tech",
    version="2.4.0",
    lifespan=lifespan
)

# Mount Static Files
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include API Routers
app.include_router(auth_routes.router)
app.include_router(ted_routes.router)
app.include_router(proposals_routes.router)
app.include_router(leads_routes.router)
app.include_router(services_routes.router)
app.include_router(tickets_routes.router)
app.include_router(ewaste_routes.router)
app.include_router(education_routes.router)
app.include_router(admin_routes.router)

# Page Routes (using modern Starlette signature: request, name, context)
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/ted", response_class=HTMLResponse)
async def ted_cockpit_page(request: Request):
    return templates.TemplateResponse(request=request, name="ted.html")

@app.get("/services", response_class=HTMLResponse)
async def services_page(request: Request):
    return templates.TemplateResponse(request=request, name="services.html")

@app.get("/hardware", response_class=HTMLResponse)
async def hardware_page(request: Request):
    return templates.TemplateResponse(request=request, name="hardware.html")

@app.get("/green-tech", response_class=HTMLResponse)
async def ewaste_page(request: Request):
    return templates.TemplateResponse(request=request, name="ewaste.html")

@app.get("/education", response_class=HTMLResponse)
async def education_page(request: Request):
    return templates.TemplateResponse(request=request, name="education.html")

@app.get("/proposal/{quote_number}", response_class=HTMLResponse)
async def proposal_page(request: Request, quote_number: str):
    return templates.TemplateResponse(request=request, name="proposal_view.html", context={"quote_number": quote_number})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/portal", response_class=HTMLResponse)
async def client_portal_page(request: Request):
    return templates.TemplateResponse(request=request, name="client_portal.html")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")
