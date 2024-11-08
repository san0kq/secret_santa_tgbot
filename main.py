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
from random import choice

from src.database.user import (
    get_all_participants,
    add_user,
    get_free_participants,
    restart_all,
    fetch_user_db,
    set_santa_user_db,
    set_selected_participant_db,
    get_participant as get_participant_db,
)
from src.database.initialize import initialize_db_data
from src.settings import API_TOKEN, ADMIN_ID
from src.tools import message_delete
from src.callback import ParticipantCallbackData, SantaIdeasCallbackData
from src.yandex_ai import get_santa_ideas

main_router = Router()
logger = logging.getLogger(__name__)
dp = Dispatcher()
dp.include_router(main_router)


@main_router.message(Command("start"))
@main_router.callback_query(ParticipantCallbackData.filter(F.action == 'menu'))
async def cmd_start(
    event: Message | types.CallbackQuery,
    callback: ParticipantCallbackData = None,
    state: FSMContext = None
):
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
                    callback_data=ParticipantCallbackData(
                        name=participant.name,
                        id=participant.id,
                        action='choice').pack()
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
        await event.message.edit_text(
            text=message_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )


@main_router.callback_query(ParticipantCallbackData.filter(F.action == "choice"))
async def choice_participant(query: CallbackQuery, callback_data: ParticipantCallbackData):
    builder = InlineKeyboardBuilder()
    participant_name = callback_data.name
    participant_id = callback_data.id

    message_text = f'❄️ {participant_name} ❄️\n\n☃️ Пожалуйста, подтвердите ваше имя ☃️'
    builder.button(
        text=f'✅ {participant_name}',
        callback_data=ParticipantCallbackData(action='add', name=participant_name, id=participant_id)
    )
    builder.button(
        text="❌ Нет, перевыбрать",
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
    user_participant = await get_participant_db(participant_id=participant_id)
    user_name = user_participant.name
    logger.info(user_name)

    participants = await get_free_participants(participant_id=participant_id)
    if participants:
        random_participant = choice(participants)
        participant_name = random_participant.name
        message_text = (
            f'🎁 Ваш получатель - <b>{participant_name}</b>!\n\n❗️ '
            f'Запомните это имя или запишите его куда-нибудь.\n'
            f'А лучше просто не удаляйте это сообщение.\n'
            f'Больше получить это имя из бота никто не сможет, в том '
            f'числе и вы.\n\nВы можете попросить настоящего Санту помочь '
            f'вам с выбором подарка для вашего получателя. Нажмите на '
            f'кнопку ниже, подождите немного и он придумает '
            f'несколько вариантов.\n\n🎄 С наступающим Новым годом! 🎄'
        )
        await set_santa_user_db(user_id=user_id)
        await set_selected_participant_db(participant_id=random_participant.id)
        photo = FSInputFile('src/images/secret_santa.png')

        builder.button(
            text='🎁 Спросить у Санты идеи для подарков 🎁',
            callback_data=SantaIdeasCallbackData(
                action='idea',
                name=user_name,
                recipient_id=random_participant.id
            )
        )
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


@main_router.callback_query(SantaIdeasCallbackData.filter(F.action == "idea"))
async def generate_ideas(
    callback: CallbackQuery,
    callback_data: SantaIdeasCallbackData
):
    builder = InlineKeyboardBuilder()

    user_name = callback_data.name
    recipient_id = callback_data.recipient_id

    recipient_paricipant = await get_participant_db(
        participant_id=recipient_id
    )

    try:
        message_text = await get_santa_ideas(
            name=user_name,
            recipient_name=recipient_paricipant.name,
            description=recipient_paricipant.description
        )
    except Exception as err:
        logger.error(err)
        message_text = (
            'Санта оказался недоступен. Наверное очень занят.\n'
            'Попробуйте позже нажать на эту кнопку.'
        )

    builder.button(
        text='🎁 Спросить у Санты ещё раз 🎁',
        callback_data=SantaIdeasCallbackData(
            action='idea',
            name=user_name,
            recipient_id=recipient_id
        )
    )
    await callback.message.answer(
        text=message_text,
        reply_markup=builder.as_markup(),
        disable_notification=True,
        parse_mode=ParseMode.HTML
    )


@main_router.message(Command("restart"))
async def cmd_restart(
    message: Message,
    state: FSMContext = None
):
    user_id = message.from_user.id

    if str(user_id) != ADMIN_ID:
        logger.info(f'{user_id} != {ADMIN_ID}')
        await message.answer('У вас нет доступа к этой команде.')
        return

    await restart_all()

    await message.answer('Игра сброшена успешно!')


async def main():
    bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
    await initialize_db_data()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
