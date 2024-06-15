from contextlib import asynccontextmanager
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Annotated

from beanie import init_beanie
from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession


from core import get_settings
from .models import EmailOutboxMessage

client = AsyncIOMotorClient(get_settings().mongo_db.mongo_dsn)
celery_db = client.get_database(name=get_settings().mongo_db.path)


async def get_session() -> AsyncGenerator[AsyncIOMotorClientSession, Any]:
    async with await client.start_session(causal_consistency=get_settings().mongo_db.causal_consistency) as session:
        yield session


async def init_db() -> None:
    await init_beanie(
        database=celery_db,
        document_models=[EmailOutboxMessage],
        multiprocessing_mode=get_settings().mongo_db.multiprocessing_mode,
    )


@asynccontextmanager
async def db_init_lifespan(_: FastAPI) -> None:
    await init_db()
    yield
