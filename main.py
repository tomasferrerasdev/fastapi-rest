from typing import Union
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from routes import users, auth_users, auth_users_jwt

app = FastAPI()
app.router.include_router(users.router)

app.router.include_router(auth_users.router)
app.router.include_router(auth_users_jwt.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
async def root():
    return "Hello FastAPI"
