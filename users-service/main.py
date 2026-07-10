from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from database import get_db, engine, Base
from models import Rola
from auth.controller import router as auth_router
from users.controller import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users Service")
Instrumentator().instrument(app).expose(app)

# Internal service: no browser access allowed; all traffic must come through the API Gateway.
# CORSMiddleware is intentionally omitted.

app.include_router(auth_router)
app.include_router(users_router)


@app.on_event("startup")
async def startup():
    db = next(get_db())
    if not db.query(Rola).filter(Rola.naziv == "administrator").first():
        db.add(Rola(naziv="administrator"))
    if not db.query(Rola).filter(Rola.naziv == "korisnik").first():
        db.add(Rola(naziv="korisnik"))
    db.commit()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "users-service"}
