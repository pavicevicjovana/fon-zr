from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from database import engine, Base
from cart.controller import router as cart_router
from orders.controller import router as orders_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Service")
Instrumentator().instrument(app).expose(app)

# Internal service: no browser access allowed; all traffic must come through the API Gateway.
# CORSMiddleware is intentionally omitted.

app.include_router(cart_router)
app.include_router(orders_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "orders-service"}
