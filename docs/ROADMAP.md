# Roadmap — Sorvetes

Esta página separa funcionalidades integradas à `main` de requisitos ainda pendentes. **O MVP local foi integrado e testado, mas não foi implantado publicamente.**

## Integrado na main (CI aprovada)

- [x] [PR #3](https://github.com/egonschneider08-sketch/sorvete-flask-api/pull/3): documentação, testes iniciais e CI integrados.
- [x] [PR #5](https://github.com/egonschneider08-sketch/sorvete-flask-api/pull/5): correção da serialização de fabricantes integrada.
- [x] [PR #10](https://github.com/egonschneider08-sketch/sorvete-flask-api/pull/10): React + TypeScript, CRUD Flask, testes e build aprovados e integrados. Homologação manual em navegador ainda pendente.
- [x] [PR #12](https://github.com/egonschneider08-sketch/sorvete-flask-api/pull/12): cadastro de clientes, login, sessões seguras básicas, CSRF e acesso administrativo por perfil, integrados à `main` com CI aprovada.

## Próximas tarefas — qualidade e operação

- [x] Revisar e integrar PR #3 → #5 → #10.
- [ ] Validar criação/edição/exclusão no navegador em Windows.
- [ ] Gerar e versionar `frontend/package-lock.json` em ambiente com acesso ao registry.
- [ ] Revisar e simplificar o `requirements.txt` legado.
- [ ] Formalizar unidade monetária e migração de eventual base antiga.
- [ ] Adicionar teste ponta a ponta em browser real.
- [ ] Melhorar acessibilidade de diálogos (travar foco, Escape e retorno ao foco original).

## Antes da implantação na internet

- [ ] Reforçar autenticação para acesso público: rate limiting, confirmação de e-mail, recuperação de senha, auditoria e avaliação de MFA para administradores.
- [ ] Políticas de CORS, CSRF/cookies e sessões conforme implantação escolhida.
- [ ] Migrar esquema de `db.create_all()` para migrações versionadas.
- [ ] Servidor WSGI, proxy reverso, TLS e variáveis de ambiente seguras.
- [ ] Logs, health/readiness, backup/restauração e proteção de dados.
- [ ] Testes de segurança e revisão de dependências.

## Funcionalidades opcionais futuras

- Gestão de estoque e pedidos.
- Categorias e relatórios.
- Paginação do catálogo para bases maiores.
- OpenAPI formal e API versionada se houver integração com terceiros.

## Regra de entrega

Mudanças pequenas com código, testes, documentação e evidência da CI. O status "implementado em branch" **não** equivale a homologação de produção.
