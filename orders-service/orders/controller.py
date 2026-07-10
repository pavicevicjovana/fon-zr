from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])
service = OrderService()


class NarudzbaSchema(BaseModel):
    adresa_isporuke: str
    email: str
    user_name: str = "Potrosac"


@router.post("/{korisnik_id}", status_code=201)
async def kreiraj_narudzbu(korisnik_id: int, podaci: NarudzbaSchema, db: Session = Depends(get_db)):
    return await service.kreiraj_narudzbu(db, korisnik_id, podaci.model_dump())


@router.get("/{korisnik_id}")
async def get_narudzbe(korisnik_id: int, db: Session = Depends(get_db)):
    return service.get_narudzbe(db, korisnik_id)


@router.get("/{korisnik_id}/{narudzba_id}")
async def get_narudzba(korisnik_id: int, narudzba_id: int, db: Session = Depends(get_db)):
    return service.get_narudzba(db, korisnik_id, narudzba_id)
