from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL


def ajustar_database_url(database_url: str) -> str:
    """
    Ajusta a URL do banco caso o serviço de hospedagem envie
    no formato postgres:// em vez de postgresql://.
    """
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)

    return database_url


DATABASE_URL_AJUSTADA = ajustar_database_url(DATABASE_URL)

connect_args = {}

if DATABASE_URL_AJUSTADA.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }

engine = create_engine(
    DATABASE_URL_AJUSTADA,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()