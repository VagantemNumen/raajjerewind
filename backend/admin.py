import os
import secrets
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from ingest import get_collection

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# In-memory token store. Wiped on backend restart — admins re-log in.
_active_tokens: set[str] = set()

router = APIRouter(prefix="/admin", tags=["admin"])


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str


def _extract_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return authorization.removeprefix("Bearer ").strip()


def verify_token(authorization: str | None = Header(default=None)) -> None:
    if not ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Admin not configured.")
    token = _extract_token(authorization)
    if token not in _active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    if not ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Admin password not configured.")
    if not secrets.compare_digest(req.password, ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid password.")
    token = secrets.token_urlsafe(32)
    _active_tokens.add(token)
    return LoginResponse(token=token)


@router.post("/logout", dependencies=[Depends(verify_token)])
def logout(authorization: str | None = Header(default=None)):
    _active_tokens.discard(_extract_token(authorization))
    return {"ok": True}


@router.get("/documents", dependencies=[Depends(verify_token)])
def list_documents():
    collection = get_collection()
    result = collection.get(include=["metadatas"])
    sources = sorted({m["source"] for m in result["metadatas"] if "source" in m})
    return {"documents": [{"source": s} for s in sources]}


@router.delete("/documents/{source}", dependencies=[Depends(verify_token)])
def delete_document(source: str):
    collection = get_collection()
    collection.delete(where={"source": source})
    return {"ok": True, "source": source}
