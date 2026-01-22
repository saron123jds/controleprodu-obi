from __future__ import annotations

from dash import dash_table, html
import pandas as pd


COLUMNS = [
    "MARCA",
    "NOME_COLECAO",
    "REFERENCIA_PRODUTO",
    "NOME_PROCESSO",
    "LOTE_PRODUCAO",
    "QTDE_PRODUCAO",
    "VENCIMENTO_PRODUCAO",
    "ATRASO_DIAS",
    "RESPONSAVEL",
]


def render_atrasos(df: pd.DataFrame, critical_delay_days: int) -> html.Div:
    if df.empty:
        filtered = df
    else:
        filtered = df[df["ATRASO_DIAS"] >= critical_delay_days]

    table = dash_table.DataTable(
        columns=[{"name": col.replace("_", " "), "id": col} for col in COLUMNS],
        data=filtered[COLUMNS].to_dict("records") if not filtered.empty else [],
        filter_action="native",
        sort_action="native",
        page_size=20,
        style_table={"overflowX": "auto"},
        style_cell={"backgroundColor": "#0f172a", "color": "#e2e8f0", "padding": "6px"},
        style_header={"backgroundColor": "#1e293b", "fontWeight": "bold"},
    )

    return html.Div(
        [
            html.H3("Atrasos Críticos"),
            html.P(f"Exibindo apenas atrasos >= {critical_delay_days} dias"),
            table,
        ],
        className="page",
    )
