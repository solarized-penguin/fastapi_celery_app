from datetime import datetime, UTC
from typing import Any, Annotated

from beanie import Document, TimeSeriesConfig, Granularity
from fastapi_mail import MessageType
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

from core import get_settings


def _generate_datetime() -> datetime:
    return datetime.now(UTC)


def _timeseries_settings(time_field: str) -> TimeSeriesConfig:
    return TimeSeriesConfig(time_field=time_field, granularity=Granularity.seconds)


class BaseDocument(Document):
    class Settings:
        keep_nulls = get_settings().beanie_default_settings.keep_nulls
        is_root = True
        with_children = get_settings().beanie_default_settings.with_children
        use_cache = get_settings().beanie_default_settings.use_cache
        cache_expiration_time = get_settings().beanie_default_settings.cache_expiration_timedelta
        cache_capacity = get_settings().beanie_default_settings.cache_capacity


class EmailBase(SQLModel):
    recipients: Annotated[list[EmailStr], Field(title="List of recipients emails")]
    subject: Annotated[str, Field(title="Message subject")]
    body_params: Annotated[dict[str, Any], Field(title="Key-value pairs used to populate template")]
    template_id: Annotated[
        int, Field(title="Email template id", description="Template will be populated with data from 'body_params'")
    ]
    subtype: Annotated[MessageType, Field(title="Message type")]


class EmailOutboxMessage(BaseDocument):
    created_at: Annotated[datetime, Field(default_factory=_generate_datetime, title="Date of creation")]
    is_processed: Annotated[bool, Field(title="Is mail already processed?")] = False
    email: Annotated[EmailBase, Field(title="Email data to send")]

    class Settings:
        name = "outbox_emails"
        is_root = False
        timeseries = _timeseries_settings("created_at")
