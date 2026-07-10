from database import SessionLocal, engine, Base
from models import Korpa, StavkaKorpe, Narudzba
import random
from datetime import datetime

Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Provjeri da li već ima podataka
    if db.query(Narudzba).first():
        print("Baza već sadrži podatke. Preskačem seedovanje.")
        db.close()
        return

    print("Počinjem sa seedovanjem 10 narudžbi...")

    for i in range(1, 11):
        
        korpa = Korpa(korisnik_id=i, status="zatvorena")
        db.add(korpa)
        db.flush()  # Da dobijemo korpa.id

        
        cijena = random.uniform(20.0, 150.0)
        stavka = StavkaKorpe(
            korpa_id=korpa.id,
            proizvod_id=f"prod_{random.randint(100, 999)}",
            naziv_proizvoda=f"Proizvod {i}",
            velicina="M",
            boja="Plava",
            kolicina=random.randint(1, 3),
            cijena_po_komadu=cijena
        )
        db.add(stavka)
        
        
        narudzba = Narudzba(
            korisnik_id=i,
            korpa_id=korpa.id,
            ukupan_iznos=cijena * stavka.kolicina,
            adresa_isporuke=f"Ulica dummy broja {i}, Grad",
            status="na_cekanju"
        )
        db.add(narudzba)
    
    db.commit()
    db.close()
    print("Seedovanje završeno uspješno!")

if __name__ == "__main__":
    seed_data()