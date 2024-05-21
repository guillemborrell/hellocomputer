from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anyscale_api_key: str = "Awesome API"
    gcs_access: str = "access"
    gcs_secret: str = "secret"
    gcs_bucketname: str = "bucket"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
