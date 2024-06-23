from typing import Annotated

from fastapi import UploadFile
from fastapi_mail import FastMail, MessageType, MessageSchema
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from core import get_settings


class MailMessage(SQLModel):
    recipients: Annotated[list[EmailStr], Field(title="List of recipients emails")]
    subject: Annotated[str, Field(title="Message subject")]
    body: Annotated[str, Field(title="Fully rendered email body")]
    subtype: Annotated[MessageType, Field(title="Message type")]
    attachments: Annotated[list[UploadFile | dict | str] | None, Field(title="Attachments")]

    @classmethod
    def create(
        cls,
        body: Annotated[str, Field(title="Fully rendered email body")],
        recipients: Annotated[list[EmailStr], Field(title="List of recipients emails")],
        subject: Annotated[str, Field(title="Message subject")],
        attachments: Annotated[list[UploadFile | dict | str] | None, Field(title="Attachments")] = None,
        subtype: Annotated[MessageType, Field(title="Message type")] = MessageType.html,
    ) -> "MailMessage":
        return cls(recipients=recipients, attachments=attachments, subject=subject, body=body, subtype=subtype)


class Mailer:
    def __init__(self) -> None:
        self._client = FastMail(
            config=get_settings().tasks.mailing.connection_config(
                template_folder=get_settings().resources.mail_templates_dir
            )
        )

    async def send(self, mail: MailMessage) -> None:
        message = MessageSchema(
            subject=mail.subject,
            recipients=mail.recipients,
            body=mail.body,
            subtype=mail.subtype,
            attachments=mail.attachments,
        )

        await self._client.send_message(message=message)
