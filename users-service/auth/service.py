from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import Korisnik
from repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def _hash_lozinku(self, lozinka: str) -> str:
        return pwd_context.hash(lozinka)

    def _provjeri_lozinku(self, lozinka: str, hash: str) -> bool:
        return pwd_context.verify(lozinka, hash)

    def register(
        self,
        email: str,
        lozinka: str,
        ime: str,
        prezime: str,
        broj_telefona: str = None
    ) -> Korisnik:
        if self.repo.get_by_email(email):
            raise HTTPException(status_code=400, detail="Email već postoji")

        if len(lozinka) < 8:
            raise HTTPException(status_code=400, detail="Lozinka mora imati najmanje 8 karaktera")

        rola = self.repo.get_role("korisnik")

        novi_korisnik = Korisnik(
            email=email,
            lozinka_hash=self._hash_lozinku(lozinka),
            ime=ime,
            prezime=prezime,
            broj_telefona=broj_telefona,
            rola_id=rola.id
        )
        return self.repo.create_user(novi_korisnik)

    def login(self, email: str, lozinka: str):
        korisnik = self.repo.get_by_email(email)

        if not korisnik or not self._provjeri_lozinku(lozinka, korisnik.lozinka_hash):
            raise HTTPException(status_code=401, detail="Pogrešan email ili lozinka")

        if not korisnik.je_aktivan:
            raise HTTPException(status_code=403, detail="Nalog je deaktiviran")

        from token_manager import TokenManager
        token = TokenManager.kreiraj_token({
            "sub": str(korisnik.id),
            "email": korisnik.email,
            "rola": korisnik.rola.naziv
        })

        return korisnik, token
