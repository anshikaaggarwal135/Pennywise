from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pennywise API"
    secret_key: str = "change-this-secret-key-before-deployment"
    access_token_expire_minutes: int = 60 * 24

    # SQLite database
    database_url: str = "sqlite:///./expense_tracker.db"

    # Frontend URLs allowed to access the API
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def allowed_origins(self):
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()