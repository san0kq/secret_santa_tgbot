from logging import getLogger

from yandex_cloud_ml_sdk import YCloudML

from src import settings

logger = getLogger(__name__)

sdk = YCloudML(folder_id=settings.CATALOG_ID, auth=settings.YANDEX_TOKEN)

ai_model = sdk.models.completions('yandexgpt-lite')
ai_model = ai_model.configure(temperature=0.5)


async def get_santa_ideas(name: str, recipient_name: str, description: str) -> str:
    result = ai_model.run(
        f'Ты Санта, который помогает Секретному Санту выбрать подарок своему '
        f'получателю. Секретного Санту зовут {name}.\n\n'
        f'Придумай 10 вариантов подарков на Новый год, в ценовом диапазоне '
        f'до 100 беларуских рублей (около 33 долларов), для человека по имени'
        f' {recipient_name}\n\nВот описание этого человека:\n\n{description}\n'
        f'Используй это описание и постарайся придумать более '
        f'персонализированные подарки\n\n'
    )

    result = result[0].text

    return result
