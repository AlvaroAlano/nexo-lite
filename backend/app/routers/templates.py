from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.expense import ExpenseTemplate
from app.models.category import Category
from app.schemas.expense import TemplateCreate, TemplateUpdate, TemplateResponse
from app.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=list[TemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(ExpenseTemplate)
        .where(ExpenseTemplate.user_id == user_id)
        .order_by(ExpenseTemplate.display_order, ExpenseTemplate.created_at)
    )
    return [TemplateResponse.model_validate(t) for t in result.scalars().all()]


@router.post("/", response_model=TemplateResponse, status_code=201)
async def create_template(
    payload: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    category_name = payload.category
    if payload.category_id:
        cat = (await db.execute(
            select(Category).where(
                Category.id == payload.category_id,
                Category.user_id == user_id
            )
        )).scalars().first()
        if cat is None:
            raise HTTPException(status_code=404, detail="Category not found")
        category_name = cat.name
    tmpl = ExpenseTemplate(
        user_id=user_id,
        name=payload.name,
        category=category_name,
        category_id=payload.category_id,
        expense_type=payload.expense_type,
        responsavel=payload.responsavel,
        base_amount=payload.base_amount,
        installment_total=payload.installment_total,
        display_order=payload.display_order,
        rent_items=payload.rent_items,
    )
    db.add(tmpl)
    await db.flush()
    return TemplateResponse.model_validate(tmpl)


@router.patch("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    payload: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(ExpenseTemplate).where(
            ExpenseTemplate.id == template_id,
            ExpenseTemplate.user_id == user_id
        )
    )
    tmpl = result.scalars().first()
    if tmpl is None:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = payload.model_dump(exclude_none=True)
    if "installment_paid" in update_data:
        total = update_data.get("installment_total") or tmpl.installment_total or 1
        if update_data["installment_paid"] > total:
            raise HTTPException(status_code=400, detail="installment_paid cannot exceed installment_total")
    if "category_id" in update_data and update_data["category_id"] is not None:
        cat = (await db.execute(
            select(Category).where(
                Category.id == update_data["category_id"],
                Category.user_id == user_id
            )
        )).scalars().first()
        if cat is None:
            raise HTTPException(status_code=404, detail="Category not found")
        update_data["category"] = cat.name
    for field, value in update_data.items():
        setattr(tmpl, field, value)

    return TemplateResponse.model_validate(tmpl)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    result = await db.execute(
        select(ExpenseTemplate).where(
            ExpenseTemplate.id == template_id,
            ExpenseTemplate.user_id == user_id
        )
    )
    tmpl = result.scalars().first()
    if tmpl is None:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.delete(tmpl)
    await db.flush()
