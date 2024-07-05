from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from passlib.context import CryptContext

ALGORITHM = "HS256"
SECRET_KEY = "0f52fc5682abf3f293ae577dc6f85d1679c78457a1d05853bd6be23efdf58dde"
router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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
        "password": "$2a$12$bUPlmqcG9M5oLru7nFUoyOWVo531g0ovXblXfBOsmMp/KIZ6AXL9G",
    },
    "puni": {
        "username": "pu",
        "full_name": "Puni",
        "email": "puni@google.com",
        "disabled": False,
        "password": "$2a$12$aXvv6MwB2DaRXi/.3h7/G.RcllE7kotMhryGHomaZES/EodQrIqhy",
    },
}


def search_user_db(username: str):
    try:
        if username in users_db:
            return UserDB(**users_db[username])
    except KeyError:
        return "Not found"


def search_user(username: str):
    try:
        if username in users_db:
            return User(**users_db[username])
    except KeyError:
        return "Not found"


def exception_unauthorized_handler(
    message: str,
):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )
    return exception


async def auth_user(token: str = Depends(oauth2)):

    try:
        username = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception_unauthorized_handler("Could not validate credentials")

    except jwt.exceptions.ExpiredSignatureError:
        raise exception_unauthorized_handler("Token has expired")

    return search_user(username)


async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    # Get user from database
    user_db = users_db.get(form_data.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or password is incorrect",
        )
    user = search_user_db(form_data.username)

    # Verify password
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = {
        "sub": user.username,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    # Return created token token
    return {
        "access_token": jwt.encode(access_token, SECRET_KEY, algorithm=ALGORITHM),
        "token_type": "bearer",
    }


@router.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
