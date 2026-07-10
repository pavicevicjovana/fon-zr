import os
import bleach
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional, List
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter

http_errors_total = Counter(
    "http_errors_total",
    "Ukupan broj HTTP gresaka (4xx + 5xx) po statusu, metodi i ruti",
    ["status_code", "method", "handler"]
)

load_dotenv()

app = FastAPI(title="Velura API Gateway")
Instrumentator().instrument(app).expose(app)

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL")
PRODUCT_CATALOG_URL = os.getenv("PRODUCT_CATALOG_URL")
ORDERS_SERVICE_URL = os.getenv("ORDERS_SERVICE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

security = HTTPBearer()
csrf_serializer = URLSafeTimedSerializer(SECRET_KEY)

# Paths excluded from CSRF validation (public/infrastructure endpoints)
CSRF_EXEMPT_PATHS = {
    "/health", "/metrics", "/api/csrf-token",
    "/docs", "/openapi.json", "/redoc",
    "/api/users/register", "/api/users/login",
}


def sanitize(value: str) -> str:
    """Strip all HTML tags from a string to prevent XSS injection."""
    return bleach.clean(value, tags=[], attributes={}, strip=True)


# --- XSS: Security response headers middleware ---
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "object-src 'none'; "
        "base-uri 'self'"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# --- Metrics: Count 4xx/5xx responses for Grafana error panel ---
@app.middleware("http")
async def count_errors_middleware(request: Request, call_next):
    response = await call_next(request)
    if response.status_code >= 400:
        http_errors_total.labels(
            status_code=str(response.status_code),
            method=request.method,
            handler=request.url.path
        ).inc()
    return response


# --- CSRF: Validate signed token for all state-changing requests ---
@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        if request.url.path not in CSRF_EXEMPT_PATHS:
            csrf_token = request.headers.get("X-CSRF-Token")
            if not csrf_token:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token nedostaje"}
                )
            try:
                csrf_serializer.loads(csrf_token, salt="csrf-token", max_age=3600)
            except SignatureExpired:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token je istekao. Osvježite stranicu."}
                )
            except (BadSignature, Exception):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Nevažeći CSRF token"}
                )
    return await call_next(request)


# --- CORS: Restrict to the frontend origin with explicit allowed headers ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    allow_credentials=True,
    expose_headers=["X-CSRF-Token"]
)


# --- XSS: Base model that sanitizes all string inputs before validation ---
class SanitizedModel(BaseModel):
    """Strips HTML tags from every string field to prevent stored/reflected XSS."""

    @model_validator(mode="before")
    @classmethod
    def sanitize_strings(cls, data):
        if not isinstance(data, dict):
            return data
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and key != "lozinka":
                result[key] = sanitize(value)
            elif isinstance(value, list):
                result[key] = [
                    sanitize(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result


class RegisterRequest(SanitizedModel):
    ime: str
    prezime: str
    email: EmailStr
    lozinka: str


class LoginRequest(SanitizedModel):
    email: EmailStr
    lozinka: str


class ProfilUpdateRequest(SanitizedModel):
    ime: Optional[str] = None
    prezime: Optional[str] = None
    broj_telefona: Optional[str] = None


class MestoRequest(SanitizedModel):
    postanski_broj: str
    grad: str
    drzava: str


class AdresaRequest(SanitizedModel):
    ulica: str
    kucni_broj: str
    sprat: Optional[str] = None
    mesto: MestoRequest
    tip_adrese: Optional[str] = "kucna"
    je_podrazumijevana: Optional[bool] = False


class VariantRequest(SanitizedModel):
    size: str
    color: str
    sku: Optional[str] = None
    stock: int = 0


class ProductCreateRequest(SanitizedModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    collection: Optional[str] = None
    images: Optional[List[str]] = []
    variants: Optional[List[VariantRequest]] = []
    is_active: Optional[bool] = True


class ProductUpdateRequest(SanitizedModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    collection: Optional[str] = None
    images: Optional[List[str]] = None
    variants: Optional[List[VariantRequest]] = None
    is_active: Optional[bool] = None


class CartItemRequest(SanitizedModel):
    proizvod_id: str
    naziv_proizvoda: str
    velicina: str
    boja: str
    kolicina: int = 1
    cijena_po_komadu: float


class OrderRequest(SanitizedModel):
    adresa_isporuke: str
    email: str
    user_name: Optional[str] = "Potrosac"


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Nevazeci token")


def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials)
    if payload.get("rola") != "administrator":
        raise HTTPException(status_code=403, detail="Pristup dozvoljen samo administratorima")
    return payload


# --- IDOR: Verify the token owner matches the requested resource ID ---
def verify_owner_or_admin(korisnik_id: int, payload: dict):
    token_user_id = payload.get("sub")
    if token_user_id is None:
        raise HTTPException(status_code=401, detail="Nevazeci token")
    try:
        if int(token_user_id) != korisnik_id and payload.get("rola") != "administrator":
            raise HTTPException(status_code=403, detail="Nemate pristup ovom resursu")
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Nevazeci token")


def proxied(response: httpx.Response) -> JSONResponse:
    return JSONResponse(content=response.json(), status_code=response.status_code)


async def forward_request(url: str, method: str, headers: dict, body: bytes = None):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
        return response
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Mikroservis nije odgovorio na vreme")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Mikroservis nije dostupan")


# --- CSRF: Token generation endpoint ---
@app.get("/api/csrf-token")
async def get_csrf_token():
    """
    Issues a signed CSRF token valid for 1 hour.
    The frontend must include it as the X-CSRF-Token header on all
    state-changing requests (POST, PUT, DELETE, PATCH).
    """
    token = csrf_serializer.dumps("csrf", salt="csrf-token")
    return {"csrf_token": token}


@app.post("/api/users/register")
async def register(data: RegisterRequest):
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/auth/register",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=data.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.post("/api/users/login")
async def login(data: LoginRequest):
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/auth/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=data.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.get("/api/users/{korisnik_id}")
async def get_profile(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.post("/api/users/{korisnik_id}/adrese")
async def dodaj_adresu(korisnik_id: int, adresa: AdresaRequest, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}/adrese",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=adresa.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.get("/api/users/{korisnik_id}/adrese")
async def get_adrese(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}/adrese",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/api/products")
async def get_products(request: Request):
    query = str(request.query_params)
    url = f"{PRODUCT_CATALOG_URL}/products"
    if query:
        url += f"?{query}"
    response = await forward_request(url=url, method="GET", headers={})
    return proxied(response)


@app.get("/api/products/search")
async def search_products(request: Request):
    query = str(request.query_params)
    url = f"{PRODUCT_CATALOG_URL}/products/search"
    if query:
        url += f"?{query}"
    response = await forward_request(url=url, method="GET", headers={})
    return proxied(response)


@app.get("/api/products/{product_id}")
async def get_product(product_id: str, request: Request):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="GET",
        headers={}
    )
    return proxied(response)


@app.get("/api/categories")
async def get_categories(request: Request):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/categories",
        method="GET",
        headers={}
    )
    return proxied(response)


@app.post("/api/products")
async def create_product(data: ProductCreateRequest, request: Request, payload: dict = Depends(verify_admin)):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=data.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.put("/api/products/{product_id}")
async def update_product(product_id: str, data: ProductUpdateRequest, request: Request, payload: dict = Depends(verify_admin)):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="PUT",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=data.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, request: Request, payload: dict = Depends(verify_admin)):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products/{product_id}",
        method="DELETE",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/api/cart/{korisnik_id}")
async def get_cart(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{korisnik_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.post("/api/cart/{korisnik_id}/items")
async def add_to_cart(korisnik_id: int, data: CartItemRequest, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{korisnik_id}/items",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=data.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.delete("/api/cart/{korisnik_id}/items/{stavka_id}")
async def remove_from_cart(korisnik_id: int, stavka_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{korisnik_id}/items/{stavka_id}",
        method="DELETE",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.post("/api/orders/{korisnik_id}")
async def create_order(korisnik_id: int, data: OrderRequest, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders/{korisnik_id}",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": request.headers.get("Authorization")
        },
        body=data.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.get("/api/orders/{korisnik_id}")
async def get_orders(korisnik_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders/{korisnik_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/api/orders/{korisnik_id}/{narudzba_id}")
async def get_order(korisnik_id: int, narudzba_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/orders/{korisnik_id}/{narudzba_id}",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.put("/api/users/{korisnik_id}")
async def update_profile(korisnik_id: int, data: ProfilUpdateRequest, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}",
        method="PUT",
        headers={"Content-Type": "application/json", "Authorization": request.headers.get("Authorization")},
        body=data.model_dump_json().encode("utf-8")
    )
    return proxied(response)


@app.delete("/api/users/{korisnik_id}/adrese/{adresa_id}")
async def delete_address(korisnik_id: int, adresa_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}/adrese/{adresa_id}",
        method="DELETE",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.put("/api/users/{korisnik_id}/adrese/{adresa_id}/podrazumijevana")
async def set_default_address(korisnik_id: int, adresa_id: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users/{korisnik_id}/adrese/{adresa_id}/podrazumijevana",
        method="PUT",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.put("/api/cart/{korisnik_id}/items/{stavka_id}")
async def update_cart_item(korisnik_id: int, stavka_id: int, kolicina: int, request: Request, payload: dict = Depends(verify_token)):
    verify_owner_or_admin(korisnik_id, payload)
    response = await forward_request(
        url=f"{ORDERS_SERVICE_URL}/cart/{korisnik_id}/items/{stavka_id}?kolicina={kolicina}",
        method="PUT",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)


@app.get("/api/admin/products")
async def admin_get_all_products(request: Request, payload: dict = Depends(verify_admin)):
    response = await forward_request(
        url=f"{PRODUCT_CATALOG_URL}/products?include_inactive=true",
        method="GET",
        headers={}
    )
    return proxied(response)


@app.get("/api/users")
async def get_all_users(request: Request, payload: dict = Depends(verify_admin)):
    response = await forward_request(
        url=f"{USERS_SERVICE_URL}/users",
        method="GET",
        headers={"Authorization": request.headers.get("Authorization")}
    )
    return proxied(response)
