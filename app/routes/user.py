from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.models.user import User, UserCreate, create_user, get_user_by_email
from app.routes.auth import authenticate_user, create_access_token

router = APIRouter()


@router.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    This endpoint allows users to log in and receive an access token.
    Request Body:
        form_data: an instance of OAuth2PasswordRequestForm which contains:
            username: the email of the user (used for authentication)
            password: the password of the user
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",  # Updated error message
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]},  # Use email as the subject in the token
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=User)
async def register_user(user: UserCreate):
    """
    This endpoint allows new users to register.
    Request Body:
        username: name of the user.
        email: email of the user
        password: password of the user
    """
    db_user = await get_user_by_email(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = await create_user(user)
    user_id = user_dict.get("id")
    return {"id": user_id, "username": user.username, "email": user.email}


async def get_user_by_credentials(email: str):
    """
    Fetch a user by their email.
    """
    user = await get_user_by_email(email)
    if user:
        return user
    return None
