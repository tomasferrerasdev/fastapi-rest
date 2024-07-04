from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
async def root():
    return "Hello FastAPI"


@app.get("/url")
async def url():
    return {"url": "https://tomasferreras.com"}


@app.post("/items/")
async def create_item(item: Item):
    return item
