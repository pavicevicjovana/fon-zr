from sqlalchemy.orm import Session
from models import Korisnik, Rola, Adresa, Mesto, KorisnikAdresa


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(Korisnik).filter(Korisnik.email == email).first()

    def get_by_id(self, id: int):
        return self.db.query(Korisnik).filter(Korisnik.id == id).first()

    def get_all(self):
        return self.db.query(Korisnik).all()

    def get_role(self, naziv: str):
        return self.db.query(Rola).filter(Rola.naziv == naziv).first()

    def create_user(self, korisnik: Korisnik) -> Korisnik:
        self.db.add(korisnik)
        self.db.commit()
        self.db.refresh(korisnik)
        return korisnik

    def update_user(self, korisnik: Korisnik) -> Korisnik:
        self.db.commit()
        self.db.refresh(korisnik)
        return korisnik

    def get_or_create_mesto(self, postanski_broj: str, grad: str, drzava: str) -> Mesto:
        mesto = self.db.query(Mesto).filter(
            Mesto.grad == grad,
            Mesto.drzava == drzava
        ).first()
        if not mesto:
            mesto = Mesto(
                postanski_broj=postanski_broj,
                grad=grad,
                drzava=drzava
            )
            self.db.add(mesto)
            self.db.commit()
            self.db.refresh(mesto)
        return mesto

    def add_address(self, adresa: Adresa) -> Adresa:
        self.db.add(adresa)
        self.db.commit()
        self.db.refresh(adresa)
        return adresa

    def add_korisnik_adresa(self, ka: KorisnikAdresa) -> KorisnikAdresa:
        self.db.add(ka)
        self.db.commit()
        return ka

    def get_korisnik_adresa(self, korisnik_id: int, adresa_id: int):
        return self.db.query(KorisnikAdresa).filter(
            KorisnikAdresa.korisnik_id == korisnik_id,
            KorisnikAdresa.adresa_id == adresa_id
        ).first()

    def set_default_address(self, korisnik_id: int, adresa_id: int):
        self.db.query(KorisnikAdresa).filter(
            KorisnikAdresa.korisnik_id == korisnik_id
        ).update({"je_podrazumijevana": False})
        ka = self.get_korisnik_adresa(korisnik_id, adresa_id)
        if ka:
            ka.je_podrazumijevana = True
            self.db.commit()
        return ka

    def delete_korisnik_adresa(self, korisnik_id: int, adresa_id: int):
        ka = self.get_korisnik_adresa(korisnik_id, adresa_id)
        if ka:
            self.db.delete(ka)
            self.db.commit()
        return ka
