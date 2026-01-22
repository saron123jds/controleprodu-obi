# Dashboard PCP (Dash + SQLite)

Sistema de dashboard estilo Power BI para acompanhamento de produção (PCP). O projeto roda localmente no Windows em `http://localhost:8000` usando Python + Dash (Plotly) e persiste configurações em SQLite.

## Requisitos

- Python 3.10+
- Windows (testado para rodar localmente)

## Instalação

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Como executar

```bash
python app.py
```

Acesse `http://localhost:8000`.

## Upload de dados

- Vá até a seção **Admin** no final do dashboard.
- Envie um arquivo `.xlsx`, `.xls` ou `.csv`.
- Clique em **Recarregar dados** para forçar a leitura do último arquivo salvo.
  - Senha padrão do painel admin: `123456`.

### Colunas obrigatórias

```
CODIGO_COLECAO
NOME_COLECAO
CODIGO_PRODUTO
REFERENCIA_PRODUTO
DESCRICAO_PRODUTO
CODIGO_PROCESSO
NOME_PROCESSO
ORDEM_PROCESSO
EMISSAO_PRODUCAO
VENCIMENTO_PRODUCAO
CONCLUSAO_PRODUCAO
STATUS_PRODUCAO
STATUS_VENCIMENTO
DIAS_PREVISAO
DIAS_CONCLUSAO
LOTE_PRODUCAO
QTDE_PRODUCAO
RESPONSAVEL
```

Colunas `Unnamed:*` são ignoradas.

## Configurações persistidas (SQLite)

- `weekly_target`
- `workdays`
- `daily_target_override`
- `selected_brands`
- `logo_path`
- `critical_delay_days`

O banco fica em `data/app.db`.

## Estrutura do projeto

```
app.py
requirements.txt
README.md
.gitignore
assets/
  styles.css
src/
  data_loader.py
  transforms.py
  kpis.py
  settings_store.py
  ui_layout.py
  pages/
    dashboard.py
    admin.py
    home.py
    processos.py
    produtos.py
    atrasos.py
    metas.py
data/
  uploads/
  app.db
```
