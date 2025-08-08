from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from jose import jwk
from jose.utils import base64url_decode
import httpx
import json
import time
from app.core.config import settings

JWKS_CACHE: Optional[dict] = None
JWKS_TS: float = 0.0

async def get_jwks() -> dict:
    global JWKS_CACHE, JWKS_TS
    now = time.time()
    if JWKS_CACHE and now - JWKS_TS < 60:
        return JWKS_CACHE
    if not settings.SUPABASE_URL:
        raise HTTPException(status_code=500, detail="SUPABASE_URL not configured")
    jwks_url = settings.SUPABASE_URL.rstrip('/') + "/auth/v1/keys"
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(jwks_url)
        r.raise_for_status()
        JWKS_CACHE = r.json()
        JWKS_TS = now
        return JWKS_CACHE

def _verify_jwt_signature(token: str, jwks: dict) -> dict:
    header_b64, payload_b64, signature_b64 = token.split('.')
    header = json.loads(base64url_decode(header_b64.encode()).decode())
    payload = json.loads(base64url_decode(payload_b64.encode()).decode())
    kid = header.get('kid')
    keys = jwks.get('keys', [])
    key = next((k for k in keys if k.get('kid') == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token key")
    public_key = jwk.construct(key)
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = base64url_decode(signature_b64.encode())
    if not public_key.verify(signing_input, signature):
        raise HTTPException(status_code=401, detail="Invalid token signature")
    return payload

async def supabase_user_from_bearer(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(' ', 1)[1]
    jwks = await get_jwks()
    payload = _verify_jwt_signature(token, jwks)
    return payload

async def require_admin_api_token(
    x_admin_api_token: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
) -> None:
    expected = (getattr(settings, 'ADMIN_API_TOKEN', None) or '').strip()
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_API_TOKEN is not configured")
    bearer = None
    if authorization and authorization.startswith('Bearer '):
        bearer = authorization.split(' ', 1)[1]
    provided = x_admin_api_token or bearer or ''
    if provided != expected:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return None


