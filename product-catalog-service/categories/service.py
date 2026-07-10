from models import CategoryCreate
from repository import CategoryRepository


class CategoryService:
    def __init__(self):
        self.repo = CategoryRepository()

    async def get_all(self) -> list:
        return await self.repo.get_all()

    async def create(self, category: CategoryCreate) -> dict:
        return await self.repo.create(category.model_dump())
