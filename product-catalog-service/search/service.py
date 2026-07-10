from typing import Optional
from repository import ProductRepository


class SearchService:
    def __init__(self):
        self.repo = ProductRepository()

    async def search(
        self,
        q: Optional[str],
        category: Optional[str],
        collection: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
    ) -> list:
        query: dict = {"is_active": True}

        if q:
            query["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
            ]

        if category:
            query["category"] = {"$regex": category, "$options": "i"}

        if collection:
            query["collection"] = {"$regex": collection, "$options": "i"}

        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price

        return await self.repo.search(query)
