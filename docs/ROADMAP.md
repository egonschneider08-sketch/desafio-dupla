# Roadmap e qualidade

**Estado:** proposta de trabalho; tarefas abaixo não representam funcionalidades prontas nem datas compromissadas.

## P0 — Confiabilidade do MVP

- [ ] Corrigir divergência entre `Fabricante.dict()` e `Sorvete.as_dict()`.
- [ ] Revisar codificação UTF-8 das mensagens de erro.
- [ ] Decidir política de `DATABASE_URL` e alinhar `.env.example`.
- [ ] Formalizar unidade de `preco` e reforçar integridade no banco.
- [ ] Expandir cobertura de exceções de persistência e rollback.
- [ ] Criar testes para validação, UUID, duplicidade, relação e dados inválidos.

## P1 — Padrões e automação

- [ ] Avaliar `requirements.txt` e remover dependências não usadas após verificação.
- [ ] Documentar ambiente de execução para produção sem debug.
- [ ] Padronizar estrutura de erro e serialização.
- [ ] Adicionar linter e verificação de tipos conforme maturidade do projeto.
- [ ] Adotar migrations versionadas e revisar `db.create_all()`.

## P2 — Produto e escalabilidade

- [ ] Definir requisitos para operações de atualizar e remover registros.
- [ ] Adicionar paginação e filtros mediante necessidade real.
- [ ] Gerar OpenAPI a partir de contrato revisado.
- [ ] Planejar autenticação/autorização se houver exposição a usuários.
- [ ] Definir estratégia de deploy, logs, backup e observabilidade.

## Definição de pronto

Uma entrega está pronta quando: requisitos e critérios de aceite estão claros; código revisado; testes relevantes executados; documentação atualizada; riscos e efeitos sobre dados avaliados; e CI aprovada.

## Registro de decisões

Manter decisões arquiteturais no Notion, com contexto, alternativas, escolha, consequências, data e status. Vincular issues/PRs a cada decisão implementada.
