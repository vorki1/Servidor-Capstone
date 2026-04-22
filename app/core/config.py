from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    METRIS_BASE_URI: str = os.getenv("METRIS_BASE_URI")
    METRIS_TOKEN: str = os.getenv("METRIS_TOKEN")

settings = Settings()