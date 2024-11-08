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
        participants = {
            'Владимир': 'Мужчина, 59 лет. Пенсионер, в прошлом полковник прокуратуры. Имеет 3 взрослых дочери и жену. Живёт в своём доме, имеет автомобиль.',
            'Тереса': 'Женщина, 58 лет. Пенсионер, в прошлом специалист по оздоровлению. По образованию бухгалтер. Имеет 3 взрослых довери и мужа. Живёт в своём доме и в квартире в городе.',
            'Юлия': 'Девушка, 30 лет. По образованию юрист. Работает юристом в государственной организации. Не замужем, детей не имеет. Любит читать, активный отдых (сноуборд, байдарки и тд.).',
            'Виктория': 'Девушка, 28 лет. По образованию врач-педиатр. В декрете. Имеет мужа и сына 1 год 8 месяцев. Хочет стать косметологом.',
            'Анна': 'Девушка, 20 лет. Учится в университете на переводчика (английский язык). Любит рисовать. Отучилась на UX/UI-дизайнера. Хочет найти работу по этому направлению. Есть молодой человек.',
            'Александр': 'Мужчина, 30 лет. По образованию врач-хирург. Отучился самостоятельно на Python-разработчика. На данный момент работает разработчиком програмного обеспечения. Любит играть в компьюетрные игры в свободное время.'
        }

        result = await session.execute(select(Participant.name))
        existing_names = {row for row in result.scalars()}

        new_participants = [
            Participant(name=name, description=description)
            for name, description in participants.items()
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
