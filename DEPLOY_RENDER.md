# Deploy no Render

## Arquivos esperados na raiz

- `README.md`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `Procfile`
- `start.sh`
- `app/`
- `frontend/`

## Build Command

```bash
pip install -r requirements.txt
```

## Start Command

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Variaveis de ambiente

Configure estas variaveis no Render:

```env
SECRET_KEY=uma_chave_grande_e_segura
ADMIN_USERNAME=admin
ADMIN_PASSWORD=uma_senha_forte
ACCESS_TOKEN_EXPIRE_MINUTES=120
DATABASE_URL=sqlite:///./softbot.db
CORS_ORIGINS=https://sua-url-do-front.com,http://127.0.0.1:5500,http://localhost:5500
WHATSAPP_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
```

Por enquanto, as variaveis do WhatsApp podem ficar vazias.

## SQLite no Render

SQLite funciona para teste, mas nao e ideal para producao no Render, porque o armazenamento pode nao ser permanente dependendo do plano e configuracao.

Ordem recomendada:

1. Testar deploy com SQLite.
2. Confirmar que a API sobe.
3. Criar PostgreSQL.
4. Trocar `DATABASE_URL` para a URL do PostgreSQL.

Exemplo:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_do_banco
```

## URL da API no front-end

Enquanto estiver local, `frontend/config.js` deve usar:

```javascript
const API_URL = "http://127.0.0.1:8000";
```

Depois do deploy, troque para a URL publica da API:

```javascript
const API_URL = "https://sua-api-no-render.onrender.com";
```
