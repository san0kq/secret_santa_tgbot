from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError
from logging import getLogger

logger = getLogger(__name__)

async def message_delete(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        event = event.message
    try:
        await event.delete()  # Deleting message
        if event.text:
            log_example_text = event.text[:32]
        else:
            log_example_text = ''
        logger.debug(
            "[-] Message %s delete success, text:  %s",
            event.message_id,
            log_example_text,
        )
    except (TelegramAPIError):
        logger.warning("[x] Error! Message not found %s", event.message_id)
    except Exception as err:
        logger.warning(
            "[x] Error deleting message %s >> %s",
            event.message_id,
            err.args,
            exc_info=err,
        )
