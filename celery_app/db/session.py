from contextlib import asynccontextmanager

from beanie import init_beanie
from beanie.odm.documents import ClientSession
from fastapi import FastAPI
from pymongo.mongo_client import client_session
from motor.motor_asyncio import AsyncIOMotorClient
from core import get_settings
from .models import EmailOutboxMessage

client = AsyncIOMotorClient(get_settings().mongo_db.mongo_dsn)
celery_db = client.get_database(name=get_settings().mongo_db.path)


@asynccontextmanager
async def get_session():
    async with await celery_db.client.start_session(
        causal_consistency=get_settings().mongo_db.causal_consistency
    ) as session:
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
