from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.config import settings

router = APIRouter(prefix="/categories", tags=["categories"])


def get_user_id() -> UUID:
    return settings.DEMO_USER_ID


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Category)
        .where(Category.user_id == get_user_id())
        .order_by(Category.display_order, Category.name)
    )
    return [CategoryResponse.model_validate(c) for c in result.scalars().all()]


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = Category(user_id=get_user_id(), **payload.model_dump())
    db.add(cat)
    await db.flush()
    return CategoryResponse.model_validate(cat)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalars().first()
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(cat, field, value)
    return CategoryResponse.model_validate(cat)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalars().first()
    if cat is None:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.flush()
