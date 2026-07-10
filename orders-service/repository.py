from sqlalchemy.orm import Session
from models import Korpa, StavkaKorpe, Narudzba


class CartRepository:
    def get_active_cart(self, db: Session, korisnik_id: int) -> Korpa | None:
        return db.query(Korpa).filter(
            Korpa.korisnik_id == korisnik_id,
            Korpa.status == "aktivna"
        ).first()

    def create_cart(self, db: Session, korisnik_id: int) -> Korpa:
        korpa = Korpa(korisnik_id=korisnik_id)
        db.add(korpa)
        db.commit()
        db.refresh(korpa)
        return korpa

    def add_item(self, db: Session, item: StavkaKorpe) -> StavkaKorpe:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def get_item(self, db: Session, stavka_id: int) -> StavkaKorpe | None:
        return db.query(StavkaKorpe).filter(StavkaKorpe.id == stavka_id).first()

    def update_item_quantity(self, db: Session, stavka: StavkaKorpe, kolicina: int) -> StavkaKorpe:
        stavka.kolicina = kolicina
        db.commit()
        return stavka

    def delete_item(self, db: Session, stavka: StavkaKorpe) -> None:
        db.delete(stavka)
        db.commit()

    def close_cart(self, db: Session, korpa: Korpa) -> None:
        korpa.status = "zatvorena"
        db.commit()

    def get_cart_by_id(self, db: Session, korpa_id: int) -> Korpa | None:
        return db.query(Korpa).filter(Korpa.id == korpa_id).first()


class OrderRepository:
    def create(self, db: Session, korisnik_id: int, korpa_id: int,
                ukupan_iznos: float, adresa_isporuke: str) -> Narudzba:
        narudzba = Narudzba(
            korisnik_id=korisnik_id,
            korpa_id=korpa_id,
            ukupan_iznos=ukupan_iznos,
            adresa_isporuke=adresa_isporuke
        )
        db.add(narudzba)
        db.commit()
        db.refresh(narudzba)
        return narudzba

    def get_by_user(self, db: Session, korisnik_id: int) -> list[Narudzba]:
        return db.query(Narudzba).filter(Narudzba.korisnik_id == korisnik_id).all()

    def get_by_id(self, db: Session, narudzba_id: int, korisnik_id: int) -> Narudzba | None:
        return db.query(Narudzba).filter(
            Narudzba.id == narudzba_id,
            Narudzba.korisnik_id == korisnik_id
        ).first()
