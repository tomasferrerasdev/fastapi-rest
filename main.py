from typing import Union
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from routes import users

app = FastAPI()
app.router.include_router(users.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
async def root():
    return "Hello FastAPI"
