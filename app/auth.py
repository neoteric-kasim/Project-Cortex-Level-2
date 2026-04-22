from fastapi import Request, HTTPException
from jose import jwt
import requests
import os

CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")

JWKS = None


def get_jwks():
    global JWKS

    if JWKS:
        return JWKS

    try:
        url = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
        JWKS = requests.get(url).json()
        return JWKS

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"JWKS fetch error: {str(e)}"
        )


# ✅ Validate user token
def get_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        scheme, token = auth_header.split()

        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    # 🔍 Extract token metadata
    try:
        header = jwt.get_unverified_header(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid JWT structure")

    # 🔑 Get JWKS
    jwks = get_jwks()
    keys = jwks.get("keys", [])

    # 🔍 Find matching key
    rsa_key = None
    for key in keys:
        if key.get("kid") == header.get("kid"):
            rsa_key = key
            break

    if not rsa_key:
        raise HTTPException(status_code=401, detail="Matching key not found")

    # 🔐 Decode token
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            options={
                "verify_aud": True,
                "verify_iss": True
            }
        )
        return payload

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token invalid: {str(e)}"
        )