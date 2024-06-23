from typing import Any

from jinja2 import meta
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from core import get_settings


def _create_jinja_templates() -> Jinja2Templates:
    def _context(request: Request) -> dict[str, Any]:
        return {"request": request, "app": request.app}

    jinja_templates = Jinja2Templates(
        env=get_settings().resources.jinja_env,
        context_processors=[_context],
    )

    return jinja_templates


templates: Jinja2Templates = _create_jinja_templates()


def extract_template_variables(template_name: str) -> list[str]:
    env = get_settings().resources.jinja_env
    template_source = env.loader.get_source(env, template_name)
    parsed_content = env.parse(template_source)
    return list(meta.find_undeclared_variables(parsed_content))
