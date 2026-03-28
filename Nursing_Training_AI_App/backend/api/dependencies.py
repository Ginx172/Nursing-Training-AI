"""
FastAPI dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.database import get_db
from core.auth import verify_token
from models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependinta FastAPI care extrage si valideaza utilizatorul curent din JWT token.
    Verifica si blacklist-ul de token-uri (logout).
    """
    token = credentials.credentials

    # Verificare blacklist (token-uri invalidate prin logout)
    from api.routes.auth import _blacklisted_tokens, _blacklist_lock, _hash_token
    token_hash = _hash_token(token)
    with _blacklist_lock:
        if token_hash in _blacklisted_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

    payload = verify_token(token, expected_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Verifica ca utilizatorul este activ"""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return user


async def get_current_admin(user: User = Depends(get_current_active_user)) -> User:
    """Verifica ca utilizatorul este admin (backward compatible)"""
    if user.role.value not in ("admin",):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def require_permission(permission):
    """Factory dependency: verifica permisiunea RBAC pe baza rolului userului.

    Utilizare:
        @router.get("/endpoint")
        async def handler(user: User = Depends(require_permission(Permission.ADMIN_USERS))):
            ...
    """
    from core.rbac import check_user_permission

    async def _check(user: User = Depends(get_current_active_user)) -> User:
        if not check_user_permission(user.role.value, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required",
            )
        return user

    return _check


def require_any_permissions(*permissions):
    """Factory dependency: verifica oricare din permisiunile listate."""
    from core.rbac import check_user_permission

    async def _check(user: User = Depends(get_current_active_user)) -> User:
        for perm in permissions:
            if check_user_permission(user.role.value, perm):
                return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: insufficient privileges",
        )

    return _check
