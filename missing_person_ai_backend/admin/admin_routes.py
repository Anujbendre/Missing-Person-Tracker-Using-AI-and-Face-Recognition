from fastapi import APIRouter, Depends, HTTPException
from auth.auth_dependency import require_permission
from admin.admin_service import (
    get_all_users,
    change_user_role,
    delete_user,
    get_all_cases,
    update_case_status,
    dashboard_stats
)

# =====================================================
# ADMIN ROUTER INITIALIZATION
# This router handles all admin related APIs
# Base URL → /admin
# =====================================================

router = APIRouter(
    prefix="/admin",
    tags=["Admin Module"]
)


# =====================================================
# USER MANAGEMENT ROUTES
# These APIs allow admin to manage system users
# =====================================================

# -------------------------------------------
# GET ALL USERS
# Endpoint → GET /admin/users
# Purpose → Admin can view all registered users
# -------------------------------------------

@router.get("/users")
def admin_get_users(user=Depends(require_permission("all"))):

    users = get_all_users()

    return {
        "status": "success",
        "total_users": len(users),
        "data": users
    }


# -------------------------------------------
# CHANGE USER ROLE
# Endpoint → PUT /admin/users/{user_id}/role
# Purpose → Admin can update role of any user
# Example → Police → Investigator
# -------------------------------------------

@router.put("/users/{user_id}/role")
def admin_change_role(
    user_id: int,
    role_id: int,
    user=Depends(require_permission("all"))
):

    success = change_user_role(user_id, role_id)

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "status": "success",
        "message": "User role updated successfully"
    }


# -------------------------------------------
# DELETE USER
# Endpoint → DELETE /admin/users/{user_id}
# Purpose → Admin can remove users from system
# -------------------------------------------

@router.delete("/users/{user_id}")
def admin_delete_user(
    user_id: int,
    user=Depends(require_permission("all"))
):

    success = delete_user(user_id)

    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "status": "success",
        "message": "User deleted successfully"
    }


# =====================================================
# CASE MANAGEMENT ROUTES
# Admin can monitor and manage investigation cases
# =====================================================

# -------------------------------------------
# VIEW ALL CASES
# Endpoint → GET /admin/cases
# Purpose → Admin can see all FIR cases
# -------------------------------------------

@router.get("/cases")
def admin_get_cases(
    user=Depends(require_permission("all"))
):

    cases = get_all_cases()

    return {
        "status": "success",
        "total_cases": len(cases),
        "data": cases
    }


# -------------------------------------------
# UPDATE CASE STATUS
# Endpoint → PUT /admin/cases/{case_id}/status
# Purpose → Admin can change case status
# Example → Active → Solved
# -------------------------------------------

@router.put("/cases/{case_id}/status")
def admin_update_status(
    case_id: int,
    status: str,
    user=Depends(require_permission("all"))
):

    success = update_case_status(case_id, status)

    if not success:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "status": "success",
        "message": "Case status updated successfully"
    }


# =====================================================
# ADMIN DASHBOARD ROUTE
# This API returns system statistics
# =====================================================

# -------------------------------------------
# ADMIN DASHBOARD
# Endpoint → GET /admin/dashboard
# Purpose → Show system analytics for admin
# -------------------------------------------

@router.get("/dashboard")
def admin_dashboard(
    user=Depends(require_permission("all"))
):

    stats = dashboard_stats()

    return {
        "status": "success",
        "data": stats
    }




