import os
import httpx
import pybreaker
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import StavkaKorpe
from repository import CartRepository

PRODUCT_CATALOG_URL = os.getenv("PRODUCT_CATALOG_URL", "http://product-catalog-service:8002")

product_catalog_breaker = pybreaker.CircuitBreaker(
    fail_max=3,  
    reset_timeout=30  
)

def circuit_breaker_async(breaker):
    """
    Dekorator za async funkcije koji koristi pybreaker CircuitBreaker.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await breaker.call_async(func, *args, **kwargs)
            except Exception as e:
                raise e
        return wrapper
    return decorator

class CartService:
    def __init__(self):
        self.repo = CartRepository()


    @circuit_breaker_async(product_catalog_breaker)
    async def _validate_stock(self, proizvod_id: str, velicina: str, boja: str, kolicina: int):
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{PRODUCT_CATALOG_URL}/products/{proizvod_id}")
            if res.status_code == 200:
                product = res.json()
                variant = next(
                    (v for v in product.get("variants", [])
                     if v["size"] == velicina and v["color"] == boja),
                    None
                )
                if variant is None:
                    raise HTTPException(status_code=400, detail="Izabrana varijanta nije dostupna")
                if variant["stock"] < kolicina:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Nema dovoljno na zalihama (dostupno: {variant['stock']} kom)"
                    )
            else:
               
                raise Exception("Product catalog service error")

    async def validate_stock_with_fallback(self, proizvod_id: str, velicina: str, boja: str, kolicina: int):
        try:
            await self._validate_stock(proizvod_id, velicina, boja, kolicina)
        except pybreaker.CircuitBreakerError:
            
            print("Circuit Breaker is OPEN: Skipping stock validation.")
        except HTTPException:
            
            raise
        except Exception as e:
            
            print(f"Stock validation failed, proceeding with fallback: {e}")
            pass

    async def dodaj_stavku(self, db: Session, korisnik_id: int, stavka_data: dict) -> dict:
        # Validacija sa Circuit Breaker zastitom
        await self.validate_stock_with_fallback(
            stavka_data["proizvod_id"],
            stavka_data["velicina"],
            stavka_data["boja"],
            stavka_data["kolicina"]
        )

        korpa = self.repo.get_active_cart(db, korisnik_id)
        if not korpa:
            korpa = self.repo.create_cart(db, korisnik_id)

        stavka = StavkaKorpe(
            korpa_id=korpa.id,
            proizvod_id=stavka_data["proizvod_id"],
            naziv_proizvoda=stavka_data["naziv_proizvoda"],
            velicina=stavka_data["velicina"],
            boja=stavka_data["boja"],
            kolicina=stavka_data["kolicina"],
            cijena_po_komadu=stavka_data["cijena_po_komadu"]
        )
        nova_stavka = self.repo.add_item(db, stavka)

        return {
            "message": "Artikal dodan u korpu",
            "korpa_id": korpa.id,
            "stavka_id": nova_stavka.id
        }

    def get_korpa(self, db: Session, korisnik_id: int) -> dict:
        korpa = self.repo.get_active_cart(db, korisnik_id)
        if not korpa:
            korpa = self.repo.create_cart(db, korisnik_id)
            return {"korpa_id": korpa.id, "korisnik_id": korisnik_id, "stavke": [], "ukupno": 0}

        stavke = []
        ukupno = 0.0
        for s in korpa.stavke:
            stavke.append({
                "stavka_id": s.id,
                "proizvod_id": s.proizvod_id,
                "naziv": s.naziv_proizvoda,
                "velicina": s.velicina,
                "boja": s.boja,
                "kolicina": s.kolicina,
                "cijena_po_komadu": s.cijena_po_komadu,
                "ukupno_stavka": s.kolicina * s.cijena_po_komadu
            })
            ukupno += s.kolicina * s.cijena_po_komadu

        return {"korpa_id": korpa.id, "korisnik_id": korisnik_id, "stavke": stavke, "ukupno": ukupno}

    def izmijeni_kolicinu(self, db: Session, korisnik_id: int, stavka_id: int, kolicina: int) -> dict:
        stavka = self.repo.get_item(db, stavka_id)
        if not stavka:
            raise HTTPException(status_code=404, detail="Stavka nije pronađena")
        # IDOR: verify the item belongs to a cart owned by the requesting user
        korpa = self.repo.get_cart_by_id(db, stavka.korpa_id)
        if not korpa or korpa.korisnik_id != korisnik_id:
            raise HTTPException(status_code=403, detail="Nemate ovlaštenje za izmjenu ove stavke")
        self.repo.update_item_quantity(db, stavka, kolicina)
        return {"message": "Količina ažurirana", "nova_kolicina": kolicina}

    def ukloni_stavku(self, db: Session, korisnik_id: int, stavka_id: int) -> dict:
        stavka = self.repo.get_item(db, stavka_id)
        if not stavka:
            raise HTTPException(status_code=404, detail="Stavka nije pronađena")
        # IDOR: verify the item belongs to a cart owned by the requesting user
        korpa = self.repo.get_cart_by_id(db, stavka.korpa_id)
        if not korpa or korpa.korisnik_id != korisnik_id:
            raise HTTPException(status_code=403, detail="Nemate ovlaštenje za brisanje ove stavke")
        self.repo.delete_item(db, stavka)
        return {"message": "Artikal uklonjen iz korpe"}