\
from __future__ import annotations
from dash import html, dcc
import plotly.express as px
import pandas as pd

def layout(df: pd.DataFrame, meta: dict):
    g = df.groupby(["ORDEM_PROCESSO","NOME_PROCESSO"])["QTDE_PRODUCAO"].sum().reset_index()
    g = g.sort_values(["ORDEM_PROCESSO","QTDE_PRODUCAO"], ascending=[True, False])
    fig = px.bar(g, x="QTDE_PRODUCAO", y="NOME_PROCESSO", orientation="h", title="Volume por processo (ordenado por etapa)")

    # gargalos: maior atraso médio
    if "ATRASO_DIAS" in df.columns:
        a = df.groupby("NOME_PROCESSO")["ATRASO_DIAS"].mean().reset_index().sort_values("ATRASO_DIAS", ascending=False).head(15)
        fig2 = px.bar(a, x="ATRASO_DIAS", y="NOME_PROCESSO", orientation="h", title="Atraso médio (dias) por processo (Top 15)")
    else:
        fig2 = px.bar(pd.DataFrame({"ATRASO_DIAS":[],"NOME_PROCESSO":[]}), x="ATRASO_DIAS", y="NOME_PROCESSO", orientation="h")

    return html.Div(
        [
            html.Div([dcc.Graph(figure=fig)], className="panel"),
            html.Div([dcc.Graph(figure=fig2)], className="panel"),
        ]
    )
