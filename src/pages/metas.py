from __future__ import annotations

from dash import dcc, html
import pandas as pd
import plotly.express as px

from src.kpis import compute_projection

def _week_bounds(today: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = today - pd.Timedelta(days=today.weekday())
    end = start + pd.Timedelta(days=6)
    return start.normalize(), end.normalize()


def render_metas(df: pd.DataFrame, settings: dict) -> html.Div:
    today = pd.Timestamp.today().normalize()
    week_start, week_end = _week_bounds(today)

    weekly_target = settings.get("weekly_target") or 0
    workdays = settings.get("workdays") or 5
    daily_override = settings.get("daily_target_override")

    daily_target = daily_override if daily_override is not None else (weekly_target / workdays if workdays else 0)

    concluded_today = 0
    concluded_week = 0

    if not df.empty:
        concluido = df[df["STATUS_PRODUCAO"].astype(str).str.upper() == "CONCLUIDO"]
        concluded_today = concluido[concluido["CONCLUSAO_PRODUCAO"].dt.normalize() == today]["QTDE_PRODUCAO"].sum()
        concluded_week = concluido[
            (concluido["CONCLUSAO_PRODUCAO"].dt.normalize() >= week_start)
            & (concluido["CONCLUSAO_PRODUCAO"].dt.normalize() <= week_end)
        ]["QTDE_PRODUCAO"].sum()

    projection = compute_projection(weekly_target, concluded_week, int(workdays), today)

    if not df.empty:
        week_data = df[
            (df["CONCLUSAO_PRODUCAO"].dt.normalize() >= week_start)
            & (df["CONCLUSAO_PRODUCAO"].dt.normalize() <= week_end)
        ]
        by_day = week_data.groupby(week_data["CONCLUSAO_PRODUCAO"].dt.day_name(), as_index=False)["QTDE_PRODUCAO"].sum()
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        by_day["day_order"] = by_day["CONCLUSAO_PRODUCAO"].apply(lambda x: order.index(x) if x in order else 99)
        by_day = by_day.sort_values("day_order")
        bar_fig = px.bar(by_day, x="CONCLUSAO_PRODUCAO", y="QTDE_PRODUCAO", title="Concluído por dia (semana atual)")
    else:
        bar_fig = px.bar(title="Concluído por dia (semana atual)")

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("Hoje", className="kpi-title"),
                            html.Div(f"{concluded_today:,} / {daily_target:,.0f}", className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Semana", className="kpi-title"),
                            html.Div(f"{concluded_week:,} / {weekly_target:,.0f}", className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Meta diária", className="kpi-title"),
                            html.Div(f"{daily_target:,.0f}", className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Projeção semanal", className="kpi-title"),
                            html.Div(f"{projection['projected_week']:,.0f}", className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                    html.Div(
                        [
                            html.Div("Ritmo diário", className="kpi-title"),
                            html.Div(f"{projection['pace_daily']:,.1f}", className="kpi-value"),
                        ],
                        className="kpi-card",
                    ),
                ],
                className="kpi-grid",
            ),
            dcc.Graph(figure=bar_fig, className="chart"),
        ],
        className="page",
    )
