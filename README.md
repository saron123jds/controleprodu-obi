# Dashboard PCP (PowerBI-like) — localhost:8000

Este projeto cria um dashboard web no estilo Power BI para acompanhar produção (PCP), com:
- Upload de Excel/CSV
- Filtros por marca/coleção/processo/status/período
- KPIs, gráficos e tabelas
- Página de Configurações: metas (semanal -> diária), seleção de marcas e upload de logo
- Persistência das configurações em SQLite

## Como rodar (Windows)

1) Abra o CMD na pasta do projeto:
```bat
cd C:\CAMINHO\dashboard_pcp
```

2) Crie e ative um ambiente virtual (recomendado):
```bat
python -m venv .venv
.venv\Scripts\activate
```

3) Instale dependências:
```bat
pip install -r requirements.txt
```

4) Rode:
```bat
python app.py
```

5) Acesse:
- http://localhost:8000

## Usando seus dados
- Vá em **Configurações** > **Upload do arquivo**
- Envie um Excel (.xlsx) ou CSV (.csv)
- Clique em **Recarregar dados**
- O dashboard atualiza automaticamente

## Observações
- A marca é detectada automaticamente a partir de `NOME_COLECAO` (ex.: contém "DAZUL", "SARON", "FILOBLU").
- Você pode selecionar as marcas exibidas em **Configurações**.
- Meta semanal gera meta diária automaticamente, mas você pode sobrescrever.

