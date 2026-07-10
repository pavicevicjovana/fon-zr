from database import products_collection, categories_collection
from bson import ObjectId
from datetime import datetime


def serialize_product(product: dict) -> dict:
    product["id"] = str(product["_id"])
    del product["_id"]
    return product


def serialize_category(category: dict) -> dict:
    category["id"] = str(category["_id"])
    del category["_id"]
    return category


class ProductRepository:
    async def get_all(self, include_inactive: bool = False, skip: int = 0, limit: int = 0) -> list:
        query = {} if include_inactive else {"is_active": True}
        cursor = products_collection.find(query).skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)
        products = []
        async for product in cursor:
            products.append(serialize_product(product))
        return products

    async def get_by_id(self, product_id: str) -> dict | None:
        product = await products_collection.find_one({"_id": ObjectId(product_id)})
        if product:
            return serialize_product(product)
        return None

    async def create(self, data: dict) -> dict:
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        result = await products_collection.insert_one(data)
        created = await products_collection.find_one({"_id": result.inserted_id})
        return serialize_product(created)

    async def update(self, product_id: str, data: dict) -> dict | None:
        oid = ObjectId(product_id)
        data["updated_at"] = datetime.utcnow()
        result = await products_collection.update_one({"_id": oid}, {"$set": data})
        if result.matched_count == 0:
            return None
        updated = await products_collection.find_one({"_id": oid})
        return serialize_product(updated)

    async def deactivate(self, product_id: str) -> bool:
        oid = ObjectId(product_id)
        result = await products_collection.update_one(
            {"_id": oid},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.matched_count > 0

    async def search(self, query: dict) -> list:
        products = []
        async for product in products_collection.find(query):
            products.append(serialize_product(product))
        return products


class CategoryRepository:
    async def get_all(self) -> list:
        categories = []
        async for category in categories_collection.find():
            categories.append(serialize_category(category))
        return categories

    async def create(self, data: dict) -> dict:
        data["created_at"] = datetime.utcnow()
        result = await categories_collection.insert_one(data)
        created = await categories_collection.find_one({"_id": result.inserted_id})
        return serialize_category(created)
