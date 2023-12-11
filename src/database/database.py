import asyncio
from typing import Generator

# import pydantic
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from settings import DATABASE_URL, DEBUG

Base = declarative_base()


db_engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG,
    pool_size=100,
    max_overflow=100,
    pool_recycle=3600,
    future=True
)
async_session_maker = async_sessionmaker(
    db_engine, expire_on_commit=False, class_=AsyncSession
)
db_session = async_scoped_session(async_session_maker, asyncio.current_task)

async_session = async_sessionmaker(
    db_engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db():
    """First time init models in clear database"""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> Generator:
    """Init session for execute requests"""
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
