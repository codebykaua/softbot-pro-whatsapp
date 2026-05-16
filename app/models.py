from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.database import Base


class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    telefone = Column(String(20), nullable=False)
    mensagem_recebida = Column(Text, nullable=False)
    resposta_enviada = Column(Text, nullable=False)
    status = Column(String(50), default="respondido")
    criado_em = Column(DateTime, default=datetime.utcnow)


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    palavra_chave = Column(String(100), nullable=False)
    pergunta = Column(Text, nullable=False)
    resposta = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=False, index=True)
    senha_hash = Column(Text, nullable=False)
    perfil = Column(String(50), default="admin")
    criado_em = Column(DateTime, default=datetime.utcnow)