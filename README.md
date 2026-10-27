![Sorvetes — catálogo Full Stack](docs/assets/sorvetes-banner.svg)

# 🍦 Sorvetes — Plataforma de Catálogo

> Sistema Full Stack para gerenciar fabricantes e sorvetes, com interface responsiva, API REST e persistência relacional.

[![Full Stack CI](https://github.com/egonschneider08-sketch/sorvete-flask-api/actions/workflows/ci.yml/badge.svg)](https://github.com/egonschneider08-sketch/sorvete-flask-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-149ECA?logo=react&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-REST%20API-1b2737?logo=flask&logoColor=white)
![MVP](https://img.shields.io/badge/Status-MVP%20em%20revis%C3%A3o-90cdb9)

## O que é

O Sorvetes é uma aplicação web para organizar um catálogo de fabricantes e seus sorvetes. Foi desenvolvido como projeto de engenharia de software e portfólio, com preocupação em testes, qualidade, documentação e evolução.

**Funcionalidades disponíveis nesta branch:**
- Dashboard com indicadores reais de fabricantes, produtos e sabores.
- CRUD de fabricantes e sorvetes.
- Busca por nome e filtro de sorvetes por fabricante.
- Formulários com validação, erros, carregamento e confirmação de exclusão.
- Regras de integridade: não excluir fabricante com produtos associados.
- Testes automáticos de backend/frontend e build verificado no GitHub Actions.

**Escopo:** MVP para desenvolvimento local. Não há autenticação; **não exponha o painel na internet sem controles de acesso**.

## Tecnologias

| Camada | Stack |
| --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS, React Router |
| Dados no frontend | TanStack Query, React Hook Form, Zod |
| Backend | Python, Flask, Blueprints, SQLAlchemy, Flask-Migrate |
| Banco | SQLite local; opção PostgreSQL configurável |
| Qualidade | pytest, Vitest, Testing Library, GitHub Actions |

## Executar localmente

### 1. Baixar o código

```powershell
git clone https://github.com/egonschneider08-sketch/sorvete-flask-api.git
cd sorvete-flask-api
```

> Até a aprovação do PR #10, execute `git switch feat/fullstack-catalog-mvp` após o clone; o conteúdo da `main` ainda não possui o frontend.

### 2. Iniciar o backend (terminal A)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

API: **http://127.0.0.1:5000/health**.

### 3. Iniciar o frontend (terminal B)

```powershell
cd frontend
npm install
npm run dev
```

Aplicação: **http://127.0.0.1:5173**.

O Vite encaminha `/api` para Flask na porta 5000, sem precisar abrir CORS para qualquer origem.

## Como testar

```powershell
# Na raiz
python -m pip install pytest
python -m pytest -q

# Em frontend/
npm test
npm run build
```

A CI executa testes em Python 3.10 e 3.12, além dos testes e build Node 22.

## Rotas HTTP

| Método | Endpoint | Descrição |
| --- | --- | --- |
| GET | /health | Verificação de conexão |
| GET, POST | /fabricantes | Listagem e cadastro |
| GET, PATCH, DELETE | /fabricantes/{id} | Consulta, edição e exclusão |
| GET, POST | /sorvetes | Listagem, filtros e cadastro |
| GET, PATCH, DELETE | /sorvetes/{id} | Consulta, edição e exclusão |

Detalhes, campos e exemplos: [Referência da API](docs/API.md).

## Estrutura

```text
app.py                      # Flask application factory
routes/                     # Blueprints e utilitários HTTP
models/                     # Modelos ORM
db.py                       # Extensão SQLAlchemy
frontend/                   # React, TypeScript, componentes e páginas
tests/                      # Testes do backend
docs/                       # API, arquitetura, guia de execução, roadmap
.github/workflows/          # CI para backend e frontend
```

## Documentação

- [Guia completo de instalação](docs/SETUP_FULLSTACK.md)
- [Arquitetura e decisões](docs/ARCHITECTURE.md)
- [Contrato da API](docs/API.md)
- [Roadmap](docs/ROADMAP.md)
- [Como contribuir](CONTRIBUTING.md)
- [Central do projeto no Notion](https://app.notion.com/p/406f69f1ed0681e79d21f2ef6f160db5)

## Limitações atuais

A API foi desenvolvida para uso local sem autenticação. O campo `preco` é inteiro; esta interface exibe seu valor em reais inteiros para evitar modificar dados legados, mas a convenção precisa ser confirmada para uso com preços reais. O código mantém `db.create_all()` até uma estratégia de migrações ser implantada. A hospedagem em produção e o lockfile de dependências frontend estão no roadmap.

## Fluxo de contribuição

Abra uma issue, crie branch curta, adicione testes, atualize documentação e faça Pull Request. Para preservar a sequência de revisões, integrar **PR #3 → PR #5 → PR #10** antes de publicar o MVP.
