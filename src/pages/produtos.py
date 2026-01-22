\
from __future__ import annotations
from dash import html, dcc
import plotly.express as px
import pandas as pd

def layout(df: pd.DataFrame, meta: dict):
    top = (
        df.groupby(["REFERENCIA_PRODUTO","DESCRICAO_PRODUTO"])["QTDE_PRODUCAO"]
        .sum().reset_index().sort_values("QTDE_PRODUCAO", ascending=False).head(20)
    )
    fig = px.bar(top, x="QTDE_PRODUCAO", y="REFERENCIA_PRODUTO", orientation="h", title="Top 20 referências por volume")

    if "DIAS_CONCLUSAO" in df.columns:
        lt = df.copy()
        lt["DIAS_CONCLUSAO"] = pd.to_numeric(lt["DIAS_CONCLUSAO"], errors="coerce")
        lt = lt.dropna(subset=["DIAS_CONCLUSAO"])
        top_lt = (
            lt.groupby(["REFERENCIA_PRODUTO","DESCRICAO_PRODUTO"])["DIAS_CONCLUSAO"]
            .mean().reset_index().sort_values("DIAS_CONCLUSAO", ascending=False).head(20)
        )
        fig2 = px.bar(top_lt, x="DIAS_CONCLUSAO", y="REFERENCIA_PRODUTO", orientation="h", title="Top 20 referências por lead time médio (dias)")
    else:
        fig2 = px.bar(pd.DataFrame({"DIAS_CONCLUSAO":[],"REFERENCIA_PRODUTO":[]}), x="DIAS_CONCLUSAO", y="REFERENCIA_PRODUTO", orientation="h")

    return html.Div(
        [
            html.Div([dcc.Graph(figure=fig)], className="panel"),
            html.Div([dcc.Graph(figure=fig2)], className="panel"),
        ]
    )
