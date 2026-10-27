# Autenticação e perfis — Sorvetes

[README](../README.md) · [API](API.md) · [Setup](SETUP_FULLSTACK.md)

## Objetivo

Usuários podem criar uma conta com nome, e-mail e senha, autenticar-se e consultar o catálogo. A conta de cadastro público recebe exclusivamente o perfil `viewer`. Apenas administradores `admin` podem criar, editar ou excluir fabricantes e sorvetes.

| Ação | Visitante | Cliente (viewer) | Administrador |
| --- | --- | --- | --- |
| GET /health | ✅ | ✅ | ✅ |
| Cadastro, login e consulta de sessão | ✅ | ✅ | ✅ |
| GET /fabricantes e GET /sorvetes | ❌ 401 | ✅ | ✅ |
| POST, PATCH, DELETE /fabricantes e /sorvetes | ❌ | ❌ 403 | ✅ |
| Criar conta com perfil admin pela web | ❌ | ❌ | ❌ |

A proteção é validada no **servidor Flask**. Ocultar botões no frontend não substitui autorização.

## Criar o primeiro administrador

O cadastro pela web **nunca** permite criar administradores. Na raiz do projeto, depois de instalar as dependências e definir as variáveis do ambiente:

```powershell
python -m flask --app app create-admin
```

O comando solicita **e-mail**, **nome** e **senha** de forma interativa. A senha não deve ser passada na linha de comando nem incluída no repositório. Se o e-mail já estiver cadastrado, o comando falha: use outro e-mail ou defina uma política formal de promoção de contas em uma evolução futura.

## Fluxo do cliente

1. Abrir http://127.0.0.1:5173/cadastro.
2. Preencher nome, e-mail e senha de 12 a 128 caracteres.
3. A conta viewer é criada e o usuário entra automaticamente.
4. Visitar catálogo e filtrar produtos.
5. Encerrar a sessão por **Sair**.
6. Para entrar novamente, usar http://127.0.0.1:5173/entrar.

## Endpoints

| Método | Rota | Resposta |
| --- | --- | --- |
| GET | /auth/session | 200, `{user, csrf_token}` (user pode ser null) |
| POST | /auth/register | 201, `{user, csrf_token}`; 400 inválido / 409 e-mail duplicado |
| POST | /auth/login | 200, `{user, csrf_token}`; 401 credenciais incorretas |
| POST | /auth/logout | 200, `{user:null, csrf_token}` |

**Antes de qualquer POST, PATCH ou DELETE**, consulte `GET /auth/session` e inclua `X-CSRF-Token` com o token retornado. Após login/cadastro/logout o token é rotacionado; use o novo valor recebido. O navegador envia o cookie de sessão automaticamente em mesma origem. Não envie tokens CSRF ou senhas para logs.

Exemplo de registro:

```json
{"name":"Cliente Exemplo","email":"cliente@example.com","password":"SenhaLongaDeExemplo123"}
```

O exemplo representa o formato dos dados; **não utilize a senha apresentada em contas reais**.

## Controles implementados

- Senhas guardadas com hash **scrypt** (Werkzeug), nunca em texto puro.
- E-mails normalizados em minúsculas e únicos na tabela `users`.
- Sessões assinadas pelo Flask, com cookies `HttpOnly`, `SameSite=Lax` e `Secure` quando `APP_ENV=production`.
- Chave de sessão `SECRET_KEY` exigida quando `APP_ENV=production`; no ambiente local sem chave explícita, a chave é efêmera e a sessão perde validade após reinício.
- Token CSRF por sessão exigido nos métodos que modificam dados.
- Login renova a sessão; logout a invalida.
- Verificação de perfil `admin` em todas as rotas de escrita, sem confiança em campos enviados pelo cliente.
- O `GET /health` permanece público; a listagem dos produtos requer conta autenticada.

## Banco de dados existente

O novo modelo SQLAlchemy `User` cria tabela `users` em inicialização local via `db.create_all()`, sem alterar o esquema das tabelas `fabricantes` e `sorvetes`. **Em produção**, use migrations versionadas e realize backup antes de qualquer mudança de esquema.

## Pontos obrigatórios antes de publicar na internet

A autenticação é um primeiro MVP e **não comprova prontidão de produção**. Planejar e testar:

- Rate limiting para login/cadastro contra força bruta e criação massiva de contas.
- Verificação de e-mail e recuperação de senha segura.
- Regras de proteção de contas, auditoria, desativação e eventual MFA para admins.
- HTTPS/TLS, configuração proxy, `SECRET_KEY` persistente e gestão de segredos.
- Migrations, monitoramento, política de privacidade e retenção de dados.
- Teste ponta a ponta no navegador e revisão de segurança.

A configuração atual prioriza uso local e testes automatizados.