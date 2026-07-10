
from fastapi import HTTPException
from sqlalchemy.orm import Session
from repository import OrderRepository, CartRepository
from producer import posalji_order_completed
import pybreaker



# Circuit Breaker za korisnički servis (primer, proširite po potrebi)
user_service_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30
)

class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()
        self.cart_repo = CartRepository()

    # Primer metode sa circuit breaker-om i fallback-om (proširite po potrebi)
    @user_service_breaker
    async def _call_user_service(self, *args, **kwargs):
        # Primer: ovde bi išao httpx/requests poziv ka users-service
        pass

    async def call_user_service_with_fallback(self, *args, **kwargs):
        try:
            await self._call_user_service(*args, **kwargs)
        except pybreaker.CircuitBreakerError:
            # Fallback logika za korisnički servis
            pass
        except Exception:
            pass

    async def kreiraj_narudzbu(self, db: Session, korisnik_id: int, podaci: dict) -> dict:
        korpa = self.cart_repo.get_active_cart(db, korisnik_id)
        if not korpa:
            raise HTTPException(status_code=404, detail="Aktivna korpa nije pronađena")
        if not korpa.stavke:
            raise HTTPException(status_code=400, detail="Korpa je prazna")

        ukupno = sum(s.kolicina * s.cijena_po_komadu for s in korpa.stavke)

        narudzba = self.order_repo.create(db, korisnik_id, korpa.id, ukupno, podaci["adresa_isporuke"])
        self.cart_repo.close_cart(db, korpa)

        stavke = [
            {
                "product_id": s.proizvod_id,
                "naziv": s.naziv_proizvoda,
                "size": s.velicina,
                "color": s.boja,
                "quantity": s.kolicina,
                "cijena_po_komadu": s.cijena_po_komadu,
                "order_id": narudzba.id
            }
            for s in korpa.stavke
        ]

        await posalji_order_completed(
            narudzba_id=narudzba.id,
            korisnik_id=korisnik_id,
            email=podaci["email"],
            ukupan_iznos=ukupno,
            stavke=stavke,
            user_name=podaci.get("user_name", "Potrosac")
        )

        return {
            "message": "Narudžbina kreirana",
            "narudzba_id": narudzba.id,
            "ukupan_iznos": narudzba.ukupan_iznos,
            "status": narudzba.status
        }

    def get_narudzbe(self, db: Session, korisnik_id: int) -> list:
        narudzbe = self.order_repo.get_by_user(db, korisnik_id)
        if not narudzbe:
            raise HTTPException(status_code=404, detail="Nema narudžbina")
        return [
            {
                "narudzba_id": n.id,
                "ukupan_iznos": n.ukupan_iznos,
                "status": n.status,
                "adresa_isporuke": n.adresa_isporuke,
                "kreirana": n.kreirana
            }
            for n in narudzbe
        ]

    def get_narudzba(self, db: Session, korisnik_id: int, narudzba_id: int) -> dict:
        narudzba = self.order_repo.get_by_id(db, narudzba_id, korisnik_id)
        if not narudzba:
            raise HTTPException(status_code=404, detail="Narudžbina nije pronađena")

        korpa = self.cart_repo.get_cart_by_id(db, narudzba.korpa_id)
        stavke = [
            {
                "naziv": s.naziv_proizvoda,
                "velicina": s.velicina,
                "boja": s.boja,
                "kolicina": s.kolicina,
                "cijena_po_komadu": s.cijena_po_komadu
            }
            for s in korpa.stavke
        ]

        return {
            "narudzba_id": narudzba.id,
            "status": narudzba.status,
            "ukupan_iznos": narudzba.ukupan_iznos,
            "adresa_isporuke": narudzba.adresa_isporuke,
            "kreirana": narudzba.kreirana,
            "stavke": stavke
        }
