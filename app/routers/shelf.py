from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from .. import schemas, models, database, dependencies

router = APIRouter(
    prefix="/shelf",
    tags=["Shelf (My Books)"]
)

@router.get("/", response_model=List[schemas.ShelfItem])
async def get_my_shelf(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    result = await db.execute(
        select(models.ShelfItem)
        .where(models.ShelfItem.user_id == current_user.id)
        .options(selectinload(models.ShelfItem.book)) 
    )
    return result.scalars().all()

@router.post("/", response_model=schemas.ShelfItem, status_code=status.HTTP_201_CREATED)
async def add_book_to_shelf(
    item: schemas.ShelfItemCreate, 
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    book_result = await db.execute(select(models.Book).where(models.Book.id == item.book_id))
    book = book_result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    existing_item = await db.execute(
        select(models.ShelfItem).where(
            models.ShelfItem.user_id == current_user.id,
            models.ShelfItem.book_id == item.book_id
        )
    )
    if existing_item.scalars().first():
        raise HTTPException(status_code=400, detail="Book already on your shelf")

    new_shelf_item = models.ShelfItem(
        user_id=current_user.id,
        book_id=item.book_id,
        status=item.status,
        rating=item.rating,
        review=item.review
    )
    
    db.add(new_shelf_item)
    await db.commit()
    await db.refresh(new_shelf_item)
    
    new_shelf_item.book = book 
    
    return new_shelf_item

@router.put("/{item_id}", response_model=schemas.ShelfItem)
async def update_shelf_item(
    item_id: int,
    update_data: schemas.ShelfItemUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    result = await db.execute(
        select(models.ShelfItem)
        .where(models.ShelfItem.id == item_id)
        .where(models.ShelfItem.user_id == current_user.id) 
        .options(selectinload(models.ShelfItem.book))
    )
    shelf_item = result.scalars().first()

    if not shelf_item:
        raise HTTPException(status_code=404, detail="Shelf item not found")

    if update_data.status is not None:
        shelf_item.status = update_data.status
    if update_data.rating is not None:
        shelf_item.rating = update_data.rating
    if update_data.review is not None:
        shelf_item.review = update_data.review

    await db.commit()
    await db.refresh(shelf_item)
    return shelf_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_shelf(
    item_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    result = await db.execute(
        select(models.ShelfItem)
        .where(models.ShelfItem.id == item_id)
        .where(models.ShelfItem.user_id == current_user.id)
    )
    shelf_item = result.scalars().first()

    if not shelf_item:
        raise HTTPException(status_code=404, detail="Shelf item not found")

    await db.delete(shelf_item)
    await db.commit()
    return None