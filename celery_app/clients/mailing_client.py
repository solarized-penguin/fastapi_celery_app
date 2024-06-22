from typing import Annotated, Any

from fastapi import UploadFile
from fastapi_mail import FastMail, MessageType
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from core import get_settings


class MailMessage(SQLModel):
    body_params: Annotated[dict[str, Any] | None, Field(title="Params to fill template with", alias="body")]
    attachments: Annotated[list[UploadFile | dict | str] | None, Field(title="Attachments")]
    template_name: Annotated[
        str | None,
        Field(title="Email template name", description="Template will be populated with data from 'body_params'"),
    ]
    recipients: Annotated[list[EmailStr], Field(title="List of recipients emails")]
    subject: Annotated[str, Field(title="Message subject")]
    subtype: Annotated[MessageType, Field(title="Message type")]

    @classmethod
    def create(
        cls,
        recipients: Annotated[list[EmailStr], Field(title="List of recipients emails")],
        subject: Annotated[str, Field(title="Message subject")],
        attachments: Annotated[list[UploadFile | dict | str] | None, Field(title="Attachments")] = None,
        template_name: Annotated[
            str | None,
            Field(title="Email template name", description="Template will be populated with data from 'body_params'"),
        ] = None,
        body_params: Annotated[dict[str, Any] | None, Field(title="Params to fill template with", alias="body")] = None,
        subtype: Annotated[MessageType, Field(title="Message type")] = MessageType.html,
    ) -> "MailMessage":
        return cls(
            recipients=recipients,
            attachments=attachments,
            subject=subject,
            template_name=template_name,
            body_params=body_params,
            subtype=subtype,
        )


class Mailer:
    def __init__(self) -> None:
        template_folder = get_settings().resources.mail_templates_dir
        self._config = get_settings().tasks.mailing.connection_config(template_folder=template_folder)
        self._client = FastMail(config=self._config)

    async def send_with_template(self, mail: MailMessage):
        print(mail)
