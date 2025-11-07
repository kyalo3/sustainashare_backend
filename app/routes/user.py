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
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from typing import Dict
from app.database import user_collection
from app.models.user import UserCreate, create_user, get_user_by_email, user_helper
from app.models.donor import get_donor_by_user_id
from app.models.recipient import get_recipient_by_user_id
from app.routes.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.utils import verify_password

router = APIRouter()

@router.post("/register", response_model=Dict[str, str])
async def register_user(user: UserCreate) -> Dict[str, str]:
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create the user and generate token
    user_data = await create_user(user)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user_data["email"]}, expires_delta=access_token_expires)

    # Default role set to none
    role = "none"

    # Check if the user has a donor or recipient profile
    donor_profile = await get_donor_by_user_id(user_data["id"])
    recipient_profile = await get_recipient_by_user_id(user_data["id"])
    if donor_profile:
        role = "donor"
    elif recipient_profile:
        role = "recipient"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user_data["id"],
        "username": user_data["username"],
        "email": user_data["email"],
        "role": role
    }

async def get_user_by_credentials(email: str, password: str):
    """Fetch a user by their email and password with role data if available"""
    # Get the user by email
    user = await user_collection.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Prepare the response
    response = user_helper(user)
    user_id = response["id"]

    # Check if the user is a donor
    donor = await get_donor_by_user_id(user_id)
    if donor:
        response["role"] = "donor"
        response["donor_data"] = donor  # add full donor data

    # Check if the user is a recipient
    recipient = await get_recipient_by_user_id(user_id)
    if recipient:
        response["role"] = "recipient"
        response["recipient_data"] = recipient  # add full recipient data

    # If neither, set role as "none"
    if not donor and not recipient:
        response["role"] = "none"

    return response

@router.post("/login", response_model=Dict[str, str])
async def login_for_access_token(email: str, password: str) -> Dict[str, str]:
    """Login endpoint to authenticate users and return full role data with access token"""
    user_data = await get_user_by_credentials(email, password)
    
    # Generate an access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_data["email"]}, expires_delta=access_token_expires)

    # Add the access token to the response
    user_data["access_token"] = access_token
    user_data["token_type"] = "bearer"
    
    return user_data
>>>>>>> refs/remotes/origin/main
>>>>>>> 812692b (new changes)
