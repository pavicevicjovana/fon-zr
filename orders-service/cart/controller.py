from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from cart.service import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])
service = CartService()


class StavkaSchema(BaseModel):
    proizvod_id: str
    naziv_proizvoda: str
    velicina: str
    boja: str
    kolicina: int
    cijena_po_komadu: float


@router.post("/{korisnik_id}/items", status_code=201)
async def dodaj_u_korpu(korisnik_id: int, stavka: StavkaSchema, db: Session = Depends(get_db)):
    return await service.dodaj_stavku(db, korisnik_id, stavka.model_dump())


@router.get("/{korisnik_id}")
async def get_korpa(korisnik_id: int, db: Session = Depends(get_db)):
    return service.get_korpa(db, korisnik_id)


@router.put("/{korisnik_id}/items/{stavka_id}")
async def izmijeni_kolicinu(korisnik_id: int, stavka_id: int, kolicina: int, db: Session = Depends(get_db)):
    return service.izmijeni_kolicinu(db, korisnik_id, stavka_id, kolicina)


@router.delete("/{korisnik_id}/items/{stavka_id}")
async def ukloni_iz_korpe(korisnik_id: int, stavka_id: int, db: Session = Depends(get_db)):
    return service.ukloni_stavku(db, korisnik_id, stavka_id)
