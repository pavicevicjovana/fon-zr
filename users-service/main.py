import httpx
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from database import get_db, engine, Base
from models import Rola
from auth.controller import router as auth_router
from users.controller import router as users_router
from users.service import get_countries
from log_config import setup_logging, correlation_id_middleware
from tracing import setup_tracing


Base.metadata.create_all(bind=engine)

logger = setup_logging("users-service")

app = FastAPI(title="Users Service")
Instrumentator().instrument(app).expose(app)

setup_tracing("users-service", app)

app.include_router(auth_router)
app.middleware("http")(correlation_id_middleware)
app.include_router(users_router)


@app.on_event("startup")
async def startup():
    db = next(get_db())
    if not db.query(Rola).filter(Rola.naziv == "administrator").first():
        db.add(Rola(naziv="administrator"))
    if not db.query(Rola).filter(Rola.naziv == "korisnik").first():
        db.add(Rola(naziv="korisnik"))
    db.commit()

    try:
        await get_countries()
    except Exception:
        pass


@app.get("/health")
async def health():
    return {"status": "ok", "service": "users-service"}


@app.get("/countries")
async def countries():
    try:
        return await get_countries()
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Ne mogu da učitam listu država")
