from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    DATA_URL: str
    JSON_SERVER_PATH: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
