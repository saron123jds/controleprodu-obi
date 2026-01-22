# Dashboard PCP (PowerBI-like) — localhost:8000

Este projeto cria um dashboard web no estilo Power BI para acompanhar produção (PCP), com:
- Upload de Excel/CSV
- Filtros por marca/coleção/processo/status/período
- KPIs, gráficos e tabelas
- Página de Configurações: metas (semanal -> diária), seleção de marcas e upload de logo
- Persistência das configurações em SQLite

## Recursos do sistema
### 1) Rodar local (localhost:8000)
- Roda no seu PC em: http://localhost:8000
- Sem precisar internet
- Pode abrir de outros dispositivos na mesma rede pelo IP (ex.: http://192.168.x.x:8000)

### 2) Upload do arquivo Excel/CSV (troca quando quiser)
Na página **Configurações** você pode:
- Fazer upload de Excel (.xlsx/.xls) ou CSV (.csv)
- Substituir o arquivo sempre que tiver um novo
- Clicar em **Recarregar dados** para atualizar o painel

📌 O sistema salva o último arquivo enviado e volta com ele na próxima vez.

### 3) Validação automática do arquivo
Quando você envia o arquivo, ele:
- Verifica se existem as colunas obrigatórias
- Converte campos numéricos (QTDE_PRODUCAO, etc.)
- Converte datas (EMISSAO, VENCIMENTO, CONCLUSAO)
- Ignora colunas vazias tipo `Unnamed: ...`
- Se faltar algo, mostra mensagem dizendo quais colunas estão faltando

### 4) Identificação automática de Marca
Mesmo se sua planilha não tiver **MARCA**:
- Ele cria a coluna MARCA automaticamente olhando `NOME_COLECAO`
- Reconhece: DAZUL, SARON, FILOBLU
- Se não achar, entra como **OUTRAS**

### 5) Filtros estilo Power BI (topo do painel)
Você tem filtros globais para:
- Marca(s)
- Coleção(ões)
- Processo(s)
- Status Produção
- Status Vencimento

Esses filtros afetam todas as páginas.

### 6) KPIs (Cards no topo da Visão Geral)
Na página **Visão geral** ele mostra:
- Peças (total)
- Concluídas
- Em aberto
- Itens atrasados
- % no prazo
- Lead time médio (dias)

### 7) Gráficos principais (Power BI style)
**Visão Geral**
- Linha: peças concluídas por dia
- Barras: peças por processo (Top 15)
- Pizza: distribuição de vencimento (no prazo x em atraso etc.)

**Processos**
- Barras: volume por processo ordenado por etapa (ORDEM_PROCESSO)
- Barras: atraso médio por processo (Top 15 gargalos)

**Produtos**
- Top 20 referências por volume
- Top 20 referências por lead time médio

### 8) Página “Atrasos” com tabela inteligente
Mostra somente atrasos críticos (configurável em **Configurações**).

Tabela com:
- marca, coleção, referência, processo, lote, qty, vencimento, atraso, responsável

A tabela permite:
- ordenar
- filtrar
- pesquisar
- paginação

### 9) Sistema de Metas (Meta semanal → Meta diária automática)
Na página **Metas** ele entrega:
- Meta semanal (configurável)
- Dias úteis (configurável)
- Meta diária automática = meta_semanal / dias_úteis

Você pode colocar uma meta diária manual e ele respeita.

Mostra:
- Concluído hoje vs meta diária
- Concluído na semana vs meta semanal
- Gráfico: concluído por dia na semana atual

### 10) Configurações completas
Na página **Configurações** você tem:

**A) Fonte de dados**
- Upload arquivo
- Botão recarregar

**B) Marcas exibidas**
- Seleciona 1 ou várias marcas para aparecer no painel
- Isso vira o “padrão” do dashboard

**C) Metas**
- Meta semanal
- Dias úteis
- Meta diária manual (opcional)
- Exibição da meta diária automática calculada

**D) Logo**
- Upload da logo (PNG/JPG)
- Ela aparece na sidebar do dashboard

**E) Regra de atraso crítico**
- Define quantos dias para considerar “crítico”

### 11) Persistência (salva tudo)
O sistema salva automaticamente (SQLite):
- metas
- marcas selecionadas
- regra de atraso crítico
- logo enviada

Fechou e abriu de novo, tudo continua igual.

### 12) Estrutura profissional pronta para Git
- `requirements.txt`
- separação em módulos (`src/`)
- páginas (`home/processos/produtos/atrasos/metas/config`)
- pronto para subir no GitHub e clonar em outro PC

### ⚡ Recursos que posso adicionar (se quiser)
- filtro de período (por emissão / vencimento / conclusão)
- ranking por responsável
- produtividade por dia/semana/mês
- comparativo Dazul x Saron
- metas por marca / por coleção
- alertas visuais (verde/amarelo/vermelho)
- exportação de tabelas para Excel
- botão “Atualizar automático” (watch de arquivo)

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
