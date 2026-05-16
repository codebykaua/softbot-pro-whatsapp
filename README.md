# SoftBot Pro WhatsApp

Sistema de automação de atendimento inspirado em WhatsApp Business, desenvolvido com Python, FastAPI, SQLite, HTML, CSS e JavaScript.

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
- SQLAlchemy
- Pydantic
- PyJWT
- python-dotenv

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
- Rota `/webhook` para processar mensagens
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

### Status de atendimento

Os status disponíveis são:

- respondido
- pendente
- encaminhado
- finalizado

### Autenticação

- Login com usuário e senha
- Token JWT
- Rotas protegidas
- Controle de acesso por perfil

### Usuários

- Criação de usuários
- Listagem de usuários
- Exclusão de usuários
- Alteração de senha
- Perfis: admin, atendente e suporte

---

## Permissões por perfil

### Admin

O usuário admin pode:

- acessar todas as páginas;
- criar usuários;
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

## Estrutura de pastas

```text
softbot-pro-whatsapp/
│
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
│
├── frontend/
│   ├── login.html
│   ├── index.html
│   ├── mensagens.html
│   ├── faq.html
│   ├── usuarios.html
│   ├── style.css
│   └── script.js
│
├── docs/
│   └── prints-do-projeto/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md