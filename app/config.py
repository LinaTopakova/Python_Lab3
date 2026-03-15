from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "My FastAPI Lab"
    admin_email: str
    items_per_page: int = 10

    model_config = SettingsConfigDict(env_file=".env")
    