from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


# User entity
class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    url: str
    age: int


users_mock = [
    User(
        id=1,
        first_name="Tomas",
        last_name="Ferreras",
        username="tomasferreras",
        email="hellotomasdev@gmail.com",
        age=24,
        url="https://tomasferreras.com",
    ),
    User(
        id=2,
        first_name="Matias",
        last_name="Perez Viecho",
        username="matipviecho",
        email="mati@gmail.com",
        age=23,
        url="https://matiaspv.dev",
    ),
    User(
        id=3,
        first_name="Ivan",
        last_name="Peusco",
        username="ivanpeusc",
        email="thepeusc@gmail.com",
        age=24,
        url="https://ivanpeusc.com",
    ),
]


def search_user(user_id: int):
    try:
        users = filter(lambda user: user.id == user_id, users_mock)
        return list(users)[0]
    except IndexError:
        raise HTTPException(status_code=404, detail="User already exists")


@app.get("/users")
async def users():
    return users_mock


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return search_user(user_id)


@app.post("/users/", status_code=201)
async def create_user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code=409, detail="User already exists")
    users_mock.append(user)
    return user


@app.put("/users/{user_id}")
async def edit_user(user_id: int, user: User):
    for i, existing_user in enumerate(users_mock):
        if existing_user.id == user_id:
            users_mock[i] = user
            return user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    user_to_delete = search_user(user_id)
    if user_to_delete:
        users_mock.remove(user_to_delete)
        return user_to_delete
    raise HTTPException(status_code=404, detail="User not found")
