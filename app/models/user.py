from pydantic import BaseModel, EmailStr
from app.utils import get_password_hash
from app.database import user_collection
"""
user model
"""


class UserBase(BaseModel):
    """ base model for User """
    Username: str


class UserCreate(UserBase):
    """ model for creating a user """
    Username: str
    Email: EmailStr
    Password: str

    

class User(UserBase):
    """ class to represent a User """
    id: str

    class Config:
        """ pydantic configuration for user """
        from_attributes = True


def user_helper(user) -> dict:
    """ helper function to transform user document into dictionary """
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "password": user["password"]
    }


async def create_user(user: UserCreate):
    """ creates a new user """
    user_dict = user.dict()
    user_dict['password'] = get_password_hash(user_dict['password'])
    new_user = await user_collection.insert_one(user_dict)
    return user_helper(await user_collection.find_one({"_id": new_user.inserted_id}))


async def get_user_by_username(username: str):
    """ function that gets a user by username """
    user = await user_collection.find_one({"username": username})
    if user:
        return user_helper(user)
    return None

async def get_user_by_email(email: str):
    """ function that gets a user by email """
    user = await user_collection.find_one({"email": email})
    if user:
        return user_helper(user)
    return None

async def get_user_by_credentials(username: str, email: str, password: str):
    """Fetch a user by their username and password"""
    user = await get_user_by_username(username)
    user = await get_user_by_email(email)
    if not user or not verify_password(password, user["password"]):
        return False
    return user
