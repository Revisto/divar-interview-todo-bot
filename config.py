import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

    DIVAR_API_KEY = os.getenv("DIVAR_API_KEY")
    DIVAR_APP_SLUG = os.getenv("DIVAR_APP_SLUG")
    DIVAR_OAUTH_SECRET = os.getenv("DIVAR_OAUTH_SECRET", "")
    DIVAR_REDIRECT_URI = f"{BASE_URL}/divar/oauth/callback"
