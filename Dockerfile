# Промежуточный этап сборки для выгрузки зависимостей из Poetry
FROM python:3.11.2-alpine as requirements_stage

ENV PYTHONUNBUFFERED=1

WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Заключительный этап сборки
FROM python:3.11.2-alpine

# Обновляем пакетный менеджер и устанавливаем зависимости
COPY --from=requirements_stage /tmp/requirements.txt ./requirements.txt

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r ./requirements.txt && \
    pip install --no-cache /wheels/* \
# Это позволит очистить кэш apt
    && rm -rf /var/lib/apt/lists/*

# Копируем все файлы приложения в рабочую директорию в контейнере
#COPY . /code
WORKDIR /code
#CMD python run.py
