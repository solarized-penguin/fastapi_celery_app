from typing import Annotated, Any

from fastapi_mail import MessageType
from pydantic import EmailStr
from sqlmodel import Field

from core import get_settings
from db import EmailBase


class EmailSchema(EmailBase):
    model_config = get_settings().default_model_config.config

    template_name: Annotated[
        str | None,
        Field(title="Email template name", description="Template will be populated with data from 'body_params'"),
    ]
    body_params: Annotated[dict[str, Any] | None, Field(title="Key-value pairs used to populate template")]

    @classmethod
    def create_schema(
        cls,
        recipients: Annotated[list[EmailStr], Field(title="List of recipients emails", unique=True)],
        subject: Annotated[str, Field(title="Message subject")],
        template_name: Annotated[
            str | None,
            Field(title="Email template name", description="Template will be populated with data from 'body_params'"),
        ] = None,
        body_params: Annotated[dict[str, Any] | None, Field(title="Key-value pairs used to populate template")] = None,
        subtype: Annotated[MessageType, Field(title="Message type")] = MessageType.html,
    ) -> dict[str, Any]:
        return cls(
            body_params=body_params,
            recipients=recipients,
            subject=subject,
            template_name=template_name,
            subtype=subtype,
        )
