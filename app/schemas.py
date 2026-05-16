from pydantic import BaseModel


class MensagemEntrada(BaseModel):
    telefone: str
    mensagem: str


class MensagemSaida(BaseModel):
    telefone: str
    resposta: str
    status: str


class FAQCriar(BaseModel):
    palavra_chave: str
    pergunta: str
    resposta: str


class StatusAtualizar(BaseModel):
    status: str


class LoginEntrada(BaseModel):
    username: str
    password: str


class TokenSaida(BaseModel):
    access_token: str
    token_type: str
    usuario: str
    perfil: str

class UsuarioCriar(BaseModel):
    nome: str
    username: str
    senha: str
    perfil: str = "atendente"


class UsuarioSenhaAtualizar(BaseModel):
    nova_senha: str


class MinhaSenhaAtualizar(BaseModel):
    senha_atual: str
    nova_senha: str


class UsuarioAtualizar(BaseModel):
    nome: str
    username: str
    perfil: str
