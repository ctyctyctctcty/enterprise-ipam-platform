from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise IP Management Platform"
    app_env: str = "local"
    debug: bool = True
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 480
    database_url: str = "sqlite:///./enterprise_ipam.db"
    admin_title: str = "Enterprise IPAM Admin"

    postgres_server: str = "db"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "enterprise_ipam"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()

