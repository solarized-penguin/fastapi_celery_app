import logging
import nest_asyncio
import uvicorn

from celery_app.core import get_settings

if __name__ == "__main__":
    # print("Running with settings: ", get_settings().model_dump_json(indent=2))
    #
    # print(get_settings().mongo_db.mongo_dsn)
    nest_asyncio.apply()
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
