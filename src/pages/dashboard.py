from __future__ import annotations

from dash import html
import pandas as pd

from . import home, processos, produtos, atrasos, metas


def _section(title: str, content):
    return html.Div(
        [
            html.Div(title, className="section-title"),
            content,
        ],
        className="section-block",
    )


def layout(df: pd.DataFrame, settings: dict):
    return html.Div(
        [
            _section("Visão geral", home.layout(df, settings)),
            _section("Processos", processos.layout(df, settings)),
            _section("Produtos", produtos.layout(df, settings)),
            _section("Atrasos críticos", atrasos.layout(df, settings)),
            _section("Metas", metas.layout(df, settings)),
        ]
    )
