from typing import Annotated, Any

from fastapi_mail import MessageType
from jinja2 import TemplateNotFound
from pydantic import EmailStr, model_validator
from sqlmodel import Field, SQLModel

from core import get_settings
from .funcs import templates, extract_template_variables


class EmailSchema(SQLModel):
    model_config = get_settings().default_model_config.config

    recipients: Annotated[list[EmailStr], Field(title="List of recipients emails", unique=True)]
    subject: Annotated[str | None, Field(title="Message subject")]
    template_name: Annotated[
        str | None,
        Field(title="Email template name", description="Template will be populated with data from 'body_params'"),
    ]
    body_params: Annotated[dict[str, Any] | None, Field(title="Key-value pairs used to populate template")]
    body: Annotated[
        str | None, Field(title="Full email body", description="Provide full email body instead using a template")
    ]
    subtype: Annotated[MessageType, Field(title="Message type")]

    async def dump_message(self) -> dict[str, Any]:
        self.body = self.body if self.body else await self._create_template()

        return dict(recipients=self.recipients, subject=self.subject, subtype=self.subtype, body=self.body)

    @model_validator(mode="after")
    def validate_model(self) -> None:
        if self.template_name and self.body:
            raise ValueError("You can either use template or provide full body, not both")
        if self.template_name and not self._does_template_exist():
            raise ValueError(f"Template '{self.template_name}' does not exist")
        if self.template_name and not self.body_params:
            template_vars = extract_template_variables(self.template_name)
            if template_vars:
                raise ValueError(f"Template '{self.template_name}' requires following body parameters: {template_vars}")
        return self

    def _does_template_exist(self) -> bool:
        try:
            templates.get_template(self.template_name)
        except TemplateNotFound:
            return False
        return True

    async def _create_template(self) -> str:
        template = templates.get_template(self.template_name)
        return await template.render_async(**self.body_params) if self.body_params else await template.render_async()

    @classmethod
    def create_schema(
        cls,
        body_params: Annotated[dict[str, Any], Field(title="Key-value pairs used to populate template")],
        recipients: Annotated[list[EmailStr], Field(title="List of recipients emails", unique=True)],
        subject: Annotated[str, Field(title="Message subject")] = None,
        template_name: Annotated[
            str,
            Field(title="Email template name", description="Template will be populated with data from 'body_params'"),
        ] = None,
        subtype: Annotated[MessageType, Field(title="Message type")] = MessageType.html,
        body: Annotated[
            str | None, Field(title="Full email body", description="Provide full email body instead using a template")
        ] = None,
    ) -> "EmailSchema":
        return cls(
            recipients=recipients,
            subject=subject,
            subtype=subtype,
            template_name=template_name,
            body_params=body_params,
            body=body,
        )
