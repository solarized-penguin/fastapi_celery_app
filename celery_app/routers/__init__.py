from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    from .mailing import mail_router

    app.include_router(mail_router)
