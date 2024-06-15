from starlette.templating import Jinja2Templates

from core import get_settings
from db import EmailBase


templates = Jinja2Templates(directory=get_settings().paths.mail_templates_dir)


class EmailSchema(EmailBase):
    model_config = get_settings().default_model_config.config
