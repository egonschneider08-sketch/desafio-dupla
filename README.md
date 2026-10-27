# 🍦 Sorvetes API

> API REST de catálogo de sorvetes e fabricantes construída com Python, Flask e SQLAlchemy.

[![CI](https://github.com/egonschneider08-sketch/sorvete-flask-api/actions/workflows/ci.yml/badge.svg)](https://github.com/egonschneider08-sketch/sorvete-flask-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-111827?logo=flask&logoColor=white)
![Status](https://img.shields.io/badge/Status-MVP_em_evolu%C3%A7%C3%A3o-2563eb)

## Sobre o projeto

O **Sorvetes API** é um backend educacional para gerenciar fabricantes e produtos de um catálogo de sorvetes. Atualmente oferece operações de criação e listagem, com identificação por UUID, validação básica de dados, relacionamento entre fabricantes e sorvetes e persistência SQLite local.

**Implementado:** `GET /health`, `GET/POST /fabricantes` e `GET/POST /sorvetes`.

**Não implementado nesta versão:** atualização/exclusão, autenticação, paginação e deploy de produção. Veja o [roadmap](docs/ROADMAP.md).

## Documentação

| Documento | Finalidade |
| --- | --- |
| [Guia da API](docs/API.md) | Endpoints, exemplos e erros |
| [Arquitetura e dados](docs/ARCHITECTURE.md) | Componentes, modelos e decisões |
| [Roadmap](docs/ROADMAP.md) | Plano de evolução e prioridades |
| [Como contribuir](CONTRIBUTING.md) | Fluxo Git e critérios de revisão |
| [Notion](https://app.notion.com/p/406f69f1ed0681e79d21f2ef6f160db5) | Central de planejamento e documentação do projeto |

## Tecnologias

- Python 3.10+ (requisito descrito pelo projeto).
- Flask, Flask-SQLAlchemy, SQLAlchemy e Flask-Migrate.
- SQLite por padrão: banco criado em `instance/sorvetes.db`.
- `python-dotenv` para carregar configuração local.

> **Atenção:** apesar de `.env.example` conter PostgreSQL, o código atual só aplica `DATABASE_URL` quando ela começa com `sqlite`. A configuração PostgreSQL ainda exige implementação.

## Começar

Requer Python e Git. No PowerShell:

```powershell
git clone https://github.com/egonschneider08-sketch/sorvete-flask-api.git
cd sorvete-flask-api
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

Sem ativar a venv (se bloqueado por política do PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run --debug
```

Abra `http://127.0.0.1:5000/health`. Resposta esperada:

```json
{"status":"ok","database":"connected"}
```

A opção `--debug` é **somente para desenvolvimento local**.

## Exemplos de uso

Criar um fabricante:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/fabricantes `
  -ContentType "application/json" -Body '{"nome":"Gelados da Serra"}'
```

Use o `id` retornado como `fabricante_id` ao criar um sorvete:

```json
{"nome":"Picolé","sabor":"Morango","preco":5,"fabricante_id":"UUID-DO-FABRICANTE"}
```

O campo `preco` aceita **inteiros não negativos**. Sua unidade monetária ainda precisa ser formalizada como regra do domínio.

## Testes e qualidade

```powershell
python -m pip install pytest
python -m pytest
```

O GitHub Actions executa a suíte básica em pushes e pull requests. Testes e integração contínua estão em evolução e **não constituem certificação de prontidão para produção**.

## Organização do repositório

```text
app.py                 # Fábrica Flask e endpoints
db.py                  # Extensão SQLAlchemy
models/book.py         # Modelos Fabricante / Sorvete
docs/                  # Contratos, arquitetura, roadmap
tests/                 # Testes automatizados básicos
.github/               # Automação e modelos de colaboração
CONTRIBUTING.md        # Guia de contribuição
```

## Desenvolvimento

Priorize mudanças pequenas com testes e pull requests. Não comite `.env`, bancos SQLite locais ou credenciais. Veja [CONTRIBUTING.md](CONTRIBUTING.md).

## Estado do projeto

MVP em evolução, com documentação de comportamento observado em `main`. Consulte [ROADMAP](docs/ROADMAP.md) para problemas conhecidos e itens planejados.