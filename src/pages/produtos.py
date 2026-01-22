from __future__ import annotations

from dash import dcc, html
import pandas as pd
import plotly.express as px


def render_produtos(df: pd.DataFrame) -> html.Div:
    if df.empty:
        volume_fig = px.bar(title="Top 20 referências por volume")
        lead_fig = px.bar(title="Top 20 referências por lead time médio")
    else:
        volume = (
            df.groupby("REFERENCIA_PRODUTO", as_index=False)["QTDE_PRODUCAO"]
            .sum()
            .sort_values("QTDE_PRODUCAO", ascending=False)
            .head(20)
        )
        volume_fig = px.bar(
            volume,
            x="REFERENCIA_PRODUTO",
            y="QTDE_PRODUCAO",
            title="Top 20 referências por volume",
        )

        lead = (
            df.groupby("REFERENCIA_PRODUTO", as_index=False)["DIAS_CONCLUSAO"]
            .mean()
            .sort_values("DIAS_CONCLUSAO", ascending=False)
            .head(20)
        )
        lead_fig = px.bar(
            lead,
            x="REFERENCIA_PRODUTO",
            y="DIAS_CONCLUSAO",
            title="Top 20 referências por lead time médio",
        )

    return html.Div(
        [
            dcc.Graph(figure=volume_fig, className="chart"),
            dcc.Graph(figure=lead_fig, className="chart"),
        ],
        className="page",
    )
