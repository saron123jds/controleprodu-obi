from __future__ import annotations
from dash import html, dcc
import plotly.express as px
import pandas as pd
from ..ui_layout import kpi_card
from ..kpis import kpi_totals

def layout(df: pd.DataFrame, meta: dict):
    k = kpi_totals(df)

    kpis = html.Div(
        [
            kpi_card("Peças (total)", f"{k['total']:,}".replace(",", ".")),
            kpi_card("Concluídas", f"{k['concluidas']:,}".replace(",", ".")),
            kpi_card("Em aberto", f"{k['aberto']:,}".replace(",", ".")),
            kpi_card("Itens atrasados", f"{k['atrasados_itens']:,}".replace(",", ".")),
            kpi_card("% no prazo", "-" if k["pct_prazo"] is None else f"{k['pct_prazo']:.1f}%"),
            kpi_card("Lead time médio", "-" if k["lead_medio"] is None else f"{k['lead_medio']:.1f} dias"),
        ],
        className="kpis",
    )

    # Time series: peças concluídas por dia
    if "CONCLUSAO_DIA" in df.columns:
        ts = (
            df[df["STATUS_PRODUCAO"].astype(str).str.upper().eq("CONCLUIDO")]
            .groupby("CONCLUSAO_DIA", dropna=True)["QTDE_PRODUCAO"].sum()
            .reset_index()
        )
    else:
        ts = pd.DataFrame({"CONCLUSAO_DIA": [], "QTDE_PRODUCAO": []})

    fig_ts = px.line(ts, x="CONCLUSAO_DIA", y="QTDE_PRODUCAO", markers=True, title="Peças concluídas por dia")

    # Processos
    proc = df.groupby("NOME_PROCESSO")["QTDE_PRODUCAO"].sum().reset_index().sort_values("QTDE_PRODUCAO", ascending=False).head(15)
    fig_proc = px.bar(proc, x="QTDE_PRODUCAO", y="NOME_PROCESSO", orientation="h", title="Peças por processo (Top 15)")

    # Status vencimento
    if "STATUS_VENCIMENTO" in df.columns:
        sv = df["STATUS_VENCIMENTO"].astype(str).fillna("SEM STATUS").str.upper()
        sv_df = sv.value_counts().reset_index()
        sv_df.columns = ["STATUS_VENCIMENTO", "QTD_ITENS"]
    else:
        sv_df = pd.DataFrame({"STATUS_VENCIMENTO": [], "QTD_ITENS": []})
    fig_sv = px.pie(sv_df, names="STATUS_VENCIMENTO", values="QTD_ITENS", title="Distribuição de vencimento")

    return html.Div(
        [
            kpis,
            html.Div(
                [
                    html.Div([dcc.Graph(figure=fig_ts)], className="panel"),
                    html.Div([dcc.Graph(figure=fig_sv)], className="panel"),
                ],
                className="grid2",
            ),
            html.Div([dcc.Graph(figure=fig_proc)], className="panel"),
        ]
    )
