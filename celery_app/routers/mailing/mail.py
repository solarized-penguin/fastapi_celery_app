from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClientSession
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from db import get_session, EmailOutboxMessage, EmailBase
from .models import EmailSchema, templates

mail_router = APIRouter(
    prefix="/tasks/mail", tags=["mail"], include_in_schema=True, default_response_class=ORJSONResponse
)


@mail_router.post("/add_to_queue", response_model=EmailBase)
async def add_mail_to_queue(
    message: Annotated[EmailSchema, Depends(EmailSchema.create_schema)],
    session: Annotated[AsyncIOMotorClientSession, Depends(get_session)],
) -> Annotated[EmailBase, ORJSONResponse]:
    outbox_mail = EmailOutboxMessage(email=message.model_dump())

    await outbox_mail.insert(session=session)
    return ORJSONResponse(status_code=status.HTTP_201_CREATED, content={"mail": outbox_mail.model_dump(mode="json")})


@mail_router.get("/templates", response_model=list[str])
async def all_templates() -> Annotated[list[str], ORJSONResponse]:
    templates_names = [template for template in templates.env.list_templates()]
    if not templates_names:
        return ORJSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

    return ORJSONResponse(status_code=status.HTTP_200_OK, content={"mail-template-names": templates_names})


@mail_router.get("/template/{name}", response_class=HTMLResponse)
async def template_by_name(name: Annotated[str, Path(title="Template file name")], request: Request) -> HTMLResponse:
    template = templates.get_template(name=name)

    if not template:
        return HTMLResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

    rendered_template = await template.render_async(
        bookstore_api_email_verification_url="http://0.0.0.0:8081/test_auth"
    )
    return HTMLResponse(content=rendered_template, status_code=status.HTTP_200_OK, media_type=HTMLResponse.media_type)
