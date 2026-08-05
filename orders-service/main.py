from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from database import engine, Base
from cart.controller import router as cart_router
from orders.controller import router as orders_router
from log_config import setup_logging, correlation_id_middleware
from tracing import setup_tracing

logger = setup_logging("orders-service")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Orders Service")
app.middleware("http")(correlation_id_middleware)
Instrumentator().instrument(app).expose(app)

setup_tracing("orders-service", app)

app.include_router(cart_router)
app.include_router(orders_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "orders-service"}

@app.get("/blockchain/status")
async def blockchain_status():
    """Stanje blokcejn mreze i statistika revizijskog traga (samo za administratore)."""
    from producer import blockchain
    return await blockchain.get_statistics()