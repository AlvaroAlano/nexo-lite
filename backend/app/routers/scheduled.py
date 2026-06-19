from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database import get_db
from app.models.scheduled_expense import ScheduledExpense
from app.schemas.scheduled import ScheduledCreate, ScheduledResponse
from app.config import settings

router = APIRouter(prefix="/scheduled", tags=["scheduled"])


def get_user_id() -> UUID:
    """Placeholder — swap for Supabase JWT extraction when auth is wired up."""
    return settings.DEMO_USER_ID


@router.get("/", response_model=list[ScheduledResponse])
async def list_scheduled(db: AsyncSession = Depends(get_db)):
    user_id = get_user_id()
    result = await db.execute(
        select(ScheduledExpense)
        .where(ScheduledExpense.user_id == user_id)
        .order_by(
            ScheduledExpense.target_year,
            ScheduledExpense.target_month,
            ScheduledExpense.display_order,
        )
    )
    return [ScheduledResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/", response_model=ScheduledResponse, status_code=201)
async def create_scheduled(payload: ScheduledCreate, db: AsyncSession = Depends(get_db)):
    user_id = get_user_id()
    scheduled = ScheduledExpense(user_id=user_id, **payload.model_dump())
    db.add(scheduled)
    await db.flush()
    return ScheduledResponse.model_validate(scheduled)


@router.delete("/{scheduled_id}", status_code=204)
async def delete_scheduled(scheduled_id: UUID, db: AsyncSession = Depends(get_db)):
    user_id = get_user_id()
    result = await db.execute(
        select(ScheduledExpense).where(
            ScheduledExpense.id == scheduled_id,
            ScheduledExpense.user_id == user_id,
        )
    )
    scheduled = result.scalars().first()
    if scheduled is None:
        raise HTTPException(status_code=404, detail="Scheduled expense not found")
    await db.delete(scheduled)
    await db.flush()
