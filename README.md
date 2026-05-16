# SoftBot Pro WhatsApp

Sistema de automação de atendimento inspirado em WhatsApp Business, desenvolvido com Python, FastAPI, SQLite/PostgreSQL, HTML, CSS e JavaScript.

O projeto simula um bot de atendimento para uma empresa de software, permitindo responder mensagens automaticamente, cadastrar perguntas frequentes, acompanhar histórico de mensagens, gerenciar status de atendimento e controlar usuários do painel administrativo.

---

## Objetivo do projeto

O objetivo do SoftBot Pro WhatsApp é criar uma base profissional para automação de atendimento via WhatsApp, com foco em:

- simulação de mensagens recebidas;
- respostas automáticas;
- gerenciamento de perguntas frequentes;
- histórico de atendimentos;
- controle de status das mensagens;
- login com autenticação JWT;
- usuários com perfis diferentes;
- preparação para integração futura com WhatsApp Business Platform.

---

## Tecnologias utilizadas

### Back-end

- Python
- FastAPI
- Uvicorn
- SQLite
- PostgreSQL preparado
- SQLAlchemy
- Pydantic
- PyJWT
- python-dotenv
- requests

### Front-end

- HTML
- CSS
- JavaScript

### Ferramentas

- VS Code
- Git
- GitHub
- Swagger UI / FastAPI Docs

---

## Funcionalidades

### Bot e mensagens

- Simulação de mensagem recebida pelo WhatsApp
- Rota `/webhook` para processar mensagens simuladas
- Respostas automáticas
- Respostas com base em FAQs cadastradas
- Histórico de mensagens
- Status de atendimento

### FAQs

- Cadastro de perguntas frequentes
- Listagem de FAQs
- Exclusão de FAQs
- Respostas automáticas por palavra-chave

### Mensagens

- Listagem de mensagens recebidas
- Exclusão de mensagens
- Limpeza de histórico
- Alteração de status
- Busca e filtro por status

### Usuários

- Criação de usuários
- Listagem de usuários
- Edição de nome, username e perfil
- Exclusão de usuários
- Alteração de senha
- Busca e filtro por perfil
- Perfis: admin, atendente e suporte

### Perfil do usuário logado

- Visualização de nome, username, perfil e data de criação
- Alteração da própria senha

---

## Permissões por perfil

### Admin

O usuário admin pode:

- acessar todas as páginas;
- criar usuários;
- editar usuários;
- excluir usuários;
- alterar senha de usuários;
- criar FAQs;
- excluir FAQs;
- excluir mensagens;
- limpar histórico;
- alterar status;
- visualizar mensagens e FAQs.

### Atendente

O usuário atendente pode:

- visualizar mensagens;
- alterar status;
- visualizar FAQs.

O atendente não pode:

- gerenciar usuários;
- criar ou excluir FAQs;
- excluir mensagens;
- limpar histórico.

### Suporte

O usuário suporte pode:

- visualizar mensagens;
- alterar status;
- visualizar FAQs.

O suporte não pode:

- gerenciar usuários;
- criar ou excluir FAQs;
- excluir mensagens;
- limpar histórico.

---

## Integração com WhatsApp Business Platform

O projeto já possui uma estrutura preparada para futura integração com a API oficial do WhatsApp Business Platform.

Atualmente, a integração está em modo de preparação e testes, utilizando payloads simulados parecidos com os enviados pela Meta.

### Arquivos relacionados

```text
app/whatsapp_service.py
tests/payload_whatsapp_texto.json
tests/payload_whatsapp_imagem.json
```

### Rotas criadas

```text
GET /whatsapp/webhook
POST /whatsapp/webhook
```

### Verificação do webhook

A rota `GET /whatsapp/webhook` é usada para validar o webhook configurado na Meta.

Exemplo local:

```text
http://127.0.0.1:8000/whatsapp/webhook?hub_mode=subscribe&hub_verify_token=softbot_verify_token_123&hub_challenge=12345
```

Resposta esperada:

```text
12345
```

### Recebimento de mensagens

A rota `POST /whatsapp/webhook` recebe mensagens em formato parecido com o payload real do WhatsApp Cloud API.

Ela consegue:

- extrair o telefone do cliente;
- identificar o tipo da mensagem;
- processar mensagens de texto;
- tratar mensagens não textuais;
- gerar resposta automática;
- salvar a mensagem no banco de dados;
- registrar logs no terminal;
- preparar o envio da resposta pelo WhatsApp.

### Tipos de mensagens tratados

```text
text
image
audio
video
document
sticker
location
contacts
interactive
unknown
```

### Observação

O envio real pelo WhatsApp ainda depende da configuração das variáveis:

```env
WHATSAPP_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
WHATSAPP_API_VERSION=
```

Enquanto essas variáveis não estiverem configuradas, a função de envio retorna uma resposta informando que o token ou o Phone Number ID não foram configurados.

Isso permite testar toda a estrutura do webhook sem conectar ainda a conta real da Meta.

---

## Principais rotas da API

### Sistema

```text
GET /
GET /health
GET /info
```

### Autenticação

```text
POST /login
```

### Mensagens

```text
POST /webhook
GET /mensagens
PUT /mensagens/{mensagem_id}/status
DELETE /mensagens/{mensagem_id}
DELETE /mensagens
```

### FAQs

```text
POST /faqs
GET /faqs
DELETE /faqs/{faq_id}
```

### Usuários

```text
POST /usuarios
GET /usuarios
PUT /usuarios/{usuario_id}
PUT /usuarios/{usuario_id}/senha
DELETE /usuarios/{usuario_id}
GET /me
PUT /me/senha
```

### WhatsApp

```text
GET /whatsapp/webhook
POST /whatsapp/webhook
```

---

## Deploy no Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

O projeto também possui:

```text
Procfile
start.sh
.env.example
DEPLOY_RENDER.md
```

SQLite funciona para teste inicial no Render, mas para produção o recomendado é usar PostgreSQL e configurar `DATABASE_URL`.

---

## Estrutura de pastas

```text
softbot-pro-whatsapp/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── bot.py
│   ├── crud.py
│   ├── auth.py
│   ├── config.py
│   └── whatsapp_service.py
├── frontend/
│   ├── login.html
│   ├── index.html
│   ├── mensagens.html
│   ├── faq.html
│   ├── usuarios.html
│   ├── perfil.html
│   ├── config.js
│   ├── style.css
│   └── script.js
├── tests/
│   ├── payload_whatsapp_texto.json
│   └── payload_whatsapp_imagem.json
├── docs/
├── .env.example
├── .gitignore
├── DEPLOY_RENDER.md
├── Procfile
├── requirements.txt
├── start.sh
└── README.md
```

---

## Próximas melhorias

- Fazer deploy da API
- Configurar PostgreSQL em produção
- Conectar com WhatsApp Business Platform
- Configurar token real do WhatsApp
- Configurar webhook na Meta
- Enviar mensagens reais pelo WhatsApp
- Criar relatórios de atendimento
- Melhorar tratamento de arquivos enviados pelo cliente
