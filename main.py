from hmac import new
from http.client import HTTPException
from operator import is_
from fastapi import FastAPI, status
from pydantic import BaseModel
import models
from typing import Optional, List
from database import SessionLocal

app = FastAPI()


class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float
    on_offer: bool

    class Config:
        orm_mode = True


db = SessionLocal()


@app.get("/items/", response_model=List[Item], status_code=status.HTTP_200_OK)
def get_all_items():
    items = db.query(models.Item).all()
    return items


@app.get("/item/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
def get_an_item(item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    return item


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_an_item(item: Item):

    db_item = db.query(models.Item).filter(models.Item.name == item.name).exists()
    # if db_item is not None:
    #     raise HTTPException
    new_item = models.Item(
        name=item.name,
        price=item.price,
        description=item.description,
        on_offer=item.on_offer,
    )


    db.add(new_item)
    db.commit()
    return new_item


@app.put("/item/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
def update_an_item(item_id: int, item: Item):
    item_to_update = db.query(models.Item).filter(models.Item.id == item_id).first()
    item_to_update.name = item.name
    item_to_update.price = item.price
    item_to_update.description = item.description
    item_to_update.on_offer = item.on_offer

    db.commit()
    return item_to_update


@app.delete("/item/{item_id}")
def remove_an_item(item_id: int):
    item_to_delete=db.query(models.Item).filter(models.Item.id==item_id).first()
    if item_to_delete is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.commit()
    return item_to_delete