from typing import Annotated, Any

from fastapi_mail import MessageType
from jinja2 import Environment
from pydantic import EmailStr
from sqlmodel import Field
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from core import get_settings
from db import EmailBase


def _create_jinja_templates() -> Jinja2Templates:

    def _app_context(request: Request) -> dict[str, Any]:
        return {"app": request.app}

    jinja_templates = Jinja2Templates(
        env=get_settings().resources.jinja_env,
        autoescape=get_settings().resources.jinja_templates_autoescape,
        auto_reload=get_settings().resources.jinja_templates_auto_reload,
        context_processors=[_app_context],
    )

    return jinja_templates


templates: Jinja2Templates = _create_jinja_templates()


class EmailSchema(EmailBase):
    model_config = get_settings().default_model_config.config

    @classmethod
    def create_schema(
        cls,
        recipients: Annotated[list[EmailStr], Field(title="List of recipients emails", unique=True)],
        subject: Annotated[str, Field(title="Message subject")],
        template_name: Annotated[
            str,
            Field(title="Email template name", description="Template will be populated with data from 'body_params'"),
        ],
        subtype: Annotated[MessageType, Field(title="Message type")],
        body_params: Annotated[dict[str, Any], Field(title="Key-value pairs used to populate template")],
    ) -> dict[str, Any]:
        return cls(
            body_params=body_params,
            recipients=recipients,
            subject=subject,
            template_name=template_name,
            subtype=subtype,
        )
