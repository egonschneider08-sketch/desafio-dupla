# Contrato HTTP — Sorvetes

[README](../README.md) · [Arquitetura](ARCHITECTURE.md) · [Guia de desenvolvimento](SETUP_FULLSTACK.md)

Base local do Flask: `http://127.0.0.1:5000`. O frontend usa o proxy `/api` em `http://127.0.0.1:5173`. Este documento descreve a implementação da branch `feat/fullstack-catalog-mvp`, ainda em revisão.

## Convenções

- `Content-Type: application/json` nas operações com corpo.
- Respostas de erro esperadas usam `{"error":"mensagem"}`.
- IDs são UUID v4 representados como string.
- Exclusão bem-sucedida devolve **204** sem corpo.
- Nomes e sabores: texto não vazio, máximo 100 caracteres.
- Preço: inteiro de 0 a 2.147.483.647; booleanos e decimais são inválidos.
- A interface considera inteiros como reais inteiros temporariamente, sem conversão de dados.
- API **sem autenticação**, destinada ao ambiente local.

## Rotas

| Método | Rota | Sucesso | Outros códigos |
| --- | --- | --- | --- |
| GET | /health | 200 | Falhas inesperadas não padronizadas |
| GET | /fabricantes | 200 | - |
| POST | /fabricantes | 201 | 400, 409 |
| GET | /fabricantes/{id} | 200 | 400, 404 |
| PATCH | /fabricantes/{id} | 200 | 400, 404, 409 |
| DELETE | /fabricantes/{id} | 204 | 400, 404, 409 |
| GET | /sorvetes | 200 | 400 para UUID de filtro inválido |
| POST | /sorvetes | 201 | 400, 404, 409 |
| GET | /sorvetes/{id} | 200 | 400, 404 |
| PATCH | /sorvetes/{id} | 200 | 400, 404, 409 |
| DELETE | /sorvetes/{id} | 204 | 400, 404 |

## Fabricantes

### POST /fabricantes

```json
{"nome":"Gelados da Serra"}
```

Retorna 201 com `{"id":"UUID","nome":"Gelados da Serra"}`. Duplicidade de nome: 409.

### GET /fabricantes

Retorna lista ordenada pelo nome:

```json
[{"id":"550e8400-e29b-41d4-a716-446655440000","nome":"Gelados da Serra"}]
```

### GET /fabricantes/{id}

Retorna fabricante e seus produtos associados:

```json
{"id":"550e8400-e29b-41d4-a716-446655440000","nome":"Gelados da Serra","sorvetes":[]}
```

### PATCH /fabricantes/{id}

Aceita exclusivamente `{"nome":"Novo nome"}`, devolve fabricante atualizado. Validação de nome: 400; nome em uso: 409.

### DELETE /fabricantes/{id}

204 sem corpo quando sem produtos. Retorna 409 ao tentar excluir fabricante com sorvetes vinculados, para preservar a integridade.

## Sorvetes

### POST /sorvetes

```json
{"nome":"Picolé","sabor":"Morango","preco":5,"fabricante_id":"550e8400-e29b-41d4-a716-446655440000"}
```

Resposta 201:

```json
{
  "id":"2ea2c95d-52ae-4fb0-a413-74e9498c1d0c",
  "nome":"Picolé",
  "sabor":"Morango",
  "preco":5,
  "fabricante_id":"550e8400-e29b-41d4-a716-446655440000",
  "fabricante":"Gelados da Serra"
}
```

Fabricante inexistente: 404. Nome, sabor, preço ou UUID inválidos: 400.

### GET /sorvetes

Retorna lista no mesmo formato, ordenada por nome. Filtros opcionais:

| Query param | Ação |
| --- | --- |
| `q` | Busca substring sem distinção de maiúsculas/minúsculas em `nome` |
| `sabor` | Filtra por substring em `sabor` |
| `fabricante_id` | Filtra por UUID exato de fabricante |

Exemplo: `GET /sorvetes?q=picolé&fabricante_id=UUID`.

### GET /sorvetes/{id}

Retorna o objeto individual (200) ou 404.

### PATCH /sorvetes/{id}

Aceita um ou mais: `nome`, `sabor`, `preco`, `fabricante_id`. Atualiza apenas os campos informados. Campos desconhecidos, corpo vazio ou valores inválidos: 400. Fabricante de destino inexistente: 404.

### DELETE /sorvetes/{id}

204 sem corpo; 404 se não encontrado.

## Garantias e limites

As rotas anteriores GET/POST de coleções permanecem compatíveis com os contratos iniciais. O servidor de desenvolvimento não oferece controle de acesso ou proteções operacionais para exposição pública. Os testes em `tests/test_api.py`, `tests/test_models.py` e `tests/test_crud.py` validam contratos de regressão e CRUD.
