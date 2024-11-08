from __future__ import annotations

from typing import TYPE_CHECKING
from logging import getLogger

from sqlalchemy.future import select

from src.database.models.models import Participant
from src.database.database import db_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


logger = getLogger(__name__)


async def initialize_participants(session: AsyncSession = db_session):

    async with session.begin():
        participants = [
            'Владимир',
            'Тереса',
            'Юлия',
            'Виктория',
            'Анна',
            'Александр'
        ]

        result = await session.execute(select(Participant.name))
        existing_names = {row for row in result.scalars()}

        new_participants = [
            Participant(name=name)
            for name in participants
            if name not in existing_names
        ]

        if new_participants:
            session.add_all(new_participants)
            await session.commit()
            logger.info(
                f'Add new participants names: '
                f'{[participant.name for participant in new_participants]}'
            )
        else:
            logger.info('All participants are already exist')


async def initialize_db_data():
    await initialize_participants()
