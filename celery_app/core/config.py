from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin

from fastapi_mail import ConnectionConfig
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import MongoDsn, SecretStr, Field, EmailStr, ConfigDict, AnyUrl, DirectoryPath
from pydantic_settings import SettingsConfigDict, BaseSettings

_ROOT_DIR = Path(__file__).parent.parent
assert _ROOT_DIR.exists() and _ROOT_DIR.is_dir()

_STATIC_DIR = _ROOT_DIR / "static"
assert _STATIC_DIR.exists() and _STATIC_DIR.is_dir()

_MAIL_TEMPLATES_DIR = _STATIC_DIR / "mail_templates"
assert _MAIL_TEMPLATES_DIR.exists() and _MAIL_TEMPLATES_DIR.is_dir()

_IMAGES_DIR = _STATIC_DIR / "images"
assert _IMAGES_DIR.exists() and _IMAGES_DIR.is_dir()

_FONTS_DIR = _STATIC_DIR / "fonts"
assert _FONTS_DIR.exists() and _FONTS_DIR.is_dir()


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False, env_file=(".env.debug", ".env.dev"), env_file_encoding="utf-8", extra="ignore"
    )


class ResourceSettings(BaseConfig, env_prefix="CELERY_RESOURCES_"):
    jinja_templates_auto_reload: bool
    base_url: AnyUrl
    jinja_templates_enable_async: bool
    jinja_templates_optimized: bool
    jinja_templates_autoescape: bool
    jinja_templates_cache_size: int
    jinja_templates_trim_blocks: bool
    jinja_templates_lstrip_blocks: bool
    jinja_templates_newline_sequence: Literal["\n", "\r\n", "\r"]
    jinja_templates_keep_trailing_newline: bool

    @property
    def root_dir(self) -> Path:
        return _ROOT_DIR

    @property
    def static_dir(self) -> Path:
        return _STATIC_DIR

    @property
    def mail_templates_dir(self) -> Path:
        return _MAIL_TEMPLATES_DIR

    @property
    def images_dir(self) -> Path:
        return _IMAGES_DIR

    @property
    def fonts_dir(self) -> Path:
        return _FONTS_DIR

    @property
    def jetbrains_mono_regular_font_url(self) -> AnyUrl:
        return AnyUrl(urljoin(self.base_url.unicode_string(), "static/fonts/JetBrainsMono-Regular.woff2"))

    @property
    def jetbrains_mono_extra_bold_font_url(self) -> AnyUrl:
        return AnyUrl(urljoin(self.base_url.unicode_string(), "static/fonts/JetBrainsMono-ExtraBold.woff2"))

    @property
    def jinja_env(self) -> Environment:
        env = Environment(
            trim_blocks=self.jinja_templates_trim_blocks,
            lstrip_blocks=self.jinja_templates_lstrip_blocks,
            newline_sequence=self.jinja_templates_newline_sequence,
            keep_trailing_newline=self.jinja_templates_keep_trailing_newline,
            optimized=self.jinja_templates_optimized,
            autoescape=self.jinja_templates_autoescape,
            loader=FileSystemLoader(searchpath=self.mail_templates_dir),
            cache_size=self.jinja_templates_cache_size,
            auto_reload=self.jinja_templates_auto_reload,
            enable_async=self.jinja_templates_enable_async,
        )
        env.globals.update(
            {
                "font_jet_brains_regular_url": self.jetbrains_mono_regular_font_url,
                "font_jet_brains_bold_url": self.jetbrains_mono_extra_bold_font_url,
                "fetch_image_by_name": self.fetch_image_by_name,
            }
        )
        return env

    def fetch_image_by_name(self, name: str) -> AnyUrl:
        return AnyUrl(urljoin(self.base_url.unicode_string(), f"static/images/{name}"))


class LoggingSettings(BaseConfig, env_prefix="CELERY_LOGGING_"):
    loki_endpoint: str
    loki_handler_version: str

    log_level: str
    log_format: str


class MailingSettings(BaseConfig, env_prefix="CELERY_TASKS_MAILING_"):
    username: str
    password: SecretStr
    server: str
    port: int
    debug: bool
    start_tls: bool
    mail_ssl_tls: bool
    mail_from: EmailStr
    mail_from_name: str
    timeout: int
    suppress_send: bool
    use_credentials: bool
    validate_certs: bool

    def connection_config(self, template_folder: DirectoryPath) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.username,
            MAIL_PASSWORD=self.password.get_secret_value(),
            MAIL_PORT=self.port,
            MAIL_SERVER=self.server,
            MAIL_STARTTLS=self.start_tls,
            MAIL_SSL_TLS=self.mail_ssl_tls,
            MAIL_DEBUG=self.debug,
            MAIL_FROM=self.mail_from,
            MAIL_FROM_NAME=self.mail_from_name,
            SUPPRESS_SEND=self.suppress_send,
            USE_CREDENTIALS=self.use_credentials,
            VALIDATE_CERTS=self.validate_certs,
            TIMEOUT=self.timeout,
            TEMPLATE_FOLDER=template_folder,
        )


class CeleryTasksSettings(BaseConfig):
    mailing: MailingSettings = MailingSettings()


class BeanieDocumentsSettings(BaseConfig, env_prefix="CELERY_BEANIE_DOCUMENTS_"):
    keep_nulls: bool
    with_children: bool
    use_cache: bool
    cache_expiration_time_seconds: int
    cache_capacity: int

    @property
    def cache_expiration_timedelta(self) -> timedelta:
        return timedelta(seconds=self.cache_expiration_time_seconds)


class MongoDbSettings(BaseConfig, env_prefix="CELERY_MONGO_DB_"):
    scheme: str
    host: str
    port: int
    username: str
    password: SecretStr
    path: str
    pool_size: int
    connect_timeout_ms: int
    socket_timeout_ms: int
    app_name: str = Field(..., alias="COMPOSE_PROJECT_NAME")
    multiprocessing_mode: bool
    causal_consistency: bool
    auth_source: str
    auth_mechanism: str

    @property
    def mongo_dsn(self) -> str:
        return MongoDsn.build(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password.get_secret_value(),
            path=self.path,
            query=f"maxPoolSize={self.pool_size}&appName={self.path}&connectTimeoutMS={self.connect_timeout_ms}"
            f"&socketTimeoutMS={self.socket_timeout_ms}"
            f"&authSource={self.auth_source}&authMechanism={self.auth_mechanism}",
        ).unicode_string()


class CeleryMailWorkerSettings(BaseConfig, env_prefix="CELERY_WORKER_MAIL_"):
    name: str


class ApiSettings(BaseConfig, env_prefix="CELERY_API_"):
    title: str
    version: str
    host: str
    port: int
    debug: bool
    openapi_url: str
    docs_url: str
    redoc_url: str
    swagger_ui_oauth2_redirect_url: str
    include_in_schema: bool


class WorkersSettings(BaseConfig):
    mail: CeleryMailWorkerSettings = CeleryMailWorkerSettings()


class RouterModelsDefaultConfigSettings(BaseConfig, env_prefix="CELERY_ROUTER_MODELS_DEFAULTS_"):
    str_strip_whitespace: bool
    extra: Literal["allow", "ignore", "forbid"]
    use_enum_values: bool
    hide_input_in_errors: bool
    cache_strings: Literal["all", "keys", "none"]

    @property
    def config(self) -> ConfigDict:
        return ConfigDict(
            str_strip_whitespace=self.str_strip_whitespace,
            extra=self.extra,
            use_enum_values=self.use_enum_values,
            hide_input_in_errors=self.hide_input_in_errors,
            cache_strings=self.cache_strings,
        )


class Settings(BaseConfig):
    api: ApiSettings = ApiSettings()
    mongo_db: MongoDbSettings = MongoDbSettings()
    workers: WorkersSettings = WorkersSettings()
    tasks: CeleryTasksSettings = CeleryTasksSettings()
    logging: LoggingSettings = LoggingSettings()
    default_model_config: RouterModelsDefaultConfigSettings = RouterModelsDefaultConfigSettings()
    beanie_default_settings: BeanieDocumentsSettings = BeanieDocumentsSettings()
    resources: ResourceSettings = ResourceSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
