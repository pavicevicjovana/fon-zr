from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_db
from token_manager import TokenManager
from producer import posalji_user_registered
from auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


class RegistracijaSchema(BaseModel):
    email: EmailStr
    lozinka: str
    ime: str
    prezime: str
    broj_telefona: Optional[str] = None


class LoginSchema(BaseModel):
    email: EmailStr
    lozinka: str


@router.post("/register", status_code=201)
async def registracija(podaci: RegistracijaSchema, db: Session = Depends(get_db)):
    """
    FZ 2.1 — Kreiranje korisničkog naloga putem email adrese
    FZ 2.2 — Validacija emaila (EmailStr) i lozinke
    """
    service = AuthService(db)
    novi_korisnik = service.register(
        email=podaci.email,
        lozinka=podaci.lozinka,
        ime=podaci.ime,
        prezime=podaci.prezime,
        broj_telefona=podaci.broj_telefona
    )

    await posalji_user_registered(
        korisnik_id=novi_korisnik.id,
        email=novi_korisnik.email,
        ime=novi_korisnik.ime,
        prezime=novi_korisnik.prezime
    )

    return {
        "message": "Korisnik uspješno registrovan",
        "id": novi_korisnik.id,
        "email": novi_korisnik.email,
        "ime": novi_korisnik.ime,
        "prezime": novi_korisnik.prezime
    }


@router.post("/login")
async def login(podaci: LoginSchema, db: Session = Depends(get_db)):
    """
    FZ 3.1 — Bezbjedna prijava korisnika putem kredencijala
    """
    service = AuthService(db)
    korisnik, token = service.login(podaci.email, podaci.lozinka)

    return {
        "access_token": token,
        "token_type": "bearer",
        "korisnik": {
            "id": korisnik.id,
            "email": korisnik.email,
            "ime": korisnik.ime,
            "prezime": korisnik.prezime,
            "rola": korisnik.rola.naziv
        }
    }


@router.get("/validate")
async def validiraj_token(token: str):
    """
    Endpoint koji api-gateway poziva da provjeri JWT token
    """
    payload = TokenManager.dekoduj_token(token)
    return {
        "korisnik_id": payload.get("sub"),
        "email": payload.get("email"),
        "rola": payload.get("rola")
    }
