import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types.message import Message
from aiogram.types import CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from settings import API_TOKEN
from random import choice

from database.user import (
    get_all_participants,
    add_user,
    get_all_participants_from_stock,
    delete_particimant_from_stock,
    fetch_user_db,
    set_santa_user_db
)
from tools import message_delete
from callback import ParticipantCallbackData

main_router = Router()
logger = logging.getLogger(__name__)
dp = Dispatcher()
dp.include_router(main_router)

@main_router.message(Command("start"))
@main_router.callback_query(ParticipantCallbackData.filter(F.action == 'menu'))
async def cmd_start(event: Message | types.CallbackQuery, callback: ParticipantCallbackData = None, state: FSMContext = None):
    if isinstance(event, CallbackQuery):
        event = event.message
    
    user_id = event.from_user.id

    if user := await fetch_user_db(user_id=user_id):
        if not user.is_santa:
            await state.update_data(
                participant_name=user.name,
                participant_id=user.participant_id
            )
            await add_participant(event=event, state=state)
            return None
        else:
            message_text = '🤷‍♂️ У вас уже есть получатель. Надеюсь, вы не забыли его имя.'
            builder = InlineKeyboardBuilder()
    else:
        participants = await get_all_participants()
        builder = InlineKeyboardBuilder()
        if participants:
            message_text = '🎄 Выберите своё имя из списка! 🎄'
            for participant in participants:
                builder.button(
                    text=participant.name,
                    callback_data=ParticipantCallbackData(name=participant.name, id=participant.id, action='choice').pack()
                )
            builder.adjust(1, 1)
        else:
            message_text = '🤷‍♂️ Все участники уже в игре.\n\n🎉 С наступающим Новым годом!'
    
    if isinstance(event, Message):
        await event.answer(
            text=message_text,
            reply_markup=builder.as_markup(),
            disable_notification=True,
            parse_mode=ParseMode.HTML
        )
        await message_delete(event)
    else:
        await event.message.edit_text(text=message_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@main_router.callback_query(ParticipantCallbackData.filter(F.action == "choice"))
async def choice_participant(query: CallbackQuery, callback_data: ParticipantCallbackData):
    user_id = query.from_user.id
    builder = InlineKeyboardBuilder()
    participant_name = callback_data.name
    participant_id = callback_data.id

    message_text = f'❄️ {participant_name} ❄️\n\n☃️ Пожалуйста, подтвердите ваше имя ☃️'
    builder.button(
        text=f'✅ {participant_name}',
        callback_data=ParticipantCallbackData(action='add', name=participant_name, id=participant_id)
    )
    builder.button(
        text="❌ Нет, я ошибся",
        callback_data=ParticipantCallbackData(action='menu', name=None, id=None)
    )
    builder.adjust(2, 1)
    await query.message.edit_text(text=message_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)


@main_router.callback_query(ParticipantCallbackData.filter(F.action == "add"))
async def add_participant(event: Message | CallbackQuery, callback_data: ParticipantCallbackData = None, state: FSMContext = None):
    user_id = event.from_user.id
    builder = InlineKeyboardBuilder()
    if callback_data:
        participant_name = callback_data.name
        participant_id = callback_data.id

        await add_user(participant_id=participant_id, user_id=user_id)
    else:
        state_data = await state.get_data()
        participant_name = state_data.get('participant_name')
        participant_id = state_data.get('participant_id')

    logger.info(f'{participant_id}, {participant_name}')
    message_text = f'🎅 Здравстуйте, <b>{participant_name}</b>! 🎅\n\n Если вы готовы, нажмите кнопку "🎁 Ваш получатель"'
    builder.button(
        text='🎁 Ваш получатель...',
        callback_data=ParticipantCallbackData(action='get', name=None, id=participant_id)
    )
    builder.adjust(1, 1)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=message_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    else:
        await event.answer(
            text=message_text,
            reply_markup=builder.as_markup(),
            disable_notification=True,
            parse_mode=ParseMode.HTML
        )
        await message_delete(event)


@main_router.callback_query(ParticipantCallbackData.filter(F.action == "get"))
async def get_participant(event: Message | CallbackQuery, callback_data: ParticipantCallbackData = None):
    user_id = event.from_user.id
    builder = InlineKeyboardBuilder()
    participant_id = callback_data.id
    logger.info(participant_id)

    participants = await get_all_participants_from_stock(participant_id=participant_id)
    if participants:
        random_participant = choice(participants)
        participant_name = random_participant.name
        message_text = f'🎁 Ваш получатель - <b>{participant_name}</b>!\n\n❗️ Запомните это имя, а лучше запишите его куда-нибудь. Больше получить это имя из бота никто не сможет, в том числе и вы.\n\n 🎄 С наступающим Новым годом! 🎄'
        await set_santa_user_db(user_id=user_id)
        photo = FSInputFile('images/secret_santa.png')
        await event.message.answer_photo(
            photo=photo,
            caption=message_text,
            reply_markup=builder.as_markup(),
            disable_notification=True,
            parse_mode=ParseMode.HTML
        )
        await message_delete(event)

    else:
        message_text = '🤷‍♂️ Доступных получателей больше нет.'

        if isinstance(event, CallbackQuery):
            await event.message.edit_text(text=message_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        else:
            await event.answer(
                text=message_text,
                reply_markup=builder.as_markup(),
                disable_notification=True,
                parse_mode=ParseMode.HTML
            )
            await message_delete(event)

    await delete_particimant_from_stock(participant_id=random_participant.participant_id)

async def main():
    session = AiohttpSession(proxy='http://proxy.server:3128')
    bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML, session=session)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
