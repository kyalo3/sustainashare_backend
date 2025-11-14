from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import User, get_user_by_email, user_collection
from app.routes.auth_utils import get_current_user
from bson import ObjectId

router = APIRouter()


@router.get("/users/", response_model=List[dict])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """
    Fetch all users (admin only)
    """
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    
    users = await user_collection.find().to_list(length=None)
    return [
        {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user.get("role", "donor"),
            "is_admin": user.get("is_admin", False)
        }
        for user in users
    ]


@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Fetch the current logged-in user.
    """
    return current_user

