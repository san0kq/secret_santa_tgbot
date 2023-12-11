from aiogram.filters.callback_data import CallbackData


class ParticipantCallbackData(CallbackData, prefix='participant'):
    action: str
    name: str | None
    id: int | None
