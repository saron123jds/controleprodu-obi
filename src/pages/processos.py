from __future__ import annotations

from dash import dcc, html
import pandas as pd
import plotly.express as px


def render_processos(df: pd.DataFrame) -> html.Div:
    if df.empty:
        volume_fig = px.bar(title="Volume por processo")
        atraso_fig = px.bar(title="Atraso médio por processo")
    else:
        ordered = df.sort_values("ORDEM_PROCESSO")
        volume = (
            ordered.groupby(["ORDEM_PROCESSO", "NOME_PROCESSO"], as_index=False)["QTDE_PRODUCAO"]
            .sum()
            .sort_values("ORDEM_PROCESSO")
        )
        volume_fig = px.bar(
            volume,
            x="NOME_PROCESSO",
            y="QTDE_PRODUCAO",
            title="Volume por processo",
        )

        atraso = (
            df.groupby("NOME_PROCESSO", as_index=False)["ATRASO_DIAS"]
            .mean()
            .sort_values("ATRASO_DIAS", ascending=False)
            .head(15)
        )
        atraso_fig = px.bar(
            atraso,
            x="NOME_PROCESSO",
            y="ATRASO_DIAS",
            title="Atraso médio por processo (Top 15)",
        )

    return html.Div(
        [
            dcc.Graph(figure=volume_fig, className="chart"),
            dcc.Graph(figure=atraso_fig, className="chart"),
        ],
        className="page",
    )
