from sqlalchemy.orm import Session

from app.models import Mensagem, FAQ, Usuario
from app.schemas import FAQCriar
from app.auth import gerar_hash_senha
from app.config import ADMIN_USERNAME, ADMIN_PASSWORD


def salvar_mensagem(
    db: Session,
    telefone: str,
    mensagem: str,
    resposta: str,
    status: str = "respondido"
):
    nova_mensagem = Mensagem(
        telefone=telefone,
        mensagem_recebida=mensagem,
        resposta_enviada=resposta,
        status=status
    )

    db.add(nova_mensagem)
    db.commit()
    db.refresh(nova_mensagem)

    return nova_mensagem


def listar_mensagens(db: Session):
    return db.query(Mensagem).order_by(Mensagem.id.desc()).all()


def excluir_mensagem(db: Session, mensagem_id: int):
    mensagem = db.query(Mensagem).filter(Mensagem.id == mensagem_id).first()

    if mensagem is None:
        return None

    db.delete(mensagem)
    db.commit()

    return mensagem


def limpar_mensagens(db: Session):
    total = db.query(Mensagem).delete()
    db.commit()

    return total


def atualizar_status_mensagem(db: Session, mensagem_id: int, novo_status: str):
    mensagem = db.query(Mensagem).filter(Mensagem.id == mensagem_id).first()

    if mensagem is None:
        return None

    mensagem.status = novo_status

    db.commit()
    db.refresh(mensagem)

    return mensagem


def criar_faq(db: Session, faq: FAQCriar):
    nova_faq = FAQ(
        palavra_chave=faq.palavra_chave.lower().strip(),
        pergunta=faq.pergunta,
        resposta=faq.resposta
    )

    db.add(nova_faq)
    db.commit()
    db.refresh(nova_faq)

    return nova_faq


def listar_faqs(db: Session):
    return db.query(FAQ).order_by(FAQ.id.desc()).all()


def excluir_faq(db: Session, faq_id: int):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()

    if faq is None:
        return None

    db.delete(faq)
    db.commit()

    return faq


def buscar_usuario_por_username(db: Session, username: str):
    return db.query(Usuario).filter(Usuario.username == username).first()


def criar_usuario(
    db: Session,
    nome: str,
    username: str,
    senha: str,
    perfil: str = "admin"
):
    senha_hash = gerar_hash_senha(senha)

    novo_usuario = Usuario(
        nome=nome,
        username=username,
        senha_hash=senha_hash,
        perfil=perfil
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


def garantir_admin_padrao(db: Session):
    usuario = buscar_usuario_por_username(db, ADMIN_USERNAME)

    if usuario:
        return usuario

    return criar_usuario(
        db=db,
        nome="Administrador",
        username=ADMIN_USERNAME,
        senha=ADMIN_PASSWORD,
        perfil="admin"
    )

def listar_usuarios(db: Session):
    return db.query(Usuario).order_by(Usuario.id.desc()).all()


def buscar_usuario_por_id(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def excluir_usuario(db: Session, usuario_id: int):
    usuario = buscar_usuario_por_id(db, usuario_id)

    if usuario is None:
        return None

    db.delete(usuario)
    db.commit()

    return usuario


def atualizar_senha_usuario(db: Session, usuario_id: int, nova_senha: str):
    usuario = buscar_usuario_por_id(db, usuario_id)

    if usuario is None:
        return None

    usuario.senha_hash = gerar_hash_senha(nova_senha)

    db.commit()
    db.refresh(usuario)

    return usuario


def atualizar_usuario(db: Session, usuario_id: int, nome: str, username: str, perfil: str):
    usuario = buscar_usuario_por_id(db, usuario_id)

    if usuario is None:
        return None

    usuario.nome = nome
    usuario.username = username
    usuario.perfil = perfil

    db.commit()
    db.refresh(usuario)

    return usuario
