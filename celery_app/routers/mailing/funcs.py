from typing import Any

from jinja2 import Environment, PackageLoader, meta
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from core import get_settings


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


def extract_template_variables(template_name: str) -> list[str]:
    env = get_settings().resources.jinja_env
    template_source = env.loader.get_source(env, template_name)
    parsed_content = env.parse(template_source)
    return list(meta.find_undeclared_variables(parsed_content))


def template_and_variables_to_html(template: str, variables: list[str]) -> str:
    return f"""
    {template}
    Variables to provide: {variables}
    """
