# Como contribuir

Obrigado por contribuir com a Sorvetes API. Nosso objetivo é manter mudanças pequenas, revisáveis e documentadas.

## Preparação

1. Leia [README](README.md), [API](docs/API.md) e [Arquitetura](docs/ARCHITECTURE.md).
2. Crie um ambiente virtual e instale as dependências do projeto.
3. Instale `pytest` e execute `python -m pytest` antes de propor alterações.

## Fluxo de trabalho

1. Abra uma issue para descrever o problema ou melhoria.
2. Crie uma branch a partir de `main`: `feat/`, `fix/`, `docs/` ou `test/`.
3. Faça commits descritivos: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
4. Atualize exemplos, contratos e documentação ao modificar endpoints.
5. Abra um pull request preenchendo o modelo; não faça merge sem revisar a CI.

## Critérios de revisão

- Mudança preserva funcionalidades existentes ou descreve claramente quebras de compatibilidade.
- Novos comportamentos possuem testes.
- Respostas e códigos HTTP permanecem coerentes.
- Sem credenciais, segredos ou bancos gerados no commit.
- Pull request explica objetivo, riscos e como validar.

## Segurança

Não exponha dados sensíveis em issues ou pull requests públicos. Vulnerabilidades devem ser comunicadas de forma privada ao responsável pelo repositório, evitando detalhes exploráveis em público.

## Escopo de produção

O servidor `flask run --debug` é para uso local. Definição de hospedagem, autenticação, backups e observabilidade será tratada antes de qualquer publicação como serviço real.
