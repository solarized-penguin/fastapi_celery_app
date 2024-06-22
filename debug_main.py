import logging
import asyncio
import uvicorn

from clients import Mailer, MailMessage
from core import get_settings

if __name__ == "__main__":
    # print("Running with settings: ", get_settings().model_dump_json(indent=2))
    #
    # print(
    #     dict(
    #         jetbrains_mono_regular_font_url=get_settings().resources.jetbrains_mono_regular_font_url,
    #         jetbrains_mono_extra_bold_font_url=get_settings().resources.jetbrains_mono_extra_bold_font_url,
    #         bookstore_mail_logo_url=get_settings().resources.bookstore_mail_logo_url,
    #     )
    # )
    # m = Mailer()
    # msg = MailMessage.create(
    #     recipients=["maciej.tomaszek@gmail.com"],
    #     subject="Test mail",
    #     body_params=dict(bookstore_api_email_verification_url="http://0.0.0.0:8081/test_auth"),
    #     template_name="email-verification.html",
    # )
    # print("\n\n\n Mailer: ", m, " msg: ", msg, "\n\n\n\n")
    # func = m.send_with_template(msg)
    #
    # asyncio.run(func)

    config = uvicorn.Config(
        "celery_app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level=logging.DEBUG,
        reload_dirs="celery_app",
        access_log=True,
        loop="asyncio",
    )
    server = uvicorn.Server(config)
    server.run()
