from datetime import datetime, UTC
from typing import Annotated

from beanie import Document, TimeSeriesConfig, Granularity
from fastapi_mail import MessageType
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from core import get_settings


def _generate_datetime() -> datetime:
    return datetime.now(UTC)


def _timeseries_settings(time_field: str) -> TimeSeriesConfig:
    return TimeSeriesConfig(time_field=time_field, granularity=Granularity.seconds)


class BaseDocumentSettings:
    keep_nulls = get_settings().beanie_default_settings.keep_nulls
    is_root = False
    with_children = get_settings().beanie_default_settings.with_children
    use_cache = get_settings().beanie_default_settings.use_cache
    cache_expiration_time = get_settings().beanie_default_settings.cache_expiration_timedelta
    cache_capacity = get_settings().beanie_default_settings.cache_capacity


class BaseDocument(Document):
    class Settings(BaseDocumentSettings):
        is_root = True


class EmailBase(SQLModel):
    recipients: Annotated[list[EmailStr], Field(title="List of recipients emails", nullable=False)]
    subject: Annotated[str, Field(title="Message subject", nullable=True)]
    body: Annotated[str, Field(title="Fully rendered email body", nullable=False)]
    subtype: Annotated[MessageType, Field(title="Message type", nullable=False)]


class EmailOutboxMessage(BaseDocument):
    created_at: Annotated[datetime, Field(default_factory=_generate_datetime, title="Date of creation", exclude=True)]
    is_processed: Annotated[bool, Field(title="Is mail already processed?", exclude=True)] = False
    email: Annotated[EmailBase, Field(title="Email data to send")]

    class Settings(BaseDocumentSettings):
        name = "outbox_emails"
        timeseries = _timeseries_settings("created_at")

    @classmethod
    def create_email(
        cls,
        recipients: Annotated[list[EmailStr], Field(title="List of recipients emails")],
        subject: Annotated[str | None, Field(title="Message subject")],
        body: Annotated[bytes, Field(title="Fully rendered email body")],
        subtype: Annotated[MessageType, Field(title="Message type")],
    ) -> "EmailOutboxMessage":
        return cls(email=EmailBase(recipients=recipients, subject=subject, body=body, subtype=subtype))
