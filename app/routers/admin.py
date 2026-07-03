"""Admin panel API + dashboard page.

All /admin/* API routes require an authenticated user whose is_admin flag is
True. The dashboard HTML itself is public, but every data call it makes is
protected, so a non-admin sees nothing.
"""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.auth import BanRequest, MessageResponse, UserResponse
from app.services import bans as ban_service
from app.services import monitoring
from app.services import tokens as token_service

router = APIRouter(prefix="/admin", tags=["admin"])

_DASHBOARD = Path(__file__).resolve().parent.parent / "static" / "admin.html"


# ---------- admin guard ----------
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return current_user


# ---------- dashboard page ----------
@router.get("", response_class=HTMLResponse, include_in_schema=False)
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    if _DASHBOARD.exists():
        return HTMLResponse(_DASHBOARD.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>admin.html not found</h1>", status_code=404)


# ---------- monitoring ----------
@router.get("/stats")
def stats(_: User = Depends(require_admin)):
    return monitoring.system_stats()


@router.get("/health")
def health(_: User = Depends(require_admin)):
    return monitoring.health()


# ---------- users ----------
@router.get("/users")
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    """List users, enriched with live ban status from Redis."""
    users = db.scalars(select(User).order_by(User.id)).all()
    out = []
    for u in users:
        data = UserResponse.model_validate(u).model_dump()
        ban = ban_service.get_ban(u.id)
        data["ban"] = ban  # None if not banned
        out.append(data)
    return out


@router.post("/users/{user_id}/ban", response_model=MessageResponse)
def ban_user(
    user_id: int,
    body: BanRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Ban a user for a custom number of minutes (or permanently) with a reason."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot ban yourself")

    ban_service.ban(user_id, body.reason, body.minutes or None)
    token_service.revoke_all(user_id)  # kill active sessions immediately
    scope = f"{body.minutes} min" if body.minutes else "permanent"
    return MessageResponse(message=f"User {user.username} banned ({scope}).")


@router.post("/users/{user_id}/unban", response_model=MessageResponse)
def unban_user(user_id: int, _: User = Depends(require_admin)):
    ban_service.unban(user_id)
    return MessageResponse(message="User unbanned.")


@router.post("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_active(
    user_id: int, admin: User = Depends(require_admin), db: Session = Depends(get_db)
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot disable yourself")
    user.is_active = not user.is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    if not user.is_active:  # revoke all sessions of a disabled user
        token_service.revoke_all(user.id)
    return user


# ---------- tokens / sessions ----------
@router.get("/tokens")
def list_tokens(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    sessions = token_service.list_all()
    # attach username for readability
    ids = {s["user_id"] for s in sessions}
    names = {}
    if ids:
        for u in db.scalars(select(User).where(User.id.in_(ids))).all():
            names[u.id] = u.username
    for s in sessions:
        s["username"] = names.get(s["user_id"])
    return {"count": len(sessions), "sessions": sessions}


@router.post("/tokens/revoke", response_model=MessageResponse)
def revoke_token(
    user_id: int, jti: str, _: User = Depends(require_admin)
):
    token_service.revoke(user_id, jti)
    return MessageResponse(message="Session revoked.")


@router.post("/users/{user_id}/revoke-all", response_model=MessageResponse)
def revoke_all_sessions(user_id: int, _: User = Depends(require_admin)):
    removed = token_service.revoke_all(user_id)
    return MessageResponse(message=f"Revoked {removed} session(s).")
