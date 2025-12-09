from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from .. import schemas, models, database, dependencies

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=List[schemas.User])
async def get_all_users(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can view all users")
    
    result = await db.execute(select(models.User))
    return result.scalars().all()

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalars().first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.username is not None:
        existing_username = await db.execute(
            select(models.User).where(
                models.User.username == user_update.username,
                models.User.id != user_id
            )
        )
        if existing_username.scalars().first():
            raise HTTPException(status_code=400, detail="Username already taken")
        db_user.username = user_update.username
    
    if user_update.email is not None:
        existing_email = await db.execute(
            select(models.User).where(
                models.User.email == user_update.email,
                models.User.id != user_id
            )
        )
        if existing_email.scalars().first():
            raise HTTPException(status_code=400, detail="Email already taken")
        db_user.email = user_update.email
    
    if user_update.role is not None and current_user.role == models.UserRole.ADMIN:
        db_user.role = user_update.role
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only administrators can delete users")
    
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalars().first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    shelf_items_result = await db.execute(
        select(models.ShelfItem).where(models.ShelfItem.user_id == user_id)
    )
    shelf_items = shelf_items_result.scalars().all()
    
    for item in shelf_items:
        await db.delete(item)
    
    await db.delete(db_user)
    await db.commit()
    return None


