# Velura Online Prodavnica Odjeće

Mikroservisna aplikacija za online prodaju odjeće razvijena u okviru predmeta Razvoj naprednih aplikacija za e-poslovanje.

## Arhitektura

Aplikacija je izgrađena po **mikroservisnoj arhitekturi** sa **Database per Service** principom i **Saga pattern** komunikacijom putem Apache Kafke.


## Servisi

| Servis | Port | Baza | Opis |
|--------|------|------|------|
| api-gateway | 8000 | — | Jedina ulazna tačka, rutira zahtjeve i validira JWT |
| users-service | 8001 | PostgreSQL | Registracija, login, profil, adrese |
| product-catalog-service | 8002 | MongoDB | Proizvodi, kategorije, pretraga |
| orders-service | 8003 | PostgreSQL | Korpa, narudžbine, plaćanje |
| notifications-service | — | — | Email obavještenja putem Brevo API |
| frontend | 3000 | — | React/Vite korisnički interfejs |

## Kafka Flow (Saga Pattern)

```
orders-service  →  topic: order_completed  →  product-catalog-service (smanjuje zalihe)
                                           →  notifications-service (šalje email potvrde)

product-catalog →  topic: refund_order     →  orders-service (otkazuje narudžbinu)
                                           →  notifications-service (šalje email o refundu)
```
## Circuit Breaker patern

U okviru orders-service mikroservisa implementiran je Circuit Breaker patern kako bi se osigurala otpornost na greške pri komunikaciji sa product-catalog-service. 

Koriscen je pybreaker za upravljanje stanjima prekidača.Ukoliko se desi 3 uzastopna neuspeha (greške u mreži, timeout ili 500 status kod), prekidač se otvara.

Dok je prekidač otvoren, servis ne pokušava ponovo poziv ka katalogu u narednih 30 sekundi (reset timeout), već automatski izvršava fallback logiku.

cart/service.py: Ovde se nalazi instanca product_catalog_breaker i definisana fallback logika u metodi validate_stock_with_fallback.

Implementirani su automatizovani testovi koji verifikuju ponašanje Circuit Breaker-a u slučaju kvara spoljnog servisa, gde Test tests/test_circuit_breaker.py simulira pad product-catalog-service, sa komandom pokretanja testa:
                  pytest tests/test_circuit_breaker.py
## Pokretanje

### Preduslovi
- Docker
- Docker Compose

### Pokretanje svih servisa

```bash
docker-compose up --build
```

### Pokretanje pojedinih servisa

```bash
docker-compose up zookeeper kafka postgres-orders orders-service
docker-compose up mongodb product-catalog-service
docker-compose up postgres-users users-service
```

## API Dokumentacija

Nakon pokretanja, Swagger UI je dostupan na:

- API Gateway: http://localhost:8000/docs
- Users Service: http://localhost:8001/docs
- Product Catalog: http://localhost:8002/docs
- Orders Service: http://localhost:8003/docs

## Eksterni API-ji

- **REST Countries API** — validacija države pri unosu adrese isporuke
- **Brevo API** — slanje email obavještenja korisnicima

## Akteri

- **Neregistrovani korisnik** — pregled i pretraga proizvoda
- **Registrovani korisnik** — upravljanje korpom, narudžbine, praćenje statusa
- **Administrator** — upravljanje katalogom proizvoda (dodavanje, izmjena, brisanje)

## Tehnologije

- **Backend:** Python, FastAPI, SQLAlchemy, Motor (async MongoDB)
- **Message Broker:** Apache Kafka + Zookeeper
- **Baze podataka:** PostgreSQL, MongoDB
- **Frontend:** React, Vite
- **Infrastruktura:** Docker, Docker Compose
