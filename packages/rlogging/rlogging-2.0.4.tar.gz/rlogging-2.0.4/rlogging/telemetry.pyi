from _typeshed import Incomplete
from rlogging import settings as settings
from rlogging.utils import flatten_dict as flatten_dict

logger: Incomplete

class OtelSettings(settings.BaseSettings):
    model_config: Incomplete
    TRACES_EXPORT_OTLP_ENDPOINT: str
    TRACES_EXPORT_INTERVAL: float
    TRACES_EXPORT_TIMEOUT: float
    METRICS_EXPORT_OTLP_ENDPOINT: str
    METRICS_EXPORT_INTERVAL: float
    METRICS_EXPORT_TIMEOUT: float

OTEL: Incomplete

def init_telemetry() -> None: ...
