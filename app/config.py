import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "troque-essa-chave-secreta")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "123456")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./softbot.db")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5500")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500"
)

CORS_ORIGINS_LIST = [
    origem.strip()
    for origem in CORS_ORIGINS.split(",")
    if origem.strip()
]

APP_NAME = os.getenv("APP_NAME", "SoftBot Pro WhatsApp")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "development")
APP_AUTHOR = os.getenv("APP_AUTHOR", "Kauã Lucas")
