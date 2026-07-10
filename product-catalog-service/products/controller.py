from fastapi import APIRouter, Query
from models import ProductCreate, ProductUpdate
from products.service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])
service = ProductService()


@router.get("")
async def get_all_products(
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(0, ge=0),
):
    return await service.get_all(include_inactive, skip, limit)


@router.get("/{product_id}")
async def get_product(product_id: str):
    return await service.get_by_id(product_id)


@router.post("", status_code=201)
async def create_product(product: ProductCreate):
    return await service.create(product)


@router.put("/{product_id}")
async def update_product(product_id: str, product: ProductUpdate):
    return await service.update(product_id, product)


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    return await service.deactivate(product_id)
