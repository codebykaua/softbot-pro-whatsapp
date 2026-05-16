from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.schemas import (
    MensagemEntrada,
    MensagemSaida,
    FAQCriar,
    StatusAtualizar,
    LoginEntrada,
    TokenSaida,
    UsuarioCriar,
    UsuarioSenhaAtualizar,
    MinhaSenhaAtualizar,
    UsuarioAtualizar
)
from app.bot import gerar_resposta_com_faq
from app.auth import verificar_senha, criar_token_acesso, decodificar_token
from app.config import (
    CORS_ORIGINS_LIST,
    APP_NAME,
    APP_VERSION,
    APP_ENV,
    APP_AUTHOR,
    WHATSAPP_TOKEN,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_VERIFY_TOKEN,
    WHATSAPP_API_VERSION
)
from app.whatsapp_service import extrair_mensagem_whatsapp, enviar_mensagem_whatsapp
from app import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    description="API de automação de atendimento para empresa de software",
    version=APP_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def iniciar_sistema():
    db = SessionLocal()

    try:
        crud.garantir_admin_padrao(db)
    finally:
        db.close()


def get_usuario_logado(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decodificar_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado."
        )

    username = payload.get("sub")

    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido."
        )

    usuario = crud.buscar_usuario_por_username(db, username)

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado."
        )

    return usuario

def exigir_admin(usuario=Depends(get_usuario_logado)):
    if usuario.perfil != "admin":
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem executar esta ação."
        )

    return usuario


@app.get("/")
def home():
    return {
        "mensagem": "SoftBot Pro API funcionando com sucesso!"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "api": APP_NAME,
            "database": "online"
        }
    except Exception:
        return {
            "status": "error",
            "api": APP_NAME,
            "database": "offline"
        }


@app.get("/info")
def info_api():
    return {
        "nome": APP_NAME,
        "versao": APP_VERSION,
        "ambiente": APP_ENV,
        "autor": APP_AUTHOR
    }


@app.post("/login", response_model=TokenSaida)
def login(dados: LoginEntrada, db: Session = Depends(get_db)):
    usuario = crud.buscar_usuario_por_username(db, dados.username)

    if usuario is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos."
        )

    senha_valida = verificar_senha(
        senha=dados.password,
        senha_hash=usuario.senha_hash
    )

    if not senha_valida:
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos."
        )

    token = criar_token_acesso({
        "sub": usuario.username,
        "perfil": usuario.perfil
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario.username,
        "perfil": usuario.perfil
    }


@app.post("/webhook", response_model=MensagemSaida)
def receber_mensagem(dados: MensagemEntrada, db: Session = Depends(get_db)):
    faqs = crud.listar_faqs(db)
    resposta, status = gerar_resposta_com_faq(dados.mensagem, faqs)

    crud.salvar_mensagem(
        db=db,
        telefone=dados.telefone,
        mensagem=dados.mensagem,
        resposta=resposta,
        status=status
    )

    return {
        "telefone": dados.telefone,
        "resposta": resposta,
        "status": status
    }


@app.get("/mensagens")
def ver_mensagens(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    mensagens = crud.listar_mensagens(db)
    return mensagens


@app.delete("/mensagens")
def deletar_todas_mensagens(
    db: Session = Depends(get_db),
    usuario=Depends(exigir_admin)
):
    total = crud.limpar_mensagens(db)

    return {
        "mensagem": "Histórico de mensagens limpo com sucesso!",
        "total_excluido": total
    }


@app.delete("/mensagens/{mensagem_id}")
def deletar_mensagem(
    mensagem_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_admin)
):
    mensagem = crud.excluir_mensagem(db, mensagem_id)

    if mensagem is None:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada.")

    return {
        "mensagem": "Mensagem excluída com sucesso!",
        "id": mensagem_id
    }


@app.put("/mensagens/{mensagem_id}/status")
def alterar_status_mensagem(
    mensagem_id: int,
    dados: StatusAtualizar,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    status_permitidos = ["respondido", "pendente", "encaminhado", "finalizado"]

    if dados.status not in status_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Status inválido. Use: respondido, pendente, encaminhado ou finalizado."
        )

    mensagem = crud.atualizar_status_mensagem(db, mensagem_id, dados.status)

    if mensagem is None:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada.")

    return {
        "mensagem": "Status atualizado com sucesso!",
        "id": mensagem_id,
        "novo_status": dados.status
    }


@app.post("/faqs")
def cadastrar_faq(
    faq: FAQCriar,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_admin)
):
    nova_faq = crud.criar_faq(db, faq)
    return nova_faq


@app.get("/faqs")
def ver_faqs(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    faqs = crud.listar_faqs(db)
    return faqs


@app.delete("/faqs/{faq_id}")
def deletar_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(exigir_admin)
):
    faq = crud.excluir_faq(db, faq_id)

    if faq is None:
        raise HTTPException(status_code=404, detail="FAQ não encontrada.")

    return {
        "mensagem": "FAQ excluída com sucesso!",
        "id": faq_id
    }

@app.post("/usuarios")
def cadastrar_usuario(
    dados: UsuarioCriar,
    db: Session = Depends(get_db),
    usuario_logado=Depends(exigir_admin)
):
    perfis_permitidos = ["admin", "atendente", "suporte"]

    if dados.perfil not in perfis_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Perfil inválido. Use: admin, atendente ou suporte."
        )

    usuario_existente = crud.buscar_usuario_por_username(db, dados.username)

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com esse username."
        )

    novo_usuario = crud.criar_usuario(
        db=db,
        nome=dados.nome,
        username=dados.username,
        senha=dados.senha,
        perfil=dados.perfil
    )

    return {
        "mensagem": "Usuário criado com sucesso!",
        "id": novo_usuario.id,
        "nome": novo_usuario.nome,
        "username": novo_usuario.username,
        "perfil": novo_usuario.perfil
    }


@app.get("/usuarios")
def ver_usuarios(
    db: Session = Depends(get_db),
    usuario_logado=Depends(exigir_admin)
):
    usuarios = crud.listar_usuarios(db)

    return [
        {
            "id": usuario.id,
            "nome": usuario.nome,
            "username": usuario.username,
            "perfil": usuario.perfil,
            "criado_em": usuario.criado_em
        }
        for usuario in usuarios
    ]


@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_logado=Depends(exigir_admin)
):
    if usuario_logado.id == usuario_id:
        raise HTTPException(
            status_code=400,
            detail="Você não pode excluir o próprio usuário logado."
        )

    usuario = crud.excluir_usuario(db, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    return {
        "mensagem": "Usuário excluído com sucesso!",
        "id": usuario_id
    }


@app.put("/usuarios/{usuario_id}/senha")
def alterar_senha_usuario(
    usuario_id: int,
    dados: UsuarioSenhaAtualizar,
    db: Session = Depends(get_db),
    usuario_logado=Depends(exigir_admin)
):
    if len(dados.nova_senha) < 6:
        raise HTTPException(
            status_code=400,
            detail="A nova senha deve ter pelo menos 6 caracteres."
        )

    usuario = crud.atualizar_senha_usuario(
        db=db,
        usuario_id=usuario_id,
        nova_senha=dados.nova_senha
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    return {
        "mensagem": "Senha atualizada com sucesso!",
        "id": usuario_id
    }


@app.get("/me")
def ver_meu_perfil(usuario=Depends(get_usuario_logado)):
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "username": usuario.username,
        "perfil": usuario.perfil,
        "criado_em": usuario.criado_em
    }


@app.put("/me/senha")
def alterar_minha_senha(
    dados: MinhaSenhaAtualizar,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    senha_valida = verificar_senha(
        senha=dados.senha_atual,
        senha_hash=usuario.senha_hash
    )

    if not senha_valida:
        raise HTTPException(
            status_code=400,
            detail="Senha atual incorreta."
        )

    if len(dados.nova_senha) < 6:
        raise HTTPException(
            status_code=400,
            detail="A nova senha deve ter pelo menos 6 caracteres."
        )

    crud.atualizar_senha_usuario(
        db=db,
        usuario_id=usuario.id,
        nova_senha=dados.nova_senha
    )

    return {
        "mensagem": "Senha alterada com sucesso!"
    }


@app.put("/usuarios/{usuario_id}")
def editar_usuario(
    usuario_id: int,
    dados: UsuarioAtualizar,
    db: Session = Depends(get_db),
    usuario_logado=Depends(exigir_admin)
):
    perfis_permitidos = ["admin", "atendente", "suporte"]

    if dados.perfil not in perfis_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Perfil inválido. Use: admin, atendente ou suporte."
        )

    usuario_existente = crud.buscar_usuario_por_username(db, dados.username)

    if usuario_existente and usuario_existente.id != usuario_id:
        raise HTTPException(
            status_code=400,
            detail="Já existe outro usuário com esse username."
        )

    usuario = crud.atualizar_usuario(
        db=db,
        usuario_id=usuario_id,
        nome=dados.nome,
        username=dados.username,
        perfil=dados.perfil
    )

    if usuario is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
        )

    return {
        "mensagem": "Usuário atualizado com sucesso!",
        "id": usuario.id,
        "nome": usuario.nome,
        "username": usuario.username,
        "perfil": usuario.perfil
    }


@app.get("/whatsapp/webhook")
def verificar_webhook_whatsapp(request: Request):
    """
    Rota usada para verificação do webhook do WhatsApp.
    """

    hub_mode = request.query_params.get("hub.mode") or request.query_params.get("hub_mode")
    hub_verify_token = (
        request.query_params.get("hub.verify_token") or
        request.query_params.get("hub_verify_token")
    )
    hub_challenge = (
        request.query_params.get("hub.challenge") or
        request.query_params.get("hub_challenge")
    )

    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)

    raise HTTPException(
        status_code=403,
        detail="Token de verificação inválido."
    )


@app.post("/whatsapp/webhook")
async def receber_webhook_whatsapp(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Rota preparada para receber mensagens reais do WhatsApp.
    """

    payload = await request.json()

    dados_mensagem = extrair_mensagem_whatsapp(payload)

    if dados_mensagem is None:
        return {
            "status": "ignorado",
            "mensagem": "Nenhuma mensagem de texto encontrada no payload."
        }

    telefone = dados_mensagem["telefone"]
    mensagem_recebida = dados_mensagem["mensagem"]
    tipo_mensagem = dados_mensagem.get("tipo", "unknown")

    print("\n[WHATSAPP] Mensagem recebida")
    print(f"Telefone: {telefone}")
    print(f"Tipo: {tipo_mensagem}")
    print(f"Mensagem: {mensagem_recebida}")

    if tipo_mensagem != "text":
        resposta = (
            "Recebemos sua mensagem, mas no momento o atendimento automático "
            "responde apenas mensagens de texto. Por favor, envie sua dúvida por escrito."
        )
        status = "pendente"
    else:
        faqs = crud.listar_faqs(db)
        resposta, status = gerar_resposta_com_faq(mensagem_recebida, faqs)

    crud.salvar_mensagem(
        db=db,
        telefone=telefone,
        mensagem=mensagem_recebida,
        resposta=resposta,
        status=status
    )

    resultado_envio = enviar_mensagem_whatsapp(
        telefone=telefone,
        mensagem=resposta
    )

    print(f"Resposta gerada: {resposta}")
    print(f"Status atendimento: {status}")
    print(f"Envio WhatsApp: {resultado_envio}")
    print("[WHATSAPP] Processamento finalizado\n")

    return {
        "status": "processado",
        "telefone": telefone,
        "mensagem_recebida": mensagem_recebida,
        "tipo_mensagem": tipo_mensagem,
        "resposta_gerada": resposta,
        "status_atendimento": status,
        "envio_whatsapp": resultado_envio
    }


@app.get("/whatsapp/status")
def status_integracao_whatsapp(usuario=Depends(get_usuario_logado)):
    token_configurado = bool(WHATSAPP_TOKEN)
    phone_id_configurado = bool(WHATSAPP_PHONE_NUMBER_ID)
    verify_token_configurado = bool(WHATSAPP_VERIFY_TOKEN)

    pronto_para_envio = token_configurado and phone_id_configurado

    modo = "produção" if pronto_para_envio else "simulação"

    return {
        "whatsapp_token_configurado": token_configurado,
        "phone_number_id_configurado": phone_id_configurado,
        "verify_token_configurado": verify_token_configurado,
        "api_version": WHATSAPP_API_VERSION,
        "modo": modo,
        "pronto_para_envio": pronto_para_envio,
        "mensagem": (
            "Integração pronta para envio real."
            if pronto_para_envio
            else "Integração em modo de simulação. Configure token e Phone Number ID para envio real."
        )
    }
    return {
        "mensagem": "Senha do admin resetada com sucesso.",
        "username": "admin",
        "senha": "123456"
    }
