import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DIVAR_API_KEY = os.getenv("DIVAR_API_KEY")
    DIVAR_APP_SLUG = os.getenv("DIVAR_APP_SLUG")
