from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Any
from bson import ObjectId
from app.database import user_collection
from app.utils import get_password_hash, verify_password
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    DONOR = "donor"
    RECIPIENT = "recipient"
    VOLUNTEER = "volunteer"


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ):
        def validate(value: str) -> ObjectId:
            if not ObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return ObjectId(value)

        return handler(source_type)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema, handler
    ):
        return handler(core_schema)


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = Field(default=UserRole.DONOR)
    is_admin: bool = Field(default=False)
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[str] = None
    preferences: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = Field(default=UserRole.DONOR.value)
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[str] = None
    preferences: Optional[str] = None


def user_helper(user) -> dict:
    """Helper function to transform user document into a dictionary."""
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user.get("role", UserRole.DONOR),
        "is_admin": user.get("is_admin", False),
        "phone_number": user.get("phone_number"),
        "company_name": user.get("company_name"),
        "address": user.get("address"),
        "skills": user.get("skills"),
        "preferences": user.get("preferences"),
        "password": user["password"],  # Keep password for authentication checks
    }


async def create_user(user_data: UserCreate):
    """Creates a new user from a Pydantic model."""
    # Support both Pydantic v1 and v2
    try:
        user_dict = user_data.model_dump()  # Pydantic v2
    except AttributeError:
        user_dict = user_data.dict()  # Pydantic v1
    
    user_dict['password'] = get_password_hash(user_dict['password'])
    if user_dict.get("role") == UserRole.ADMIN.value:
        user_dict["is_admin"] = True
    else:
        user_dict["is_admin"] = False
    new_user = await user_collection.insert_one(user_dict)
    return new_user


async def get_user_by_id(user_id: str):
    """Gets a user by their ID."""
    try:
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return user_helper(user)
    except Exception:  # Catches invalid ObjectId format
        return None
    return None


async def get_user_by_email(email: str):
    """Gets a user by email."""
    user = await user_collection.find_one({"email": email})
    if user:
        return user_helper(user)
    return None


async def get_user_by_credentials(email: str, password: str):
    """Fetch a user by their email and password"""
    user = await user_collection.find_one({"email": email})

    # Verify user exists and password matches
    if not user or not verify_password(password, user["password"]):
        return None
    return user_helper(user)
