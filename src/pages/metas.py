\
from __future__ import annotations
from dash import html, dcc
import plotly.express as px
import pandas as pd

def _iso_week(ts: pd.Timestamp) -> str:
    return ts.to_period("W").astype(str)

def layout(df: pd.DataFrame, meta: dict):
    weekly_target = float(meta.get("weekly_target") or 0)
    workdays = int(meta.get("workdays") or 5)
    daily_override = meta.get("daily_target_override")

    daily_target = None
    if daily_override is None:
        daily_target = weekly_target / workdays if workdays else 0
        daily_target_mode = "Automática"
    else:
        daily_target = float(daily_override or 0)
        daily_target_mode = "Manual"

    # progresso hoje/semana
    today = pd.Timestamp.today().normalize()
    week_key = today.to_period("W").astype(str)

    concl = df[df["STATUS_PRODUCAO"].astype(str).str.upper().eq("CONCLUIDO")]
    concl_today = 0
    concl_week = 0
    if "CONCLUSAO_PRODUCAO" in concl.columns:
        concl_today = int(concl[concl["CONCLUSAO_PRODUCAO"].dt.normalize().eq(today)]["QTDE_PRODUCAO"].sum())
        concl_week = int(concl[concl["CONCLUSAO_PRODUCAO"].dt.to_period("W").astype(str).eq(week_key)]["QTDE_PRODUCAO"].sum())

    # série da semana atual
    if "CONCLUSAO_PRODUCAO" in concl.columns:
        week_series = concl[concl["CONCLUSAO_PRODUCAO"].dt.to_period("W").astype(str).eq(week_key)].copy()
        week_series["DIA"] = week_series["CONCLUSAO_PRODUCAO"].dt.date
        by_day = week_series.groupby("DIA")["QTDE_PRODUCAO"].sum().reset_index()
    else:
        by_day = pd.DataFrame({"DIA": [], "QTDE_PRODUCAO": []})

    fig = px.bar(by_day, x="DIA", y="QTDE_PRODUCAO", title="Concluído por dia (semana atual)")

    return html.Div(
        [
            html.Div(
                [
                    html.Div("Metas", className="panel-title"),
                    html.Div(
                        [
                            html.Div([html.B("Meta semanal:"), f" {weekly_target:.0f} peças"]),
                            html.Div([html.B("Dias úteis:"), f" {workdays}"]),
                            html.Div([html.B("Meta diária:"), f" {daily_target:.1f} peças ({daily_target_mode})"]),
                            html.Div([html.B("Hoje:"), f" {concl_today} / {daily_target:.1f} peças"]),
                            html.Div([html.B("Semana:"), f" {concl_week} / {weekly_target:.0f} peças"]),
                        ],
                        className="row",
                        style={"gap":"18px", "marginTop":"8px"}
                    ),
                ],
                className="panel",
            ),
            html.Div([dcc.Graph(figure=fig)], className="panel"),
        ]
    )
