from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from search.controller import router as search_router
from products.controller import router as products_router
from categories.controller import router as categories_router

app = FastAPI(title="Product Catalog Service")
Instrumentator().instrument(app).expose(app)

# Internal service: no browser access allowed; all traffic must come through the API Gateway.
# CORSMiddleware is intentionally omitted.

app.include_router(search_router)
app.include_router(products_router)
app.include_router(categories_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "product-catalog-service"}
