from __future__ import annotations

from dash import dash_table, dcc, html
import pandas as pd
import plotly.express as px


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

    bucket_fig = (
        px.bar(
            df["ATRASO_FAIXA"].value_counts().rename_axis("Faixa").reset_index(name="Qtde"),
            x="Faixa",
            y="Qtde",
            title="Distribuição de atrasos por faixa",
        )
        if not df.empty
        else px.bar(title="Distribuição de atrasos por faixa")
    )

    top_atrasos = (
        df.sort_values("ATRASO_DIAS", ascending=False)
        .head(10)[COLUMNS]
        if not df.empty
        else pd.DataFrame(columns=COLUMNS)
    )

    top_table = dash_table.DataTable(
        columns=[{"name": col.replace("_", " "), "id": col} for col in COLUMNS],
        data=top_atrasos.to_dict("records") if not top_atrasos.empty else [],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"backgroundColor": "#0f172a", "color": "#e2e8f0", "padding": "6px"},
        style_header={"backgroundColor": "#1e293b", "fontWeight": "bold"},
    )

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
            dcc.Graph(figure=bucket_fig, className="chart"),
            html.Div(
                [
                    html.H4("Top 10 atrasos"),
                    top_table,
                ],
                className="card",
            ),
            table,
        ],
        className="page",
    )
