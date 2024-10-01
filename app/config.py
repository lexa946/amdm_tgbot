from pydantic import model_validator
from pydantic_settings import BaseSettings
from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    DATABASE_URL: str

    BOT_TOKEN: str
    MAIN_URL_AMDM:str


    @model_validator(mode="before")
    def get_database_url(cls, values):
        values["DATABASE_URL"] = (f"postgresql://{values['DB_USER']}:{values['DB_PASS']}"
                                  f"@{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}")
        return values


    class Config:
        env_file = '.env'


settings = Settings()


engine = create_engine(settings.DATABASE_URL)
session_maker = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass