from __future__ import annotations

from dash import dash_table, dcc, html
import pandas as pd
import plotly.express as px

from src.kpis import compute_kpis, compute_kpis_by
from src.transforms import compute_completion_trends


def _kpi_card(title: str, value: str) -> html.Div:
    return html.Div(
        [
            html.Div(title, className="kpi-title"),
            html.Div(value, className="kpi-value"),
        ],
        className="kpi-card",
    )


def render_home(df: pd.DataFrame, data_quality_alerts: list[str]) -> html.Div:
    kpis = compute_kpis(df)
    trends = compute_completion_trends(df)

    line_fig = px.line(
        df,
        x="CONCLUSAO_DIA",
        y="QTDE_PRODUCAO",
        title="Peças concluídas por dia",
        markers=True,
    ) if not df.empty else px.line(title="Peças concluídas por dia")

    weekly_fig = (
        px.line(
            trends["weekly"],
            x="PERIODO",
            y="QTDE_PRODUCAO",
            title="Peças concluídas por semana",
            markers=True,
        )
        if not trends["weekly"].empty
        else px.line(title="Peças concluídas por semana")
    )
    monthly_fig = (
        px.line(
            trends["monthly"],
            x="PERIODO",
            y="QTDE_PRODUCAO",
            title="Peças concluídas por mês",
            markers=True,
        )
        if not trends["monthly"].empty
        else px.line(title="Peças concluídas por mês")
    )

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

    by_process = compute_kpis_by(df, "NOME_PROCESSO")
    by_responsavel = compute_kpis_by(df, "RESPONSAVEL")

    table_process = dash_table.DataTable(
        columns=[{"name": col.replace("_", " ").title(), "id": col} for col in by_process.columns],
        data=by_process.sort_values("pecas", ascending=False).head(10).to_dict("records") if not by_process.empty else [],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"backgroundColor": "#0f172a", "color": "#e2e8f0", "padding": "6px"},
        style_header={"backgroundColor": "#1e293b", "fontWeight": "bold"},
    )

    table_resp = dash_table.DataTable(
        columns=[{"name": col.replace("_", " ").title(), "id": col} for col in by_responsavel.columns],
        data=by_responsavel.sort_values("pecas", ascending=False).head(10).to_dict("records") if not by_responsavel.empty else [],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"backgroundColor": "#0f172a", "color": "#e2e8f0", "padding": "6px"},
        style_header={"backgroundColor": "#1e293b", "fontWeight": "bold"},
    )

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
                    html.H4("Alertas de qualidade de dados"),
                    html.Ul([html.Li(alert) for alert in data_quality_alerts])
                    if data_quality_alerts
                    else html.Div("Nenhum alerta identificado.", className="muted"),
                ],
                className="card",
            ),
            html.Div(
                [
                    dcc.Graph(figure=line_fig, className="chart"),
                    dcc.Graph(figure=weekly_fig, className="chart"),
                    dcc.Graph(figure=monthly_fig, className="chart"),
                    dcc.Graph(figure=process_fig, className="chart"),
                    dcc.Graph(figure=status_fig, className="chart"),
                ],
                className="chart-grid",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.H4("KPIs por processo (Top 10)"),
                            table_process,
                        ],
                        className="card",
                    ),
                    html.Div(
                        [
                            html.H4("KPIs por responsável (Top 10)"),
                            table_resp,
                        ],
                        className="card",
                    ),
                ],
                className="chart-grid",
            ),
        ],
        className="page",
    )
