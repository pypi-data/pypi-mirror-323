from _typeshed import Incomplete
from pydantic_settings import BaseSettings
from rlogging.settings import AppBaseSettings as AppBaseSettings, ENV_FILE as ENV_FILE

class SentrySettings(BaseSettings):
    model_config: Incomplete
    DSN: str | None
    SAMPLE_RATE: float
    TRACES_SAMPLE_RATE: float
    PROFILES_SAMPLE_RATE: float

def init() -> None: ...
