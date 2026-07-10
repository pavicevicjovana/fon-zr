import os
import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Adresa, KorisnikAdresa
from repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def get_profil(self, korisnik_id: int):
        korisnik = self.repo.get_by_id(korisnik_id)
        if not korisnik:
            raise HTTPException(status_code=404, detail="Korisnik nije pronađen")
        return korisnik

    def update_profil(self, korisnik_id: int, ime=None, prezime=None, broj_telefona=None):
        korisnik = self.repo.get_by_id(korisnik_id)
        if not korisnik:
            raise HTTPException(status_code=404, detail="Korisnik nije pronađen")
        if ime is not None:
            korisnik.ime = ime
        if prezime is not None:
            korisnik.prezime = prezime
        if broj_telefona is not None:
            korisnik.broj_telefona = broj_telefona
        return self.repo.update_user(korisnik)

    def get_all_users(self):
        return self.repo.get_all()

    def get_adrese(self, korisnik_id: int):
        korisnik = self.repo.get_by_id(korisnik_id)
        if not korisnik:
            raise HTTPException(status_code=404, detail="Korisnik nije pronađen")

        rezultat = []
        for ka in korisnik.adrese:
            rezultat.append({
                "adresa_id": ka.adresa.id,
                "ulica": ka.adresa.ulica,
                "kucni_broj": ka.adresa.kucni_broj,
                "sprat": ka.adresa.sprat,
                "grad": ka.adresa.mesto.grad,
                "postanski_broj": ka.adresa.mesto.postanski_broj,
                "drzava": ka.adresa.mesto.drzava,
                "tip_adrese": ka.tip_adrese,
                "je_podrazumijevana": ka.je_podrazumijevana
            })
        return rezultat

    async def dodaj_adresu(
        self,
        korisnik_id: int,
        ulica: str,
        kucni_broj: str,
        sprat,
        postanski_broj: str,
        grad: str,
        drzava: str,
        tip_adrese: str = "kucna",
        je_podrazumijevana: bool = False
    ):
        korisnik = self.repo.get_by_id(korisnik_id)
        if not korisnik:
            raise HTTPException(status_code=404, detail="Korisnik nije pronađen")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{os.getenv('REST_COUNTRIES_URL')}/name/{drzava}",
                    timeout=5.0
                )
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Država '{drzava}' nije validna")
            except httpx.TimeoutException:
                pass

        mesto = self.repo.get_or_create_mesto(postanski_broj, grad, drzava)

        nova_adresa = Adresa(
            ulica=ulica,
            kucni_broj=kucni_broj,
            sprat=sprat,
            mesto_id=mesto.id
        )
        nova_adresa = self.repo.add_address(nova_adresa)

        korisnik_adresa = KorisnikAdresa(
            korisnik_id=korisnik_id,
            adresa_id=nova_adresa.id,
            tip_adrese=tip_adrese,
            je_podrazumijevana=je_podrazumijevana
        )
        self.repo.add_korisnik_adresa(korisnik_adresa)

        return {
            "message": "Adresa uspješno dodana",
            "adresa_id": nova_adresa.id,
            "ulica": nova_adresa.ulica,
            "kucni_broj": nova_adresa.kucni_broj,
            "grad": mesto.grad,
            "drzava": mesto.drzava
        }

    def set_default_address(self, korisnik_id: int, adresa_id: int):
        ka = self.repo.set_default_address(korisnik_id, adresa_id)
        if not ka:
            raise HTTPException(status_code=404, detail="Adresa nije pronađena")
        return {"message": "Adresa postavljena kao podrazumijevana"}

    def obrisi_adresu(self, korisnik_id: int, adresa_id: int):
        ka = self.repo.delete_korisnik_adresa(korisnik_id, adresa_id)
        if not ka:
            raise HTTPException(status_code=404, detail="Adresa nije pronađena")
        return {"message": "Adresa uspješno obrisana"}
