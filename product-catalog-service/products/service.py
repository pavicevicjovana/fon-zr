from fastapi import HTTPException
from bson.errors import InvalidId
from models import ProductCreate, ProductUpdate
from repository import ProductRepository


class ProductService:
    def __init__(self):
        self.repo = ProductRepository()

    async def get_all(self, include_inactive: bool, skip: int, limit: int) -> list:
        return await self.repo.get_all(include_inactive, skip, limit)

    async def get_by_id(self, product_id: str) -> dict:
        try:
            product = await self.repo.get_by_id(product_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Nevalidan ID proizvoda")
        if not product:
            raise HTTPException(status_code=404, detail="Proizvod nije pronađen")
        return product

    async def create(self, product: ProductCreate) -> dict:
        return await self.repo.create(product.model_dump())

    async def update(self, product_id: str, product: ProductUpdate) -> dict:
        data = {k: v for k, v in product.model_dump().items() if v is not None}
        try:
            updated = await self.repo.update(product_id, data)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Nevalidan ID proizvoda")
        if updated is None:
            raise HTTPException(status_code=404, detail="Proizvod nije pronađen")
        return updated

    async def deactivate(self, product_id: str) -> dict:
        try:
            found = await self.repo.deactivate(product_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Nevalidan ID proizvoda")
        if not found:
            raise HTTPException(status_code=404, detail="Proizvod nije pronađen")
        return {"message": "Proizvod uspješno deaktiviran"}
