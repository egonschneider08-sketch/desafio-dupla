# Arquitetura Full Stack — Sorvetes

[README](../README.md) · [API](API.md) · [Setup](SETUP_FULLSTACK.md)

## Visão

```text
Browser → React + TypeScript / Vite (localhost:5173)
                       |
                  HTTP /api/*
                       |
                 proxy Vite dev
                       |
                Flask (localhost:5000)
                       |
             Blueprints e validação
                       |
                  SQLAlchemy
                       |
                SQLite por padrão
```

## Frontend

```text
frontend/src/
├── App.tsx                  Navegação e shell da aplicação
├── main.tsx                 Providers React Query e Router
├── components/UI.tsx        Dialog, confirmação, feedback e estados reutilizáveis
├── lib/api.ts               Cliente HTTP, tipagem e serialização monetária
├── pages/
│   ├── Dashboard.tsx        Indicadores reais, atalhos e produtos recentes
│   ├── Fabricantes.tsx      CRUD e pesquisa de fabricantes
│   └── Sorvetes.tsx         CRUD, filtros e pesquisa de produtos
└── styles.css               Tokens e layout responsivo
```

O TanStack Query compartilha os dados remotos entre páginas e invalida cache após mutações. React Hook Form e Zod validam a entrada do formulário; o Flask realiza validação independente no servidor. O cliente usa URL relativa `/api`.

## Backend

```text
app.py                    Application Factory, configuração e registro de blueprints
routes/
├── health.py             GET /health
├── fabricantes.py        Rotas de fabricantes
├── sorvetes.py           Rotas de sorvetes
└── common.py             UUID, validações e serializadores
db.py                     SQLAlchemy extension
models/book.py            Fabricante e Sorvete (nome legado de arquivo)
```

O código preserva a application factory e os endpoints originais. Ainda **não** existe camada separada de serviços: as regras são curtas e ficam nos blueprints para evitar abstração prematura. Introduzir serviços conforme a lógica de negócio crescer.

## Modelo de dados

```text
fabricantes (1) ─────────────── (N) sorvetes

fabricantes:
  id             String(36), PK, UUID v4
  nome           String(100), UNIQUE, NOT NULL

sorvetes:
  id             String(36), PK, UUID v4
  nome           String(100), NOT NULL
  sabor          String(100), NOT NULL
  preco          Integer, NOT NULL
  fabricante_id  String(36), FK NOT NULL
```

Regras na API: `preco` inteiro não negativo; excluir fabricante com produtos retorna 409; nomes e sabores até 100 caracteres.

**Nota monetária:** os registros anteriores não definiam unidade; a interface exibe o inteiro como reais inteiros sem converter dados. Revisar a semântica antes de implantar com preços financeiros reais.

## Banco e ambientes

SQLite: padrão `instance/sorvetes.db`, criado na inicialização. `DATABASE_URL` pode apontar para SQLite ou PostgreSQL; URLs incompatíveis geram erro em vez de fallback silencioso. PostgreSQL exige driver `psycopg` e banco de destino. Testes usam SQLite temporário.

O uso de `db.create_all()` continua **apenas para o MVP local**. Implementar migrations versionadas antes de aplicar mudanças de schema em base persistida de produção.

## Segurança

O sistema ainda não tem autenticação/autorização. **Não implantar publicamente como painel administrativo.** O desenvolvimento usa proxy para evitar CORS irrestrito; proteger `.env`, excluir bancos locais do Git e desabilitar debug em produção.

## Qualidade e trade-offs

- Contratos HTTP existentes preservados.
- Blueprints dividem rotas por recurso.
- Testes pytest para CRUD, validadores e integridade; Vitest e React Testing Library para frontend.
- GitHub Actions valida backend Python 3.10/3.12, frontend Node 22.
- Não existem ainda migrações de schema, login, observabilidade completa nem workflow de implantação.

Decisões: [ADR-004 no Notion](https://app.notion.com/p/406f69f1ed068183965afb7861252fc1).
