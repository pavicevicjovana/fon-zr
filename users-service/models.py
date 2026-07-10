from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Rola(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String, unique=True, nullable=False)  

    korisnici = relationship("Korisnik", back_populates="rola")


class Korisnik(Base):
    __tablename__ = "korisnici"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    lozinka_hash = Column(String, nullable=False)
    ime = Column(String, nullable=False)
    prezime = Column(String, nullable=False)
    broj_telefona = Column(String, nullable=True)
    je_aktivan = Column(Boolean, default=True)
    kreiran = Column(DateTime, default=datetime.utcnow)

    
    rola_id = Column(Integer, ForeignKey("role.id"), nullable=False, default=2)
    rola = relationship("Rola", back_populates="korisnici")

    
    adrese = relationship("KorisnikAdresa", back_populates="korisnik")


class Mesto(Base):
    __tablename__ = "mesta"

    id = Column(Integer, primary_key=True, index=True)
    postanski_broj = Column(String, nullable=False)
    grad = Column(String, nullable=False)
    drzava = Column(String, nullable=False)

    adrese = relationship("Adresa", back_populates="mesto")


class Adresa(Base):
    __tablename__ = "adrese"

    id = Column(Integer, primary_key=True, index=True)
    ulica = Column(String, nullable=False)
    kucni_broj = Column(String, nullable=False)
    sprat = Column(String, nullable=True)

    
    mesto_id = Column(Integer, ForeignKey("mesta.id"), nullable=False)
    mesto = relationship("Mesto", back_populates="adrese")

    korisnici = relationship("KorisnikAdresa", back_populates="adresa")


class KorisnikAdresa(Base):
    """
    Asocijativna klasa iz dokumenta
    Jedan korisnik moze imati vise adresa
    Ista adresa moze biti dodeljena vise korisnika
    """
    __tablename__ = "korisnik_adresa"

    id = Column(Integer, primary_key=True, index=True)
    korisnik_id = Column(Integer, ForeignKey("korisnici.id"), nullable=False)
    adresa_id = Column(Integer, ForeignKey("adrese.id"), nullable=False)
    datum_dodavanja = Column(DateTime, default=datetime.utcnow)
    tip_adrese = Column(String, default="kucna")   # kucna, poslovna
    je_podrazumijevana = Column(Boolean, default=False)

    korisnik = relationship("Korisnik", back_populates="adrese")
    adresa = relationship("Adresa", back_populates="korisnici")

