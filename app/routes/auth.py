from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import get_user_by_email  # Updated to get user by email
from app.utils import get_password_hash, verify_password
import os

# Secret key and algorithm for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "secret")  # Environment variable for secret key, with default fallback
ALGORITHM = "HS256"  # Algorithm for JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 300  # Token expiration time in minutes

# Initialize password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer instance to get token from request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate_user(email: str, password: str):
    """
    Authenticate the user by verifying the email and password.
    Returns the user if authentication is successful, otherwise returns False.
    """
    user = await get_user_by_email(email)  # Fetch user by email
    if not user or not verify_password(password, user["password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Function that creates a JWT access token with an expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Function that gets the current user from the provided JWT token.
    Raises an HTTP 401 error if the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # Now using email as the subject
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch the user by email
    user = await get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user
