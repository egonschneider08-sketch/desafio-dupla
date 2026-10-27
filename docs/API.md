# Referência da API HTTP

[Voltar ao README](../README.md) · [Arquitetura](ARCHITECTURE.md)

Base local: `http://127.0.0.1:5000`. Endpoints conforme leitura do `app.py`, sem suposição de operações ainda não implementadas.

| Método | Caminho | Efeito | Resposta principal |
| --- | --- | --- | --- |
| GET | `/health` | Verifica banco com `SELECT 1` | 200 |
| GET | `/fabricantes` | Lista ordenada por nome | 200 |
| POST | `/fabricantes` | Cadastra fabricante | 201 |
| GET | `/sorvetes` | Lista ordenada por nome | 200 |
| POST | `/sorvetes` | Cadastra sorvete | 201 |

## GET /health

```json
{"status":"ok","database":"connected"}
```

## GET /fabricantes

Retorna `[]` quando vazio ou uma lista de objetos:

```json
[{"id":"550e8400-e29b-41d4-a716-446655440000","nome":"Gelados da Serra"}]
```

## POST /fabricantes

`Content-Type: application/json`

```json
{"nome":"Gelados da Serra"}
```

**201:** retorna `id` e `nome`. **400:** nome inválido ou JSON incorreto. **409:** erro de integridade tratado pela aplicação como fabricante duplicado.

## GET /sorvetes

Resposta de exemplo:

```json
[{
  "id":"2ea2c95d-52ae-4fb0-a413-74e9498c1d0c",
  "nome":"Picolé",
  "sabor":"Morango",
  "preco":5,
  "fabricante_id":"550e8400-e29b-41d4-a716-446655440000",
  "fabricante":"Gelados da Serra"
}]
```

## POST /sorvetes

`Content-Type: application/json`

```json
{
  "nome":"Picolé",
  "sabor":"Morango",
  "preco":5,
  "fabricante_id":"550e8400-e29b-41d4-a716-446655440000"
}
```

**201:** retorna o mesmo formato de objeto de `GET /sorvetes` (não uma lista).

**400:** corpo não é objeto JSON; nome/sabor vazios; preço não é inteiro não negativo (booleanos rejeitados); `fabricante_id` não é UUID string válido.

**404:** não existe fabricante com o UUID informado.

## Observações contratuais

- O campo `preco` ainda não possui unidade monetária documentada no domínio. Não assuma centavos ou reais.
- Não há autenticação nos endpoints mostrados.
- Não há endpoints de atualização e exclusão nessa versão.
- Mensagens exatas de erro podem apresentar problemas de encoding no código atual.
- Respostas de erro inesperado ainda dependem do comportamento padrão do Flask.
