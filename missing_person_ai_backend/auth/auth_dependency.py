from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import JWT_SECRET_KEY, JWT_ALGORITHM
from auth.role_permissions import ROLE_PERMISSIONS

# ================= SECURITY =================
security = HTTPBearer()


# ================= GET CURRENT USER =================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        # ✅ VALIDATION CHECKS
        if not payload or "user_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ================= PERMISSION CHECK =================
def require_permission(permission: str):

    def checker(user: dict = Depends(get_current_user)):

        role_id = user.get("role_id")

        # ✅ Ensure role_id exists
        if role_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Role not found in token. Please login again."
            )

        # ✅ Get permissions from map
        permissions = ROLE_PERMISSIONS.get(role_id, [])

        # ✅ Check access
        if "all" in permissions or permission in permissions:
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' denied"
        )

    return checker


# ================= ROLE CHECK =================
def require_role(role: str):

    def checker(user: dict = Depends(get_current_user)):

        user_role = user.get("role")

        # ✅ Normalize (avoid case issues)
        if not user_role or user_role.lower() != role.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role '{role}'"
            )

        return user

    return checker
