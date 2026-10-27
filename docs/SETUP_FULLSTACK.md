# Guia de execução — Sorvetes Full Stack

## Visão geral

O MVP possui **Flask + SQLAlchemy** no backend e **React + TypeScript + Vite** no frontend. Em desenvolvimento são dois processos, com proxy Vite: chamadas do navegador para `/api/...` são encaminhadas a `http://127.0.0.1:5000/...`. Assim, o browser usa **mesma origem** (porta 5173) e não é necessário abrir CORS permissivo.

## Pré-requisitos

- Python 3.10 ou 3.12 (ambos testados na CI).
- Node.js 22 e npm.
- Git.

### 1. Backend — terminal A

```powershell
git clone https://github.com/egonschneider08-sketch/sorvete-flask-api.git
cd sorvete-flask-api
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

**Alternativa:** dependências de produção e testes mínimas no pipeline de CI, pois o `requirements.txt` legado contém bibliotecas extras; sua revisão está no roadmap.

**Banco:** SQLite `instance/sorvetes.db` é criado automaticamente. PostgreSQL requer banco existente e driver psycopg. Nunca copie senhas de exemplo para produção.

### 2. Frontend — terminal B

```powershell
cd sorvete-flask-api/frontend
npm install
npm run dev
```

Abra **http://127.0.0.1:5173**. Recarregue a página se o Flask tiver sido iniciado depois do Vite.

### 3. Testes e build

```powershell
# Raiz do projeto
python -m pytest -q

# Pasta frontend
npm test
npm run build
```

A CI executa testes backend em Python 3.10/3.12, testes frontend e build com Node 22. Se uma etapa falhar, não integre a mudança.

## Contrato HTTP

| Recurso | Operações |
| --- | --- |
| Saúde | GET /health |
| Fabricantes | GET /fabricantes · POST /fabricantes · GET/PATCH/DELETE /fabricantes/{id} |
| Sorvetes | GET /sorvetes · POST /sorvetes · GET/PATCH/DELETE /sorvetes/{id} |

Filtros opcionais no GET /sorvetes: `q` (nome), `sabor` e `fabricante_id` (UUID).

Um fabricante com sorvetes relacionados retorna **409** ao ser excluído; remova produtos associados antes. Exclusões bem-sucedidas retornam **204** sem corpo.

## Preços — decisão de compatibilidade do MVP

A API preexistente armazenava `preco` como inteiro sem especificação formal. Para exibir seus registros existentes **sem converter ou migrar dados**, o frontend apresenta o inteiro como **reais inteiros** (`5` → `R$ 5,00`). Não há centavos armazenados; futuras alterações devem introduzir unidade explícita, migração e teste de compatibilidade. Confirme a convenção com os responsáveis pelos dados antes de inserir preços monetários reais.

## Segurança

- A API atual não tem autenticação. O painel é para **desenvolvimento local**; não publique endpoints administrativos sem controle de acesso.
- CORS não é aberto: Vite usa proxy local e futuras implantações devem configurar roteamento de mesma origem.
- O servidor `flask --debug` não é um servidor de produção.
- `.env`, bancos locais e segredos não devem ser versionados.

## Troubleshooting

- **Erro de conexão na tela:** cheque se Flask está acessível em `http://127.0.0.1:5000/health`.
- **Porta 5173 ocupada:** encerre a aplicação que está usando a porta ou ajuste Vite e a URL.
- **Erro de configuração DATABASE_URL:** remova a variável ou forneça URL SQLite/PostgreSQL válida.
- **Não consegue excluir fabricante:** apague primeiro os sorvetes vinculados; isso evita perda de dados.
