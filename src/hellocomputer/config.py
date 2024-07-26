from enum import StrEnum
from pathlib import Path
from typing import Optional, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageEngines(StrEnum):
    local = "local"
    gcs = "GCS"


class Settings(BaseSettings):
    storage_engine: StorageEngines = "local"
    base_url: str = "http://localhost:8000"
    llm_api_key: str = "Awesome API"
    llm_base_url: Optional[str] = None
    gcs_access: Optional[str] = None
    gcs_secret: Optional[str] = None
    gcs_bucketname: Optional[str] = None
    path: Optional[Path] = None
    auth: bool = True
    auth0_client_id: Optional[str] = None
    auth0_client_secret: Optional[str] = None
    auth0_domain: Optional[str] = None
    app_secret_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def check_cloud_storage(self) -> Self:
        if self.storage_engine == StorageEngines.gcs:
            if any(
                (
                    self.gcs_access is None,
                    self.gcs_bucketname is None,
                    self.gcs_secret is None,
                )
            ):
                raise ValueError("Cloud storage configuration not provided")
        return self

    @model_validator(mode="after")
    def check_auth_config(self) -> Self:
        if not self.auth:
            if any(
                (
                    self.auth0_client_id is None,
                    self.auth0_client_secret is None,
                    self.auth0_domain is None,
                    self.app_secret_key is None,
                )
            ):
                raise ValueError("Auth is enabled but no auth config is providedc")

        return self

    @model_validator(mode="after")
    def check_local_storage(self) -> Self:
        if self.storage_engine == StorageEngines.local:
            if self.path is None:
                raise ValueError("Local storage requires a path")

        return self


settings = Settings()
