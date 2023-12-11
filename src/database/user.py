from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import delete, update
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.future import select

from database.database import db_session

from database.models.models import (
    User,
    Participant,
    ParticipantStock
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

logger = logging.getLogger(__name__)

async def fetch_user_db(
    user_id: int, session: async_scoped_session[AsyncSession] = db_session
):
    stmt = select(User.id, User.participant_id, User.is_santa, Participant.name).where(User.user_id == user_id).join(Participant)
    async with session.begin():
        result = await session.execute(stmt)
        user = result.fetchone()
        await session.close()
        return user


async def set_santa_user_db(
    user_id: int, session: async_scoped_session[AsyncSession] = db_session
):
    stmt = update(User).where(User.user_id == user_id).values(is_santa=True)
    async with session.begin():
        await session.execute(stmt)
        await session.commit()


async def get_all_participants(
    session: async_scoped_session[AsyncSession] = db_session
) -> list[Participant]:
    stmt = select(Participant).outerjoin(User, User.participant_id == Participant.id).filter(User.user_id.is_(None))
    async with session.begin():
        result = await session.execute(stmt)
        participants = result.scalars().all()
        return participants
    

async def get_all_participants_from_stock(
    participant_id: int,
    session: async_scoped_session[AsyncSession] = db_session
) -> list[ParticipantStock]:
    try:
        stmt = select(ParticipantStock.participant_id, Participant.name).join(Participant).filter(ParticipantStock.participant_id != participant_id)
        async with session.begin():
            result = await session.execute(stmt)
            participants = result.fetchall()
            return participants
        
    except Exception as err:
        logger.info(err)


async def add_user(
    participant_id: int,
    user_id: int,
    session: async_scoped_session[AsyncSession] = db_session
) -> None:
    user = User(
        user_id=user_id,
        participant_id=participant_id
    )
    async with session.begin():
        session.add(user)
        await session.commit()


async def delete_particimant_from_stock(
    participant_id: int,
    session: async_scoped_session[AsyncSession] = db_session
) -> None:
    stmt = delete(ParticipantStock).where(ParticipantStock.participant_id == participant_id)
    async with session.begin():
        await session.execute(stmt)
        await session.commit()
