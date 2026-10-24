# API de sorvetes

API Flask conectada a um banco PostgreSQL. O banco roda em um container Docker
e mantém os dados em um volume, mesmo depois que o container for parado.

## Requisitos

- Docker Desktop com Docker Compose
- Python 3.10 ou superior para executar a API fora do Docker

## Iniciar o banco

Na raiz do projeto, copie o arquivo de exemplo e inicie o PostgreSQL:

```powershell
Copy-Item .env.example .env
docker compose pull db
docker compose up -d db
```

O Compose também baixa a imagem automaticamente se ela ainda não estiver
instalada. Para conferir o estado do banco:

```powershell
docker compose ps
docker compose logs db
```

As configurações locais ficam em `.env`. Os valores de exemplo são apenas para
desenvolvimento; altere a senha antes de usar em qualquer ambiente compartilhado.
Se mudar o usuário, a senha, o nome ou a porta do banco, atualize também o
`DATABASE_URL` para manter a conexão da aplicação alinhada.

## Executar a API

Instale as dependências já declaradas no projeto e inicie o servidor:

```powershell
python -m pip install -r requirements.txt
flask --app app run --debug
```

A aplicação fica disponível em `http://127.0.0.1:5000`. Ela cria as tabelas
necessárias ao iniciar. Se `DATABASE_URL` não estiver definido, usa um SQLite
local (`instance/sorvetes.db`) para facilitar a execução sem Docker.

## Endpoints

### Verificar a conexão

```http
GET /health
```

### Fabricantes

```http
GET /fabricantes
POST /fabricantes
Content-Type: application/json

{"nome": "Gelados da Serra"}
```

### Sorvetes

```http
GET /sorvetes
POST /sorvetes
Content-Type: application/json

{
  "nome": "Picolé",
  "sabor": "Morango",
  "preco": 5,
  "fabricante_id": "<UUID retornado por POST /fabricantes>"
}
```

`preco` é um número inteiro não negativo. Cada sorvete precisa estar associado
a um fabricante existente. As respostas incluem o UUID do registro.

Exemplo para cadastrar fabricante no PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/fabricantes `
  -ContentType "application/json" -Body '{"nome":"Gelados da Serra"}'
```

## Comandos úteis

```powershell
docker compose stop db       # parar sem apagar os dados
docker compose start db      # iniciar novamente
docker compose down          # remover o container, preservando o volume
docker compose down -v       # apagar também o volume e todos os dados
```

Por padrão, o PostgreSQL é publicado na porta `5432`. Ajuste `POSTGRES_PORT`
no `.env` se essa porta já estiver ocupada.
