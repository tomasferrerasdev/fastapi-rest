from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel


router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")


# User entity
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


users_db = {
    "tomasferreras": {
        "username": "tomasferreras",
        "full_name": "Tomas Ferreras",
        "email": "tomas@google.com",
        "disabled": False,
        "password": "123456",
    },
    "puni": {
        "username": "pu",
        "full_name": "Puni",
        "email": "puni@google.com",
        "disabled": False,
        "password": "654321",
    },
}


def search_user(username: str):
    try:
        if username in users_db:
            return User(**users_db[username])
    except KeyError:
        return "Not found"


def search_user_db(username: str):
    try:
        if username in users_db:
            return UserDB(**users_db[username])
    except KeyError:
        return "Not found"


async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or password is incorrect",
        )
    user = search_user_db(form.username)
    if user.password != form.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or password is incorrect",
        )
    return {"access_token": user.username, "token_type": "bearer"}


@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
