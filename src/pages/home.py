from __future__ import annotations

from dash import dcc, html
import pandas as pd
import plotly.express as px

from src.kpis import compute_kpis


def _kpi_card(title: str, value: str) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="kpi-title"),
            html.Div(value, className="kpi-value"),
        ],
        className="kpi-card",
    )


def render_home(df: pd.DataFrame) -> html.Div:
    kpis = compute_kpis(df)

    line_fig = px.line(
        df,
        x="CONCLUSAO_DIA",
        y="QTDE_PRODUCAO",
        title="Peças concluídas por dia",
        markers=True,
    ) if not df.empty else px.line(title="Peças concluídas por dia")

    process_fig = px.bar(
        df.groupby("NOME_PROCESSO", as_index=False)["QTDE_PRODUCAO"].sum()
        .sort_values("QTDE_PRODUCAO", ascending=False)
        .head(15),
        x="NOME_PROCESSO",
        y="QTDE_PRODUCAO",
        title="Peças por processo (Top 15)",
    ) if not df.empty else px.bar(title="Peças por processo (Top 15)")

    status_fig = px.pie(
        df,
        names="STATUS_VENCIMENTO",
        values="QTDE_PRODUCAO",
        title="Distribuição Status Vencimento",
    ) if not df.empty else px.pie(title="Distribuição Status Vencimento")

    return html.Div(
        [
            html.Div(
                [
                    _kpi_card("Peças", f"{kpis['pecas']:,}"),
                    _kpi_card("Concluídas", f"{kpis['concluidas']:,}"),
                    _kpi_card("Em aberto", f"{kpis['em_aberto']:,}"),
                    _kpi_card("Itens atrasados", f"{kpis['atrasados']:,}"),
                    _kpi_card("% no prazo", f"{kpis['percentual_no_prazo']:.0%}"),
                    _kpi_card("Lead time médio", f"{kpis['lead_time_medio']:.1f} dias"),
                ],
                className="kpi-grid",
            ),
            html.Div(
                [
                    dcc.Graph(figure=line_fig, className="chart"),
                    dcc.Graph(figure=process_fig, className="chart"),
                    dcc.Graph(figure=status_fig, className="chart"),
                ],
                className="chart-grid",
            ),
        ],
        className="page",
    )
