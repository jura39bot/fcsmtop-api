from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from api.database import init_db
from api.routers import national, clubs
from api.schemas import HealthOut

APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="fcsmtop-api",
    description=(
        "API REST pour les statistiques du Championnat National de football français "
        "avec focus sur le FC Sochaux-Montbéliard (FCSM).\n\n"
        "Repo : https://github.com/jura39bot/fcsmtop-api"
    ),
    version=APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(national.router)
app.include_router(clubs.router)

# Servir le frontend statique
web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.isdir(web_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(web_dir, "static")), name="static")

    @app.get("/", include_in_schema=False)
    async def root():
        return FileResponse(os.path.join(web_dir, "index.html"))

    @app.get("/fcsm", include_in_schema=False)
    async def fcsm_page():
        return FileResponse(os.path.join(web_dir, "fcsm.html"))


@app.get("/health", response_model=HealthOut, tags=["Système"])
async def health():
    """État de l'API."""
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fcsmtop.db")
    db_type = "postgresql" if "postgresql" in db_url else "sqlite"
    return HealthOut(status="ok", version=APP_VERSION, db=db_type)
