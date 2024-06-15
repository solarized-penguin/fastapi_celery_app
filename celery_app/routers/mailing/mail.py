from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClientSession
from starlette import status

from core import get_settings
from db import get_session, EmailOutboxMessage, EmailBase
from .models import EmailSchema

mail_router = APIRouter(
    prefix="/tasks/mail", tags=["mail"], include_in_schema=True, default_response_class=ORJSONResponse
)


@mail_router.post("/add_to_queue")
async def add_mail_to_queue(
    message: Annotated[EmailSchema, Body(title="Email data")],
    session: Annotated[AsyncIOMotorClientSession, Depends(get_session)],
) -> Annotated[EmailSchema, ORJSONResponse]:
    outbox_mail = EmailOutboxMessage(email=EmailBase.parse_obj(message))
    print(outbox_mail)
    return 200


@mail_router.get("/templates", response_model=list[str], response_class=ORJSONResponse)
async def all_templates() -> Annotated[list[str], ORJSONResponse]:
    templates_names = [path.name for path in get_settings().paths.mail_templates_dir.iterdir() if path.is_file()]
    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"mail-template-names": templates_names})
