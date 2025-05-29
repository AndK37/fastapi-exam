from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_NAME: str = 'default'
    JWT_SECRET_KEY: str = 'default'
    model_config = SettingsConfigDict(env_file='.env')
settings = Settings()