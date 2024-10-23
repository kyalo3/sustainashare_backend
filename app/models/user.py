from pydantic import BaseModel, EmailStr
from app.utils import get_password_hash, verify_password
from app.database import user_collection
from bson import ObjectId

"""
User model
"""

class UserBase(BaseModel):
    """Base model for User"""
    username: str  # Username is required but not unique


class UserCreate(UserBase):
    """Model for creating a user"""
    email: EmailStr  # Email will be unique
    password: str


class User(UserBase):
    """Class to represent a User"""
    id: str
    email: EmailStr  # Email is required and unique

    class Config:
        """Pydantic configuration for user"""
        from_attributes = True


def user_helper(user) -> dict:
    """Helper function to transform user document into dictionary"""
    return {
        "id": str(user["_id"]),
        "username": user["username"],  # Username is required
        "email": user["email"],        # Email is required and unique
        "password": user["password"]   # Hashed password
    }


async def create_user(user: UserCreate):
    """Creates a new user"""
    user_dict = user.dict()
    
    # Hash the password before saving
    user_dict['password'] = get_password_hash(user_dict['password'])
    
    # Insert the new user into the database
    new_user = await user_collection.insert_one(user_dict)
    
    # Return the created user with the database's ObjectId converted to string
    return user_helper(await user_collection.find_one({"_id": new_user.inserted_id}))


async def get_user_by_email(email: str):
    """Function that gets a user by email"""
    user = await user_collection.find_one({"email": email})
    if user:
        return user_helper(user)
    return None


async def get_user_by_credentials(email: str, password: str):
    """Fetch a user by their email and password"""
    user = await get_user_by_email(email)
    
    # Verify user exists and password matches
    if not user or not verify_password(password, user["password"]):
        return False
    return user
