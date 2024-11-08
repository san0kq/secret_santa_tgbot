from __future__ import annotations

from typing import TYPE_CHECKING
from sqlalchemy import delete, update
import logging

from sqlalchemy.future import select

from src.database.database import db_session

from src.database.models.models import (
    User,
    Participant,
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


async def set_selected_participant_db(
    participant_id: int,
    session: async_scoped_session[AsyncSession] = db_session
):
    stmt = update(Participant).where(Participant.id == participant_id).values(is_selected=True)
    async with session.begin():
        await session.execute(stmt)
        await session.commit()


async def get_all_participants(
    session: async_scoped_session[AsyncSession] = db_session
) -> list[Participant]:
    stmt = select(Participant).outerjoin(
        User,
        User.participant_id == Participant.id).filter(User.user_id.is_(None))
    async with session.begin():
        result = await session.execute(stmt)
        participants = result.scalars().all()
        return participants


async def get_free_participants(
    participant_id: int,
    session: async_scoped_session[AsyncSession] = db_session
) -> list[Participant]:
    try:
        stmt = (
            select(Participant.id, Participant.name, Participant.description)
            .where(
                Participant.id != participant_id,
                Participant.is_selected == False
            )
        )
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


async def restart_all(
    session: async_scoped_session[AsyncSession] = db_session
) -> None:
    stmt = delete(User)
    stmt2 = update(Participant).values(is_selected=False)
    async with session.begin():
        await session.execute(stmt)
        await session.execute(stmt2)
        await session.commit()


async def get_participant(
        participant_id: int,
        session: async_scoped_session[AsyncSession] = db_session
) -> Participant:
    stmt = select(Participant).where(Participant.id == participant_id).limit(1)

    async with session.begin():
        result = await session.execute(stmt)
        participant = result.scalar_one()
        return participant
