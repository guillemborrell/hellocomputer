from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    base_url: str = "http://localhost:8000"
    llm_api_key: str = "Awesome API"
    llm_base_url: str = "Awessome Endpoint"
    gcs_access: str = "access"
    gcs_secret: str = "secret"
    gcs_bucketname: str = "bucket"
    auth: bool = True
    auth0_client_id: str = ""
    auth0_client_secret: str = ""
    auth0_domain: str = ""
    app_secret_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
