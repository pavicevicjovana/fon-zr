from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Korpa(Base):
    __tablename__ = "korpa"

    id = Column(Integer, primary_key=True, index=True)
    korisnik_id = Column(Integer, nullable=False)
    status = Column(String, default="aktivna")  # aktivna, zatvorena
    kreirana = Column(DateTime, default=datetime.utcnow)

    stavke = relationship("StavkaKorpe", back_populates="korpa")


class StavkaKorpe(Base):
    __tablename__ = "stavke_korpe"

    id = Column(Integer, primary_key=True, index=True)
    korpa_id = Column(Integer, ForeignKey("korpa.id"), nullable=False)
    
    
    proizvod_id = Column(String, nullable=False)
    naziv_proizvoda = Column(String, nullable=False)
    velicina = Column(String, nullable=False)
    boja = Column(String, nullable=False)
    kolicina = Column(Integer, nullable=False)
    cijena_po_komadu = Column(Float, nullable=False)

    korpa = relationship("Korpa", back_populates="stavke")


class Narudzba(Base):
    __tablename__ = "narudzbe"

    id = Column(Integer, primary_key=True, index=True)
    korisnik_id = Column(Integer, nullable=False)
    korpa_id = Column(Integer, ForeignKey("korpa.id"), nullable=False)
    ukupan_iznos = Column(Float, nullable=False)
    status = Column(String, default="na_cekanju")  # na_cekanju, placeno, otkazano
    kreirana = Column(DateTime, default=datetime.utcnow)
    adresa_isporuke = Column(String, nullable=False)