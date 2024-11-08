from aiogram.filters.callback_data import CallbackData


class ParticipantCallbackData(CallbackData, prefix='participant'):
    action: str
    name: str | None
    id: int | None


class SantaIdeasCallbackData(CallbackData, prefix='ideas'):
    action: str
    name: str | None
    recipient_id: int | None
