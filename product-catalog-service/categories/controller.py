from fastapi import APIRouter
from models import CategoryCreate
from categories.service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])
service = CategoryService()


@router.get("")
async def get_categories():
    return await service.get_all()


@router.post("", status_code=201)
async def create_category(category: CategoryCreate):
    return await service.create(category)
