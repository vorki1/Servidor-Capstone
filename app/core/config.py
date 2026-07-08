from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    METRIS_BASE_URI: str = os.getenv("METRIS_BASE_URI")
    METRIS_TOKEN: str = os.getenv("METRIS_TOKEN")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    URL_API_AWS: str = os.getenv("URL_API_AWS")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME")
    ADMIN_NAME: str = os.getenv("ADMIN_NAME")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD")
    USUARIO_USERNAME: str = os.getenv("USUARIO_USERNAME")
    USUARIO_NAME: str = os.getenv("USUARIO_NAME")
    USUARIO_PASSWORD: str = os.getenv("USUARIO_PASSWORD")


    class Config:
        env_file = ".env"

settings = Settings()