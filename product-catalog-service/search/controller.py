from fastapi import APIRouter, Query
from typing import Optional
from search.service import SearchService

router = APIRouter(prefix="/products", tags=["Search"])
service = SearchService()


@router.get("/search")
async def search_products(
    q: Optional[str] = Query(None, description="Kljucna rijec za pretragu"),
    category: Optional[str] = Query(None, description="Filtriranje po kategoriji"),
    collection: Optional[str] = Query(None, description="Filtriranje po kolekciji"),
    min_price: Optional[float] = Query(None, description="Minimalna cijena"),
    max_price: Optional[float] = Query(None, description="Maksimalna cijena"),
):
    return await service.search(q, category, collection, min_price, max_price)
