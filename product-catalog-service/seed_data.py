import os
import sys
from pymongo import MongoClient


MONGO_URI = os.getenv("MONGODB_URL", "mongodb://catalog_admin:catalog_password123@localhost:27017/velura_catalog?authSource=admin")

try:
    client = MongoClient(MONGO_URI)
    db = client.velura_catalog
    collection = db.products

    def variants(sizes, colors, stock=10):
        result = []
        for i, size in enumerate(sizes):
            for j, color in enumerate(colors):
                result.append({
                    "size": size,
                    "color": color,
                    "sku": f"SKU-{i}{j}",
                    "stock": stock
                })
        return result

    dummy_products = [
        {"name": "Letnja haljina", "description": "Lagana letnja haljina od pamuka.", "price": 2500, "category": "Odeca", "collection": "Leto", "images": [], "is_active": True, "variants": variants(["XS","S","M","L"], ["Bijela","Roza"])},
        {"name": "Farmerke plave", "description": "Klasične plave farmerke slim fit.", "price": 3500, "category": "Odeca", "collection": "Osnovna", "images": [], "is_active": True, "variants": variants(["S","M","L","XL"], ["Plava"])},
        {"name": "Zimska jakna", "description": "Topla zimska jakna s postavom.", "price": 8000, "category": "Odeca", "collection": "Zima", "images": [], "is_active": True, "variants": variants(["M","L","XL"], ["Crna","Siva"])},
        {"name": "Patike sportske", "description": "Udobne sportske patike za svaki dan.", "price": 5000, "category": "Obuca", "collection": "Sport", "images": [], "is_active": True, "variants": variants(["38","39","40","41","42","43"], ["Bijela","Crna"])},
        {"name": "Kožna jakna", "description": "Elegantna jakna od prave kože.", "price": 9500, "category": "Odeca", "collection": "Premium", "images": [], "is_active": True, "variants": variants(["S","M","L"], ["Crna","Smeđa"])},
        {"name": "Bela majica", "description": "Klasična bijela majica od 100% pamuka.", "price": 800, "category": "Odeca", "collection": "Osnovna", "images": [], "is_active": True, "variants": variants(["XS","S","M","L","XL"], ["Bijela"])},
        {"name": "Crne čizme", "description": "Elegantne kožne čizme do koljena.", "price": 6000, "category": "Obuca", "collection": "Jesen", "images": [], "is_active": True, "variants": variants(["37","38","39","40","41"], ["Crna"])},
        {"name": "Duks sa kapuljačom", "description": "Topli duks sa kapuljačom od flisa.", "price": 2200, "category": "Odeca", "collection": "Osnovna", "images": [], "is_active": True, "variants": variants(["S","M","L","XL"], ["Siva","Crna","Plava"])},
        {"name": "Elegantne cipele", "description": "Muške elegantne cipele za posebne prilike.", "price": 7500, "category": "Obuca", "collection": "Premium", "images": [], "is_active": True, "variants": variants(["40","41","42","43","44"], ["Crna","Smeđa"])},
        {"name": "Šorts za plažu", "description": "Lagani šorts za plažu i slobodno vrijeme.", "price": 1200, "category": "Odeca", "collection": "Leto", "images": [], "is_active": True, "variants": variants(["S","M","L","XL"], ["Plava","Zelena","Narančasta"])},
        {"name": "Vuneni džemper", "description": "Topli vuneni džemper za hladne dane.", "price": 3200, "category": "Odeca", "collection": "Zima", "images": [], "is_active": True, "variants": variants(["S","M","L"], ["Bež","Siva","Bordo"])},
        {"name": "Sandale kožne", "description": "Udobne kožne sandale za ljeto.", "price": 4000, "category": "Obuca", "collection": "Leto", "images": [], "is_active": True, "variants": variants(["36","37","38","39","40"], ["Smeđa","Bijela"])},
        {"name": "Trenerka komplet", "description": "Komplet trenerka gornji i donji dio.", "price": 4500, "category": "Odeca", "collection": "Sport", "images": [], "is_active": True, "variants": variants(["S","M","L","XL"], ["Crna","Siva"])},
        {"name": "Kaiš kožni", "description": "Kožni kaiš s metalnom kopčom.", "price": 1500, "category": "Dodaci", "collection": "Osnovna", "images": [], "is_active": True, "variants": [{"size": "Univerzalna", "color": "Crna", "sku": "SKU-K1", "stock": 20}, {"size": "Univerzalna", "color": "Smeđa", "sku": "SKU-K2", "stock": 20}]},
        {"name": "Kapa vunena", "description": "Topla vunena kapa za zimu.", "price": 900, "category": "Dodaci", "collection": "Zima", "images": [], "is_active": True, "variants": [{"size": "Univerzalna", "color": "Crna", "sku": "SKU-KP1", "stock": 30}, {"size": "Univerzalna", "color": "Siva", "sku": "SKU-KP2", "stock": 30}]},
        {"name": "Rukavice kožne", "description": "Tople kožne rukavice podstavljene.", "price": 2000, "category": "Dodaci", "collection": "Zima", "images": [], "is_active": True, "variants": [{"size": "S/M", "color": "Crna", "sku": "SKU-R1", "stock": 15}, {"size": "L/XL", "color": "Crna", "sku": "SKU-R2", "stock": 15}]},
        {"name": "Pantalone chino", "description": "Elegantne chino pantalone za sve prilike.", "price": 3800, "category": "Odeca", "collection": "Osnovna", "images": [], "is_active": True, "variants": variants(["S","M","L","XL"], ["Bež","Maslinasta","Teget"])},
        {"name": "Majica polo", "description": "Klasična polo majica s kragnom.", "price": 1800, "category": "Odeca", "collection": "Osnovna", "images": [], "is_active": True, "variants": variants(["S","M","L","XL"], ["Bijela","Teget","Bordo"])},
        {"name": "Baletanke", "description": "Lagane baletanke za svaki dan.", "price": 2800, "category": "Obuca", "collection": "Osnovna", "images": [], "is_active": True, "variants": variants(["36","37","38","39","40"], ["Crna","Bež","Roza"])},
        {"name": "Jakna vetrovka", "description": "Lagana vjetrovka otporna na kišu.", "price": 4200, "category": "Odeca", "collection": "Jesen", "images": [], "is_active": True, "variants": variants(["S","M","L","XL"], ["Crna","Plava","Zelena"])},
    ]

    
    collection.delete_many({})
    collection.insert_many(dummy_products)
    print(f"Uspešno dodato {len(dummy_products)} proizvoda u bazu!")
except Exception as e:
    print(f"Greška pri seedovanju MongoDB: {e}")
    sys.exit(1)