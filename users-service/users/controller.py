from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from dependencies import verify_admin_token
from users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


class ProfilUpdateSchema(BaseModel):
    ime: Optional[str] = None
    prezime: Optional[str] = None
    broj_telefona: Optional[str] = None


class MestoSchema(BaseModel):
    postanski_broj: str
    grad: str
    drzava: str


class AdresaSchema(BaseModel):
    ulica: str
    kucni_broj: str
    sprat: Optional[str] = None
    mesto: MestoSchema
    tip_adrese: Optional[str] = "kucna"
    je_podrazumijevana: Optional[bool] = False


@router.get("")
async def get_all_users(
    db: Session = Depends(get_db),
    payload: dict = Depends(verify_admin_token)
):
    """
    FZ — Lista svih korisnika (samo administrator)
    """
    service = UserService(db)
    korisnici = service.get_all_users()
    return [
        {
            "id": k.id,
            "email": k.email,
            "ime": k.ime,
            "prezime": k.prezime,
            "broj_telefona": k.broj_telefona,
            "rola": k.rola.naziv,
            "je_aktivan": k.je_aktivan,
            "kreiran": k.kreiran
        }
        for k in korisnici
    ]


@router.get("/{korisnik_id}")
async def get_profil(korisnik_id: int, db: Session = Depends(get_db)):
    """
    FZ 3.2 — Pristup ličnom profilu nakon uspješne prijave
    """
    service = UserService(db)
    korisnik = service.get_profil(korisnik_id)
    return {
        "id": korisnik.id,
        "email": korisnik.email,
        "ime": korisnik.ime,
        "prezime": korisnik.prezime,
        "broj_telefona": korisnik.broj_telefona,
        "rola": korisnik.rola.naziv,
        "kreiran": korisnik.kreiran
    }


@router.put("/{korisnik_id}")
async def update_profil(
    korisnik_id: int,
    podaci: ProfilUpdateSchema,
    db: Session = Depends(get_db)
):
    service = UserService(db)
    korisnik = service.update_profil(
        korisnik_id,
        ime=podaci.ime,
        prezime=podaci.prezime,
        broj_telefona=podaci.broj_telefona
    )
    return {
        "id": korisnik.id,
        "email": korisnik.email,
        "ime": korisnik.ime,
        "prezime": korisnik.prezime,
        "broj_telefona": korisnik.broj_telefona,
        "rola": korisnik.rola.naziv
    }


@router.post("/{korisnik_id}/adrese", status_code=201)
async def dodaj_adresu(
    korisnik_id: int,
    adresa: AdresaSchema,
    db: Session = Depends(get_db)
):
    """
    Dodavanje adrese isporuke korisniku
    Koristi REST Countries API za validaciju države — eksterni API
    """
    service = UserService(db)
    return await service.dodaj_adresu(
        korisnik_id=korisnik_id,
        ulica=adresa.ulica,
        kucni_broj=adresa.kucni_broj,
        sprat=adresa.sprat,
        postanski_broj=adresa.mesto.postanski_broj,
        grad=adresa.mesto.grad,
        drzava=adresa.mesto.drzava,
        tip_adrese=adresa.tip_adrese,
        je_podrazumijevana=adresa.je_podrazumijevana
    )


@router.get("/{korisnik_id}/adrese")
async def get_adrese(korisnik_id: int, db: Session = Depends(get_db)):
    """Vraća sve adrese korisnika"""
    service = UserService(db)
    return service.get_adrese(korisnik_id)


@router.put("/{korisnik_id}/adrese/{adresa_id}/podrazumijevana")
async def set_default_address(
    korisnik_id: int,
    adresa_id: int,
    db: Session = Depends(get_db)
):
    service = UserService(db)
    return service.set_default_address(korisnik_id, adresa_id)


@router.delete("/{korisnik_id}/adrese/{adresa_id}")
async def obrisi_adresu(
    korisnik_id: int,
    adresa_id: int,
    db: Session = Depends(get_db)
):
    service = UserService(db)
    return service.obrisi_adresu(korisnik_id, adresa_id)
