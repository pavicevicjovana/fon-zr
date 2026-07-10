from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from token_manager import TokenManager

security = HTTPBearer()


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = TokenManager.dekoduj_token(credentials.credentials)
    if payload.get("rola") != "administrator":
        raise HTTPException(status_code=403, detail="Pristup dozvoljen samo administratorima")
    return payload
