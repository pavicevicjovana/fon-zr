import os
import sys
from database import SessionLocal, engine, Base
from models import Korisnik, Rola
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    try:
        db = SessionLocal()

        if not db.query(Rola).filter(Rola.naziv == "administrator").first():
            db.add(Rola(naziv="administrator"))
        if not db.query(Rola).filter(Rola.naziv == "korisnik").first():
            db.add(Rola(naziv="korisnik"))
        db.commit()

        admin_rola = db.query(Rola).filter(Rola.naziv == "administrator").first()
        korisnik_rola = db.query(Rola).filter(Rola.naziv == "korisnik").first()

        users = [
            {"email": "admin@velura.com", "ime": "Velura", "prezime": "Admin", "rola_id": admin_rola.id},
        ]
        
        for i in range(1, 10):
            users.append({
                "email": f"kupac{i}@velura.com",
                "ime": f"Kupac",
                "prezime": f"Broj{i}",
                "rola_id": korisnik_rola.id
            })
        
        for u in users:
            if not db.query(Korisnik).filter(Korisnik.email == u["email"]).first():
                novi = Korisnik(
                    email=u["email"],
                    lozinka_hash=pwd_context.hash("lozinka123"),
                    ime=u["ime"],
                    prezime=u["prezime"],
                    rola_id=u["rola_id"]
                )
                db.add(novi)
        
        db.commit()
        db.close()
        print("Baza uspešno naseljena sa 1 adminom i 9 korisnika.")
    except Exception as e:
        print(f"Greška pri seedovanju PostgreSQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    seed()