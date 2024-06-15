from fastapi import FastAPI
from starlette.staticfiles import StaticFiles


def create_app() -> FastAPI:
    from core import get_settings
    from db import db_init_lifespan
    from routers import register_routers

    app = FastAPI(
        title=get_settings().api.title,
        debug=get_settings().api.debug,
        version=get_settings().api.version,
        openapi_url=get_settings().api.openapi_url,
        docs_url=get_settings().api.docs_url,
        redoc_url=get_settings().api.redoc_url,
        swagger_ui_oauth2_redirect_url=get_settings().api.swagger_ui_oauth2_redirect_url,
        include_in_schema=get_settings().api.include_in_schema,
        lifespan=db_init_lifespan,
    )

    app.mount(path="/static", app=StaticFiles(directory=get_settings().paths.static_dir), name="static")

    register_routers(app)

    return app
