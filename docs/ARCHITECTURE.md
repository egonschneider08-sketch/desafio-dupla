# Arquitetura e modelo de dados

[Voltar ao README](../README.md) · [Contrato HTTP](API.md) · [Roadmap](ROADMAP.md)

## Visão geral

A aplicação usa Flask e SQLAlchemy com persistência relacional. Hoje, as rotas, regras de entrada e operações ORM estão em `app.py`; os modelos estão em `models/book.py`.

```text
Cliente HTTP
    │
    ▼
Flask / app.py ──► validação de JSON
    │                  │
    ▼                  ▼
db.py / Flask-SQLAlchemy
    │
    ▼
Fabricante e Sorvete (models/book.py)
    │
    ▼
SQLite (instance/sorvetes.db)
```

## Ciclo de inicialização

A função `create_app(test_config=None)` carrega variáveis com `load_dotenv()`, prepara `instance/`, seleciona SQLite por padrão, inicializa SQLAlchemy e Flask-Migrate e chama `db.create_all()`.

A substituição via `DATABASE_URL` é permitida **apenas** para URLs iniciadas com `sqlite`. Portanto, `.env.example` descreve PostgreSQL como intenção ou legado de configuração, não como suporte confirmado.

`db.create_all()` cria tabelas ausentes, mas não substitui migrações versionadas.

## Modelo relacional

```text
fabricantes
  id         VARCHAR(36) PRIMARY KEY   (UUID v4 como texto)
  nome       VARCHAR(100) NOT NULL UNIQUE
      │ 1
      │
      │ N
sorvetes
  id         VARCHAR(36) PRIMARY KEY   (UUID v4 como texto)
  nome       VARCHAR(100) NOT NULL
  sabor      VARCHAR(100) NOT NULL
  preco      INTEGER NOT NULL
  fabricante_id VARCHAR(36) NOT NULL REFERENCES fabricantes(id)
```

O endpoint de criação exige `preco >= 0`; não foi identificada uma restrição SQL explícita de não negatividade. A unidade monetária ainda não está definida.

## Regras da aplicação

- Fabricantes devem ter nome não vazio; o nome é único no banco.
- Sorvetes exigem nome, sabor, preço inteiro não negativo e fabricante existente.
- As listagens ordenam pelo nome.
- Identificadores são UUIDs criados em Python, armazenados como `String(36)`.
- O método `Fabricante.dict()` tenta chamar `sorvete.dict()`, mas `Sorvete` expõe `as_dict()`: inconsistência conhecida a corrigir.

## Limitações e riscos

1. Tratamento de exceções não é uniforme entre `POST /fabricantes` e `POST /sorvetes`.
2. Algumas mensagens acentuadas aparecem corrompidas no arquivo `app.py`.
3. Aplicação concentra validação, rotas e serialização em um módulo.
4. Não há contrato OpenAPI versionado identificado na leitura inicial.
5. Debug local não deve ser utilizado em produção.

## Proposta para crescimento

Adotar blueprints para endpoints, serviços para regras de negócio, schemas de entrada/saída e migrações versionadas, **somente conforme a necessidade**. Manter simplicidade do MVP, evitar abstrações prematuras e registrar decisões arquiteturais no Notion.
