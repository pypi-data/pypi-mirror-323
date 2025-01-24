from typing import Dict

from openg2p_fastapi_common.config import Settings as BaseSettings
from pydantic_settings import SettingsConfigDict

from . import __version__


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="registry_celery_beat_", env_file=".env", extra="allow"
    )
    openapi_title: str = "OpenG2P Registry Celery Tasks"
    openapi_description: str = """
        Celery tasks for OpenG2P Registry
        ***********************************
        Further details goes here
        ***********************************
        """
    openapi_version: str = __version__

    db_dbname: str = "registrydb"
    db_driver: str = "postgresql"

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_backend_url: str = "redis://localhost:6379/0"

    registry_beat_producer_frequency: int = 10
    worker_type_max_attempts: Dict[str, int]
    batch_size: int = 10000
