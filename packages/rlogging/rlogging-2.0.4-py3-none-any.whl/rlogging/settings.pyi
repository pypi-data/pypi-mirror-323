from _typeshed import Incomplete
from pydantic_settings import BaseSettings
from typing import Any

ENV_FILE: Incomplete

class AppBaseSettings(BaseSettings):
    model_config: Incomplete
    DEBUG: bool
    DEVELOP: bool
    NAME: str
    VERSION: str
    ENVIRONMENT: str
    LOGGING_TEXT_FORMAT: str
    LOGGING_MODULES: list[str]
    LOGGING_LEVEL: str
    LOGGING_DEPS_LEVEL: str
    MODULE_PATH: str | None
    def get_service_info(self) -> dict[str, Any]: ...

APP: Incomplete
